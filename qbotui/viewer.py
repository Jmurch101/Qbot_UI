"""Owns the confirmed address and the probe servers for the active observer."""

from __future__ import annotations

from PySide6.QtCore import QObject

from qbotui.bind_policy import BindPolicy, BindRejected
from qbotui.contract import ProbeContract, ProbeStream
from qbotui.probe_server import ProbeServer


class Viewer(QObject):
    """Start and stop PC listeners for the selected streams. No camera device."""

    def __init__(self, policy: BindPolicy, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._policy = policy
        self._active = False
        self._active_labels: frozenset[str] = frozenset(
            stream.label for stream in ProbeContract.STREAMS
        )
        self._servers = {
            stream.label: ProbeServer(stream, policy, parent=self)
            for stream in ProbeContract.STREAMS
        }

    @property
    def servers(self) -> tuple[ProbeServer, ...]:
        return tuple(self._servers[stream.label] for stream in ProbeContract.STREAMS)

    def server_for(self, label: str) -> ProbeServer:
        return self._servers[label]

    @property
    def confirmed_address(self) -> str | None:
        return self._policy.confirmed_address

    @property
    def listeners_active(self) -> bool:
        return self._active

    @property
    def active_labels(self) -> frozenset[str]:
        return self._active_labels

    def set_streams(self, streams: tuple[ProbeStream, ...]) -> None:
        if self._active:
            raise BindRejected("Changing observer streams is allowed only while servers are stopped")
        if not streams:
            raise BindRejected("Observer must expose at least one stream")
        self._active_labels = frozenset(stream.label for stream in streams)

    def confirm_address(self, host: str) -> str:
        if self._active:
            raise BindRejected("Changing address is allowed only while servers are stopped")
        candidate = self._policy.validated_host(host)
        current = self._policy.confirmed_address
        if current is not None and current != candidate:
            self._policy.release()
        return self._policy.confirm(candidate)

    def start(self) -> None:
        if self._active:
            return
        host = self._policy.confirmed_address
        if host is None:
            raise BindRejected("Confirm one IPv4 before starting listeners")
        self._active = True
        for label, server in self._servers.items():
            if label not in self._active_labels:
                server.mark_stopped()
                continue
            try:
                server.start(host)
            except BindRejected:
                server.mark_bind_failure()

    def stop(self) -> None:
        for server in self._servers.values():
            server.request_stop()
        for server in self._servers.values():
            server.join(3.0)
        for server in self._servers.values():
            server.mark_stopped()
        self._active = False
