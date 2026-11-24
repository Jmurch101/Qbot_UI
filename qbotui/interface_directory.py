"""IPv4 enumeration. This class never selects an address."""

from __future__ import annotations

import ipaddress
import socket
import struct
import sys
from ctypes import (
    CDLL,
    POINTER,
    Structure,
    byref,
    c_char_p,
    c_int,
    c_ubyte,
    c_uint,
    c_uint8,
    c_uint16,
    c_uint32,
    c_ulong,
    c_ushort,
    c_void_p,
    c_wchar_p,
    cast,
    create_string_buffer,
)

if sys.platform == "win32":
    from ctypes import WinDLL
else:
    WinDLL = None  # type: ignore[misc, assignment]


class UnicastAddressFilter:
    """Drop loopback, APIPA, and adapters that are not up."""

    LOOPBACK = ipaddress.IPv4Network("127.0.0.0/8")
    APIPA = ipaddress.IPv4Network("169.254.0.0/16")
    UP = 1

    def keep(self, ipv4: str, oper_status: int) -> bool:
        if oper_status != self.UP:
            return False
        try:
            address = ipaddress.IPv4Address(ipv4)
        except ipaddress.AddressValueError:
            return False
        if address in self.LOOPBACK or address in self.APIPA:
            return False
        return True


class _SockAddr(Structure):
    _fields_ = (
        ("sa_family", c_ushort),
        ("sa_data", c_ubyte * 14),
    )


class _SocketAddress(Structure):
    _fields_ = (
        ("lpSockaddr", POINTER(_SockAddr)),
        ("iSockaddrLength", c_uint),
    )


class _IpAdapterUnicastAddress(Structure):
    pass


_IpAdapterUnicastAddress._fields_ = (
    ("Length", c_ulong),
    ("Flags", c_ulong),
    ("Next", POINTER(_IpAdapterUnicastAddress)),
    ("Address", _SocketAddress),
    ("PrefixOrigin", c_uint),
    ("SuffixOrigin", c_uint),
    ("DadState", c_uint),
    ("ValidLifetime", c_ulong),
    ("PreferredLifetime", c_ulong),
    ("LeaseLifetime", c_ulong),
    ("OnLinkPrefixLength", c_ubyte),
)


class _IpAdapterAddresses(Structure):
    pass


_IpAdapterAddresses._fields_ = (
    ("Length", c_ulong),
    ("IfIndex", c_ulong),
    ("Next", POINTER(_IpAdapterAddresses)),
    ("AdapterName", c_void_p),
    ("FirstUnicastAddress", POINTER(_IpAdapterUnicastAddress)),
    ("FirstAnycastAddress", c_void_p),
    ("FirstMulticastAddress", c_void_p),
    ("FirstDnsServerAddress", c_void_p),
    ("DnsSuffix", c_wchar_p),
    ("Description", c_wchar_p),
    ("FriendlyName", c_wchar_p),
    ("PhysicalAddress", c_ubyte * 8),
    ("PhysicalAddressLength", c_ulong),
    ("Flags", c_ulong),
    ("Mtu", c_ulong),
    ("IfType", c_ulong),
    ("OperStatus", c_uint),
)


class _DarwinSockAddrIn(Structure):
    _fields_ = (
        ("sin_len", c_uint8),
        ("sin_family", c_uint8),
        ("sin_port", c_uint16),
        ("sin_addr", c_uint32),
        ("sin_zero", c_ubyte * 8),
    )


class _LinuxSockAddrIn(Structure):
    _fields_ = (
        ("sin_family", c_uint16),
        ("sin_port", c_uint16),
        ("sin_addr", c_uint32),
        ("sin_zero", c_ubyte * 8),
    )


class _PosixIfAddrs(Structure):
    pass


_PosixIfAddrs._fields_ = (
    ("ifa_next", POINTER(_PosixIfAddrs)),
    ("ifa_name", c_char_p),
    ("ifa_flags", c_uint),
    ("ifa_addr", c_void_p),
    ("ifa_netmask", c_void_p),
    ("ifa_ifu", c_void_p),
    ("ifa_data", c_void_p),
)


