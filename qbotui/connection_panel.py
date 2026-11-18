"""Control-center connection cards: network, task, devices, platform actions."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QBoxLayout,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from qbotui.address_chooser import AddressChooser
from qbotui.responsive import stack_controls
from qbotui.ssh_launcher import SshTarget
from qbotui.tasks import TaskCatalog, TaskProfile


def _card(title: str) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 14, 14, 14)
    layout.setSpacing(10)
    heading = QLabel(title)
    heading.setObjectName("sectionTitle")
    layout.addWidget(heading)
    return frame, layout


class ConnectionPanel(QWidget):
    """Network, task, device, and platform controls styled like the Phase A mock."""

    refresh_requested = Signal()
    confirm_requested = Signal()
    execute_requested = Signal()
    start_requested = Signal()
    disconnect_requested = Signal()
    task_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("connectionPanel")
        self._listening = False

        self._system_ready = QLabel("SYSTEM READY")
        self._system_ready.setObjectName("systemReadyPill")
        self._network_status = QLabel("NETWORK: DISCONNECTED")
        self._network_status.setObjectName("networkStatusLabel")

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        app_title = QLabel("QBOT PLATFORM")
        app_title.setObjectName("appTitle")
        app_sub = QLabel("PHASE A · CONTROL CENTER")
        app_sub.setObjectName("appSubtitle")
        title_col.addWidget(app_title)
        title_col.addWidget(app_sub)

        header_right = QHBoxLayout()
        header_right.addWidget(self._system_ready)
        header_right.addSpacing(12)
        header_right.addWidget(self._network_status)

        self.header = QWidget()
        header = QHBoxLayout(self.header)
        header.setContentsMargins(0, 0, 0, 0)
        header.addLayout(title_col, 1)
        header.addLayout(header_right)

        self.network_card, network_layout = _card("NETWORK CONFIGURATION")
        self._addresses = AddressChooser()
        self._addresses.setObjectName("addressList")
        self._refresh = QPushButton("Refresh")
        self._refresh.setObjectName("refreshAddressesButton")
        self._refresh.clicked.connect(self.refresh_requested.emit)
        self._confirm = QPushButton("CONFIRM")
        self._confirm.setObjectName("confirmAddressButton")
        self._confirm.clicked.connect(self.confirm_requested.emit)
        address_row = QHBoxLayout()
        address_row.addWidget(self._addresses, 1)
        address_row.addWidget(self._refresh)
        address_row.addWidget(self._confirm)
        network_layout.addLayout(address_row)
        self._ip_host = QLabel("Confirmed ipHost · Not confirmed")
        self._ip_host.setObjectName("ipHostLabel")
        self._ip_host.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        network_layout.addWidget(self._ip_host)

        self.task_card, task_layout = _card("TASK CONTROL")
        choose = QLabel("Choose task")
        choose.setObjectName("mutedLabel")
        self._task = QComboBox()
        self._task.setObjectName("taskCombo")
        for task in TaskCatalog.ALL:
            self._task.addItem(
                f"{task.name}  ·  {task.window_count} windows  ·  {task.startup_script}",
                task.key,
            )
        self._task.currentIndexChanged.connect(self._emit_task)
        self._execute = QPushButton("EXECUTE TASK")
        self._execute.setObjectName("executeTaskButton")
        self._execute.clicked.connect(self.execute_requested.emit)
        task_layout.addWidget(choose)
        task_layout.addWidget(self._task)
        task_layout.addWidget(self._execute)

        self.devices_card, devices_layout = _card("CONNECTED DEVICES")
        self._ssh_host = QLineEdit()
        self._ssh_host.setObjectName("sshHostEdit")
        self._ssh_host.setPlaceholderText("Robot SSH host / IP")
        self._ssh_user = QLineEdit("nvidia")
        self._ssh_user.setObjectName("sshUserEdit")
        self._ssh_user.setPlaceholderText("SSH username")
        self._ssh_password = QLineEdit()
        self._ssh_password.setObjectName("sshPasswordEdit")
        self._ssh_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._ssh_password.setPlaceholderText("SSH password (optional)")
        self._device = QLabel("Device 01 · Offline\nIP: Not connected")
        self._device.setObjectName("deviceAddressLabel")
        self._device.setWordWrap(True)
        self._device.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        devices_layout.addWidget(self._ssh_host)
        devices_layout.addWidget(self._ssh_user)
        devices_layout.addWidget(self._ssh_password)
        devices_layout.addWidget(self._device)

        self.mid_row = QWidget()
        self._mid_layout = QHBoxLayout(self.mid_row)
        self._mid_layout.setContentsMargins(0, 0, 0, 0)
        self._mid_layout.setSpacing(12)
        self._mid_layout.addWidget(self.task_card, 1)
        self._mid_layout.addWidget(self.devices_card, 1)
        self._controls_stacked = False

        self._start = QPushButton("START QBOT")
        self._start.setObjectName("startListenersButton")
        self._start.setMinimumHeight(48)
        self._start.clicked.connect(self.start_requested.emit)
        self._disconnect = QPushButton("EMERGENCY DISCONNECT")
        self._disconnect.setObjectName("emergencyDisconnectButton")
        self._disconnect.setMinimumHeight(48)
        self._disconnect.clicked.connect(self.disconnect_requested.emit)
        self.actions_row = QWidget()
        self._actions_layout = QHBoxLayout(self.actions_row)
        self._actions_layout.setContentsMargins(0, 0, 0, 0)
        self._actions_layout.setSpacing(12)
        self._actions_layout.addWidget(self._start, 1)
        self._actions_layout.addWidget(self._disconnect, 1)

        self.footer = QWidget()
        footer = QHBoxLayout(self.footer)
        footer.setContentsMargins(0, 0, 0, 0)
        left = QLabel("PLATFORM CONTROL")
        left.setObjectName("appSubtitle")
        right = QLabel("SYSTEM MONITORING")
        right.setObjectName("appSubtitle")
        footer.addWidget(left)
        footer.addStretch(1)
        footer.addWidget(right)

        # Keep a default empty layout so the panel can exist as a QObject owner.
        QVBoxLayout(self).setContentsMargins(0, 0, 0, 0)

    @property
    def address_chooser(self) -> AddressChooser:
        return self._addresses

    def current_task(self) -> TaskProfile:
        key = self._task.currentData()
        if not isinstance(key, str):
            return TaskCatalog.default()
        return TaskCatalog.by_key(key)

    def ssh_target(self) -> SshTarget:
        return SshTarget(
            host=self._ssh_host.text().strip(),
            username=self._ssh_user.text().strip(),
            password=self._ssh_password.text(),
        )

    def set_task_enabled(self, enabled: bool) -> None:
        self._task.setEnabled(enabled)
        self._execute.setEnabled(enabled)

    def set_ssh_enabled(self, enabled: bool) -> None:
        self._ssh_host.setEnabled(enabled)
        self._ssh_user.setEnabled(enabled)
        self._ssh_password.setEnabled(enabled)

    def set_address_enabled(self, enabled: bool) -> None:
        self._addresses.setEnabled(enabled)
        self._refresh.setEnabled(enabled)
        self._confirm.setEnabled(enabled)

    def set_listening(self, listening: bool) -> None:
        self._listening = listening
        self._network_status.setText(
            "NETWORK: CONNECTED" if listening else "NETWORK: DISCONNECTED"
        )
        self._start.setEnabled(not listening)
        self._start.setText("START QBOT")
        self._start.setObjectName("startListenersButton" if not listening else "startQbotButton")
        self.style().unpolish(self._start)
        self.style().polish(self._start)

    def set_confirmed(self, device_name: str | None, address: str | None) -> None:
        if address:
            self._ip_host.setText(f"Confirmed ipHost · {address}")
        else:
            self._ip_host.setText("Confirmed ipHost · Not confirmed")
        device = device_name if device_name else "Device 01"
        if address:
            self._device.setText(f"{device} · Online\nIP: {address}")
        else:
            self._device.setText(f"{device} · Offline\nIP: Not connected")

    def set_session_enabled(self, enabled: bool) -> None:
        if not self._listening:
            self._start.setEnabled(enabled)
        self._execute.setEnabled(enabled and not self._listening)

    def apply_breakpoint(self, width: int) -> None:
        """Stack task/devices and action buttons when the window is narrow."""
        stacked = stack_controls(width)
        if stacked == self._controls_stacked:
            return
        self._controls_stacked = stacked
        direction = (
            QBoxLayout.Direction.TopToBottom
            if stacked
            else QBoxLayout.Direction.LeftToRight
        )
        self._mid_layout.setDirection(direction)
        self._actions_layout.setDirection(direction)

    def _emit_task(self, _index: int) -> None:
        task = self.current_task()
        self.task_changed.emit(task.key)
