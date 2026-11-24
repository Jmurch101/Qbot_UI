"""Initialization screen: device selection, system panels, START / OPEN PLATFORM."""

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
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from qbotui.address_chooser import AddressChooser
from qbotui.responsive import stack_controls
from qbotui.robots import RobotCatalog, RobotProfile
from qbotui.ssh_launcher import SshTarget
from qbotui.tasks import TaskCatalog, TaskProfile


def _card(title: str, *, object_name: str = "card") -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName(object_name)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(18, 16, 18, 16)
    layout.setSpacing(12)
    heading = QLabel(title)
    heading.setObjectName("sectionTitle")
    layout.addWidget(heading)
    return frame, layout


def _checklist_row(text: str) -> tuple[QWidget, QLabel]:
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 4, 0, 4)
    layout.setSpacing(10)
    mark = QLabel("○")
    mark.setObjectName("checklistMark")
    mark.setFixedWidth(22)
    label = QLabel(text)
    label.setObjectName("checklistLabel")
    layout.addWidget(mark, 0, Qt.AlignmentFlag.AlignTop)
    layout.addWidget(label, 1)
    return row, mark


class ConnectionPanel(QWidget):
    """Init / Operations screen matching the device-selection mock."""

    refresh_requested = Signal()
    confirm_requested = Signal()
    execute_requested = Signal()
    start_requested = Signal()
    disconnect_requested = Signal()
    open_platform_requested = Signal()
    task_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("connectionPanel")
        self._listening = False
        self._verified = False
        self._controls_stacked = False

        # --- Hero ---
        self.hero = QFrame()
        self.hero.setObjectName("initHero")
        self.hero.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        hero_layout = QVBoxLayout(self.hero)
        hero_layout.setContentsMargins(24, 28, 24, 24)
        hero_layout.setSpacing(8)
        hero_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        app_title = QLabel("QBOT PLATFORM")
        app_title.setObjectName("heroTitle")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_sub = QLabel("ROBOTICS CONTROL & MANAGEMENT SYSTEM")
        app_sub.setObjectName("heroSubtitle")
        app_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._init_pill = QLabel("INITIALIZATION")
        self._init_pill.setObjectName("initPill")
        self._init_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._init_pill.setFixedWidth(160)

        hero_layout.addWidget(app_title)
        hero_layout.addWidget(app_sub)
        pill_row = QHBoxLayout()
        pill_row.addStretch(1)
        pill_row.addWidget(self._init_pill)
        pill_row.addStretch(1)
        hero_layout.addSpacing(8)
        hero_layout.addLayout(pill_row)

        # Keep a compact header handle for main_window title chrome on Platform.
        self.header = QWidget()
        self.header.setVisible(False)
        QVBoxLayout(self.header).setContentsMargins(0, 0, 0, 0)

        # --- Device selection ---
        self.device_card, device_layout = _card("⚙  DEVICE SELECTION")
        self.device_card.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        robot_label = QLabel("QBot")
        robot_label.setObjectName("mutedLabel")
        self._robot = QComboBox()
        self._robot.setObjectName("robotCombo")
        self._robot.addItem("Select a QBot…", None)
        for robot in RobotCatalog.ALL:
            self._robot.addItem(robot.label, robot.key)
        self._robot.currentIndexChanged.connect(self._on_robot_changed)
        device_layout.addWidget(robot_label)
        device_layout.addWidget(self._robot)

        select_label = QLabel("PC ipHost (this machine)")
        select_label.setObjectName("mutedLabel")
        self._addresses = AddressChooser()
        self._addresses.setObjectName("addressList")
        self._refresh = QPushButton("Refresh")
        self._refresh.setObjectName("refreshAddressesButton")
        self._refresh.clicked.connect(self.refresh_requested.emit)
        address_row = QHBoxLayout()
        address_row.setSpacing(8)
        address_row.addWidget(self._addresses, 1)
        address_row.addWidget(self._refresh)
        device_layout.addWidget(select_label)
        device_layout.addLayout(address_row)

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
        device_layout.addWidget(self._ssh_host)
        device_layout.addWidget(self._ssh_user)
        device_layout.addWidget(self._ssh_password)

        task_label = QLabel("Task")
        task_label.setObjectName("mutedLabel")
        self._task = QComboBox()
        self._task.setObjectName("taskCombo")
        for task in TaskCatalog.ALL:
            self._task.addItem(
                f"{task.name}  ·  {task.window_count} windows  ·  {task.startup_script}",
                task.key,
            )
        self._task.currentIndexChanged.connect(self._emit_task)
        self._execute = QPushButton("APPLY TASK")
        self._execute.setObjectName("executeTaskButton")
        self._execute.clicked.connect(self.execute_requested.emit)
        device_layout.addWidget(task_label)
        device_layout.addWidget(self._task)
        device_layout.addWidget(self._execute)

        auth_row = QHBoxLayout()
        auth_caption = QLabel("SSH Authentication")
        auth_caption.setObjectName("mutedLabel")
        self._ssh_key_badge = QLabel("SSH KEY")
        self._ssh_key_badge.setObjectName("sshKeyBadge")
        auth_row.addWidget(auth_caption, 1)
        auth_row.addWidget(self._ssh_key_badge)
        device_layout.addLayout(auth_row)

        verify_row = QHBoxLayout()
        conn_caption = QLabel("Connection status")
        conn_caption.setObjectName("mutedLabel")
        self._verified_badge = QLabel("UNVERIFIED")
        self._verified_badge.setObjectName("unverifiedBadge")
        verify_row.addWidget(conn_caption, 1)
        verify_row.addWidget(self._verified_badge)
        device_layout.addLayout(verify_row)

        self._ip_host = QLabel("Confirmed ipHost · Not confirmed")
        self._ip_host.setObjectName("ipHostLabel")
        self._ip_host.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._device = QLabel("Device 01 · Offline\nIP: Not connected")
        self._device.setObjectName("deviceAddressLabel")
        self._device.setWordWrap(True)
        self._device.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        device_layout.addWidget(self._ip_host)
        device_layout.addWidget(self._device)

        self._confirm = QPushButton("▶  VERIFY SSH CONNECTION")
        self._confirm.setObjectName("verifySshButton")
        self._confirm.setMinimumHeight(44)
        self._confirm.clicked.connect(self.confirm_requested.emit)
        device_layout.addStretch(1)
        device_layout.addWidget(self._confirm)

        # Compatibility aliases used by older layout code / tests.
        self.network_card = self.device_card
        self.task_card = self.device_card
        self.devices_card = self.device_card

        # --- Initial system panels ---
        self.system_panels_card, panels_layout = _card("📋  INITIAL SYSTEM PANELS")
        self.system_panels_card.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._panel_marks: dict[str, QLabel] = {}
        for key, text in (
            ("activity", "System Activity"),
            ("events", "Connection Events"),
            ("diagnostics", "Device Diagnostics"),
            ("listeners", "Listener Status"),
        ):
            row, mark = _checklist_row(text)
            self._panel_marks[key] = mark
            panels_layout.addWidget(row)
        panels_layout.addStretch(1)

        self.mid_row = QWidget()
        self._mid_layout = QHBoxLayout(self.mid_row)
        self._mid_layout.setContentsMargins(0, 0, 0, 0)
        self._mid_layout.setSpacing(14)
        self._mid_layout.addWidget(self.device_card, 1)
        self._mid_layout.addWidget(self.system_panels_card, 1)

        # --- Footer actions ---
        self._start = QPushButton("▶  START")
        self._start.setObjectName("startListenersButton")
        self._start.setMinimumHeight(56)
        self._start.clicked.connect(self._on_start_or_disconnect)

        self._open_platform = QPushButton("▦  OPEN QBOT PLATFORM")
        self._open_platform.setObjectName("openPlatformButton")
        self._open_platform.setMinimumHeight(56)
        self._open_platform.clicked.connect(self.open_platform_requested.emit)

        # Hidden disconnect handle for tests / callers that still look it up.
        self._disconnect = QPushButton("EMERGENCY DISCONNECT")
        self._disconnect.setObjectName("emergencyDisconnectButton")
        self._disconnect.setVisible(False)
        self._disconnect.clicked.connect(self.disconnect_requested.emit)

        self.actions_row = QWidget()
        self._actions_layout = QHBoxLayout(self.actions_row)
        self._actions_layout.setContentsMargins(0, 0, 0, 0)
        self._actions_layout.setSpacing(14)
        self._actions_layout.addWidget(self._start, 1)
        self._actions_layout.addWidget(self._open_platform, 1)

        self.footer = QWidget()
        self.footer.setVisible(False)
        QVBoxLayout(self.footer).setContentsMargins(0, 0, 0, 0)

        self._network_status = QLabel("NETWORK: DISCONNECTED")
        self._network_status.setObjectName("networkStatusLabel")
        self._network_status.setVisible(False)
        self._system_ready = QLabel("SYSTEM READY")
        self._system_ready.setObjectName("systemReadyPill")
        self._system_ready.setVisible(False)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)
        root.addWidget(self.hero, 2)
        root.addWidget(self.mid_row, 5)
        root.addWidget(self.actions_row, 1)
        root.addWidget(self._disconnect)

        self._set_panel_state("activity", False)
        self._set_panel_state("events", False)
        self._set_panel_state("diagnostics", False)
        self._set_panel_state("listeners", False)

    @property
    def address_chooser(self) -> AddressChooser:
        return self._addresses

    def current_task(self) -> TaskProfile:
        key = self._task.currentData()
        if not isinstance(key, str):
            return TaskCatalog.default()
        return TaskCatalog.by_key(key)

    def current_robot(self) -> RobotProfile | None:
        key = self._robot.currentData()
        if not isinstance(key, str):
            return None
        return RobotCatalog.by_key(key)

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
        self._robot.setEnabled(enabled)
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
        if listening:
            self._start.setText("■  EMERGENCY DISCONNECT")
            self._start.setObjectName("emergencyDisconnectButton")
            self._set_panel_state("listeners", True)
            self._set_panel_state("activity", True)
        else:
            self._start.setText("▶  START")
            self._start.setObjectName("startListenersButton")
            self._set_panel_state("listeners", False)
        self.style().unpolish(self._start)
        self.style().polish(self._start)
        self._start.setEnabled(True)

    def set_confirmed(self, device_name: str | None, address: str | None) -> None:
        if address:
            self._ip_host.setText(f"Confirmed ipHost · {address}")
            self._verified = True
            self._verified_badge.setText("VERIFIED")
            self._verified_badge.setObjectName("verifiedBadge")
            self._set_panel_state("events", True)
            self._set_panel_state("diagnostics", True)
        else:
            self._ip_host.setText("Confirmed ipHost · Not confirmed")
            self._verified = False
            self._verified_badge.setText("UNVERIFIED")
            self._verified_badge.setObjectName("unverifiedBadge")
            self._set_panel_state("events", False)
            self._set_panel_state("diagnostics", False)
        self.style().unpolish(self._verified_badge)
        self.style().polish(self._verified_badge)
        robot = self.current_robot()
        device = robot.name if robot else (device_name if device_name else "Device 01")
        robot_ip = robot.host if robot else "—"
        if address:
            self._device.setText(f"{device} · Online\nQBot IP: {robot_ip}\nipHost: {address}")
        else:
            self._device.setText(f"{device} · Offline\nQBot IP: {robot_ip}")

    def set_session_enabled(self, enabled: bool) -> None:
        if not self._listening:
            self._start.setEnabled(enabled)
        self._execute.setEnabled(enabled and not self._listening)
        self._open_platform.setEnabled(True)

    def apply_breakpoint(self, width: int) -> None:
        """Stack device/panels and footer buttons when the window is narrow."""
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

    def _on_start_or_disconnect(self) -> None:
        if self._listening:
            self.disconnect_requested.emit()
        else:
            self.start_requested.emit()

    def _set_panel_state(self, key: str, done: bool) -> None:
        mark = self._panel_marks.get(key)
        if mark is None:
            return
        mark.setText("●" if done else "○")
        mark.setObjectName("checklistMarkDone" if done else "checklistMark")
        self.style().unpolish(mark)
        self.style().polish(mark)

    def _on_robot_changed(self, _index: int) -> None:
        robot = self.current_robot()
        if robot is None:
            return
        self._ssh_host.setText(robot.host)
        # Refresh device line with the selected QBot name/IP.
        confirmed = None
        text = self._ip_host.text()
        marker = "Confirmed ipHost · "
        if text.startswith(marker):
            value = text[len(marker) :].strip()
            if value and value != "Not confirmed":
                confirmed = value
        self.set_confirmed(robot.name, confirmed)

    def _emit_task(self, _index: int) -> None:
        task = self.current_task()
        self.task_changed.emit(task.key)
