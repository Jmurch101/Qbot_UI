"""Owns the confirmed address and the four probe servers."""

from __future__ import annotations

from PySide6.QtCore import QObject

from qbotui.bind_policy import BindPolicy, BindRejected
from qbotui.contract import ProbeContract
from qbotui.probe_server import ProbeServer


class Viewer(QObject):
    """Start and stop the four PC listeners. No camera device and no second address."""

    def __init__(self, policy: BindPolicy, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._policy = policy
        self._active = False
        self._servers = tuple(
            ProbeServer(stream, policy, parent=self) for stream in ProbeContract.STREAMS
        )

    @property
    def servers(self) -> tuple[ProbeServer, ...]:
        return self._servers

    @property
    def confirmed_address(self) -> str | None:
        return self._policy.confirmed_address

    @property
    def listeners_active(self) -> bool:
        return self._active

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
        for server in self._servers:
            try:
                server.start(host)
            except BindRejected:
                server.mark_bind_failure()

    def stop(self) -> None:
        for server in self._servers:
            server.request_stop()
        for server in self._servers:
            server.join(3.0)
        for server in self._servers:
            server.mark_stopped()
        self._active = False