class InterfaceDirectory:
    """Walk OS adapters and return (friendly_name, ipv4) rows."""

    AF_INET = 2
    GAA_FLAG_SKIP_ANYCAST = 0x0002
    GAA_FLAG_SKIP_MULTICAST = 0x0004
    GAA_FLAG_SKIP_DNS_SERVER = 0x0008
    FLAGS = GAA_FLAG_SKIP_ANYCAST | GAA_FLAG_SKIP_MULTICAST | GAA_FLAG_SKIP_DNS_SERVER
    ERROR_SUCCESS = 0
    ERROR_BUFFER_OVERFLOW = 111
    IFF_UP = 0x1

    def __init__(self, address_filter: UnicastAddressFilter | None = None) -> None:
        self._filter = address_filter if address_filter is not None else UnicastAddressFilter()

    def keep_address(self, ipv4: str, oper_status: int) -> bool:
        return self._filter.keep(ipv4, oper_status)

    def ipv4_from_sa_data(self, sa_data: bytes) -> str:
        data = bytes(sa_data)
        octets = data[2:6]
        if len(octets) != 4:
            raise ValueError("sa_data does not contain an IPv4 address")
        return ".".join(str(octet) for octet in octets)

    def list_addresses(self) -> list[tuple[str, str]]:
        rows: list[tuple[str, str]] = []
        seen: set[str] = set()
        for friendly_name, ipv4, oper_status in self._read_adapters():
            if ipv4 in seen:
                continue
            if self.keep_address(ipv4, oper_status):
                seen.add(ipv4)
                rows.append((friendly_name, ipv4))
        return rows

    def _read_adapters(self) -> list[tuple[str, str, int]]:
        if sys.platform == "win32" and WinDLL is not None:
            return self._read_adapters_windows()
        return self._read_adapters_posix()

    def _read_adapters_windows(self) -> list[tuple[str, str, int]]:
        assert WinDLL is not None
        iphlpapi = WinDLL("iphlpapi")
        get_adapters = iphlpapi.GetAdaptersAddresses
        get_adapters.argtypes = [
            c_ulong,
            c_ulong,
            c_void_p,
            c_void_p,
            POINTER(c_ulong),
        ]
        get_adapters.restype = c_ulong

        size = c_ulong(0)
        overflow = get_adapters(
            self.AF_INET,
            self.FLAGS,
            None,
            None,
            byref(size),
        )
        if overflow not in (self.ERROR_BUFFER_OVERFLOW, self.ERROR_SUCCESS):
            raise OSError(int(overflow), "GetAdaptersAddresses size query failed")
        if size.value == 0:
            return []

        buffer = create_string_buffer(size.value)
        result = get_adapters(
            self.AF_INET,
            self.FLAGS,
            None,
            cast(buffer, c_void_p),
            byref(size),
        )
        if result == self.ERROR_BUFFER_OVERFLOW:
            buffer = create_string_buffer(size.value)
            result = get_adapters(
                self.AF_INET,
                self.FLAGS,
                None,
                cast(buffer, c_void_p),
                byref(size),
            )
        if result != self.ERROR_SUCCESS:
            raise OSError(int(result), "GetAdaptersAddresses failed")

        rows: list[tuple[str, str, int]] = []
        adapter = cast(buffer, POINTER(_IpAdapterAddresses))
        for _adapter_index in range(128):
            if not adapter:
                break
            item = adapter.contents
            friendly_name = item.FriendlyName or ""
            oper_status = int(item.OperStatus)
            unicast = item.FirstUnicastAddress
            for _address_index in range(64):
                if not unicast:
                    break
                record = unicast.contents
                ipv4 = self._ipv4_from_unicast(record)
                if ipv4 is not None:
                    rows.append((friendly_name, ipv4, oper_status))
                unicast = record.Next
            adapter = item.Next
        return rows

    def _ipv4_from_unicast(self, record: _IpAdapterUnicastAddress) -> str | None:
        sockaddr_pointer = record.Address.lpSockaddr
        if not sockaddr_pointer:
            return None
        sockaddr = sockaddr_pointer.contents
        if int(sockaddr.sa_family) != self.AF_INET:
            return None
        return self.ipv4_from_sa_data(bytes(sockaddr.sa_data))

    def _read_adapters_posix(self) -> list[tuple[str, str, int]]:
        lib_name = "libc.dylib" if sys.platform == "darwin" else "libc.so.6"
        try:
            libc = CDLL(lib_name)
        except OSError as exc:
            raise OSError(f"Unable to load {lib_name} for interface enumeration") from exc

        getifaddrs = libc.getifaddrs
        getifaddrs.argtypes = [POINTER(POINTER(_PosixIfAddrs))]
        getifaddrs.restype = c_int
        freeifaddrs = libc.freeifaddrs
        freeifaddrs.argtypes = [POINTER(_PosixIfAddrs)]
        freeifaddrs.restype = None

        head = POINTER(_PosixIfAddrs)()
        if getifaddrs(byref(head)) != 0:
            raise OSError("getifaddrs failed")

        rows: list[tuple[str, str, int]] = []
        try:
            node = head
            for _ in range(256):
                if not node:
                    break
                item = node.contents
                name = (item.ifa_name or b"").decode("utf-8", errors="replace")
                flags = int(item.ifa_flags)
                oper_status = UnicastAddressFilter.UP if (flags & self.IFF_UP) else 2
                ipv4 = self._ipv4_from_posix_addr(item.ifa_addr)
                if ipv4 is not None:
                    rows.append((name, ipv4, oper_status))
                node = item.ifa_next
        finally:
            freeifaddrs(head)
        return rows

    def _ipv4_from_posix_addr(self, addr: c_void_p) -> str | None:
        if not addr:
            return None
        if sys.platform == "darwin":
            sockaddr = cast(addr, POINTER(_DarwinSockAddrIn)).contents
            family = int(sockaddr.sin_family)
            addr_value = sockaddr.sin_addr
        else:
            sockaddr = cast(addr, POINTER(_LinuxSockAddrIn)).contents
            family = int(sockaddr.sin_family)
            addr_value = sockaddr.sin_addr
        if family != socket.AF_INET:
            return None
        packed = struct.pack("=I", addr_value)
        return socket.inet_ntoa(packed)
