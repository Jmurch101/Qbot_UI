"""IPv4 enumeration. This class never selects an address."""

from __future__ import annotations

import ipaddress
import sys
from ctypes import (
    POINTER,
    Structure,
    byref,
    c_ubyte,
    c_uint,
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


class InterfaceDirectory:
    """Walk GetAdaptersAddresses and return (friendly_name, ipv4) rows."""

    AF_INET = 2
    GAA_FLAG_SKIP_ANYCAST = 0x0002
    GAA_FLAG_SKIP_MULTICAST = 0x0004
    GAA_FLAG_SKIP_DNS_SERVER = 0x0008
    FLAGS = GAA_FLAG_SKIP_ANYCAST | GAA_FLAG_SKIP_MULTICAST | GAA_FLAG_SKIP_DNS_SERVER
    ERROR_SUCCESS = 0
    ERROR_BUFFER_OVERFLOW = 111

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
        for friendly_name, ipv4, oper_status in self._read_adapters():
            if self.keep_address(ipv4, oper_status):
                rows.append((friendly_name, ipv4))
        return rows

    def _read_adapters(self) -> list[tuple[str, str, int]]:
        if sys.platform != "win32" or WinDLL is None:
            return []
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
