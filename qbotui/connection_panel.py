"""Initialization screen: pick QBot, pick laptop IP, start session."""

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
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from qbotui.address_chooser import AddressChooser
from qbotui.robots import RobotCatalog, RobotProfile
from qbotui.ssh_launcher import SshTarget
from qbotui.tasks import TaskCatalog, TaskProfile


def _card(title: str, *, object_name: str = "card") -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName(object_name)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(20, 18, 20, 18)
    layout.setSpacing(10)
    heading = QLabel(title)
    heading.setObjectName("sectionTitle")
    layout.addWidget(heading)
    return frame, layout


def _field_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("mutedLabel")
    label.setWordWrap(True)
    return label


class ConnectionPanel(QWidget):
    """Init screen: two IPs (robot + laptop), one task, clear actions."""

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

        # Compact header (not a giant hero — leaves room for the form).
        self.hero = QFrame()
        self.hero.setObjectName("initHero")
        self.hero.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        hero_layout = QVBoxLayout(self.hero)
        hero_layout.setContentsMargins(20, 14, 20, 14)
        hero_layout.setSpacing(4)
        app_title = QLabel("QBOT PLATFORM")
        app_title.setObjectName("heroTitle")
        app_sub = QLabel("Connect a QBot, then start its lab script from this PC")
        app_sub.setObjectName("heroSubtitle")
        app_sub.setWordWrap(True)
        hero_layout.addWidget(app_title)
        hero_layout.addWidget(app_sub)

        # Kept for older layout / chrome hooks.
        self.header = QWidget()
        self.header.setVisible(False)
        QVBoxLayout(self.header).setContentsMargins(0, 0, 0, 0)

        self.device_card, form = _card("CONNECT")
        self.device_card.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.network_card = self.device_card
        self.task_card = self.device_card
        self.devices_card = self.device_card

        # --- Step 1: robot ---
        form.addWidget(_field_label("1. QBot (robot) — pick the robot; its IP fills in below"))
        self._robot = QComboBox()
        self._robot.setObjectName("robotCombo")
        self._robot.addItem("Select a QBot…", None)
        for robot in RobotCatalog.ALL:
            self._robot.addItem(robot.label, robot.key)
        self._robot.currentIndexChanged.connect(self._on_robot_changed)
        form.addWidget(self._robot)

        form.addWidget(_field_label("Robot IP (SSH host) — where the app logs in"))
        self._ssh_host = QLineEdit()
        self._ssh_host.setObjectName("sshHostEdit")
        self._ssh_host.setPlaceholderText("Choose a QBot above, or type an IP")
        self._ssh_host.setClearButtonEnabled(True)
        form.addWidget(self._ssh_host)

        ssh_row = QHBoxLayout()
        ssh_row.setSpacing(8)
        self._ssh_user = QLineEdit("nvidia")
        self._ssh_user.setObjectName("sshUserEdit")
        self._ssh_user.setPlaceholderText("SSH username")
        self._ssh_password = QLineEdit()
        self._ssh_password.setObjectName("sshPasswordEdit")
        self._ssh_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._ssh_password.setPlaceholderText("SSH password (if needed)")
        ssh_row.addWidget(self._ssh_user, 1)
        ssh_row.addWidget(self._ssh_password, 1)
        form.addLayout(ssh_row)

        # --- Step 2: laptop ---
        form.addSpacing(6)
        form.addWidget(
            _field_label(
                "2. This laptop’s IP on Quanser_UVS — the address the robot dials (ipHost). "
                "Use your 192.168.2.x Wi‑Fi address, not Ethernet / Cursor."
            )
        )
        self._addresses = AddressChooser()
        self._addresses.setObjectName("addressList")
        self._refresh = QPushButton("Refresh")
        self._refresh.setObjectName("refreshAddressesButton")
        self._refresh.clicked.connect(self.refresh_requested.emit)
        address_row = QHBoxLayout()
        address_row.setSpacing(8)
        address_row.addWidget(self._addresses, 1)
        address_row.addWidget(self._refresh)
        form.addLayout(address_row)

        self._confirm = QPushButton("Confirm laptop IP")
        self._confirm.setObjectName("verifySshButton")
        self._confirm.setMinimumHeight(40)
        self._confirm.clicked.connect(self.confirm_requested.emit)
        form.addWidget(self._confirm)

        self._ip_host = QLabel("Laptop ipHost · not confirmed yet")
        self._ip_host.setObjectName("ipHostLabel")
        self._ip_host.setWordWrap(True)
        self._ip_host.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        form.addWidget(self._ip_host)

        # --- Step 3: task ---
        form.addSpacing(6)
        form.addWidget(_field_label("3. Lab task — script the QBot will run after START"))
        self._task = QComboBox()
        self._task.setObjectName("taskCombo")
        for task in TaskCatalog.ALL:
            self._task.addItem(
                f"{task.name}  ·  {task.startup_script}",
                task.key,
            )
        self._task.currentIndexChanged.connect(self._emit_task)
        form.addWidget(self._task)

        # Hidden APPLY control — task combo already applies; keep for API/tests.
        self._execute = QPushButton("APPLY TASK")
        self._execute.setObjectName("executeTaskButton")
        self._execute.setVisible(False)
        self._execute.clicked.connect(self.execute_requested.emit)
        form.addWidget(self._execute)

        self._verified_badge = QLabel("LAPTOP IP · NOT CONFIRMED")
        self._verified_badge.setObjectName("unverifiedBadge")
        self._verified_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form.addWidget(self._verified_badge)

        self._device = QLabel("No QBot selected")
        self._device.setObjectName("deviceAddressLabel")
        self._device.setWordWrap(True)
        self._device.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        form.addWidget(self._device)

        self._status_note = QLabel(
            "Pick a QBot, confirm this laptop’s 192.168.2.x IP, then press START."
        )
        self._status_note.setObjectName("initStatusNote")
        self._status_note.setWordWrap(True)
        form.addWidget(self._status_note)

        # Compatibility: unused decorative panels removed from layout but hooks kept.
        self.system_panels_card = QFrame()
        self.system_panels_card.setVisible(False)
        self._panel_marks: dict[str, QLabel] = {}
        self._ssh_key_badge = QLabel("SSH KEY")
        self._ssh_key_badge.setVisible(False)

        scroll = QScrollArea()
        scroll.setObjectName("initScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(self.device_card)

        self.mid_row = scroll
        self._mid_layout = QHBoxLayout()  # unused; kept for apply_breakpoint API

        # --- Footer actions (always visible, outside scroll) ---
        self._start = QPushButton("START — listen + run script on QBot")
        self._start.setObjectName("startListenersButton")
        self._start.setMinimumHeight(48)
        self._start.clicked.connect(self._on_start_or_disconnect)

        self._open_platform = QPushButton("Open camera platform")
        self._open_platform.setObjectName("openPlatformButton")
        self._open_platform.setMinimumHeight(48)
        self._open_platform.clicked.connect(self.open_platform_requested.emit)

        self._disconnect = QPushButton("EMERGENCY DISCONNECT")
        self._disconnect.setObjectName("emergencyDisconnectButton")
        self._disconnect.setVisible(False)
        self._disconnect.clicked.connect(self.disconnect_requested.emit)

        self.actions_row = QWidget()
        self._actions_layout = QHBoxLayout(self.actions_row)
        self._actions_layout.setContentsMargins(0, 0, 0, 0)
        self._actions_layout.setSpacing(10)
        self._actions_layout.addWidget(self._start, 2)
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
        root.setSpacing(12)
        root.addWidget(self.hero, 0)
        root.addWidget(scroll, 1)
        root.addWidget(self.actions_row, 0)
        root.addWidget(self._disconnect)

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

    def show_note(self, message: str) -> None:
        """Surface feedback on the Init screen (not only on Platform)."""
        self._status_note.setText(message)

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
            self._start.setText("STOP listeners (disconnect)")
            self._start.setObjectName("emergencyDisconnectButton")
            self._set_panel_state("listeners", True)
            self._set_panel_state("activity", True)
        else:
            self._start.setText("START — listen + run script on QBot")
            self._start.setObjectName("startListenersButton")
            self._set_panel_state("listeners", False)
        self.style().unpolish(self._start)
        self.style().polish(self._start)
        self._start.setEnabled(True)

    def set_confirmed(self, device_name: str | None, address: str | None) -> None:
        if address:
            self._ip_host.setText(f"Laptop ipHost · {address}")
            self._verified = True
            self._verified_badge.setText("LAPTOP IP · CONFIRMED")
            self._verified_badge.setObjectName("verifiedBadge")
            self._set_panel_state("events", True)
            self._set_panel_state("diagnostics", True)
        else:
            self._ip_host.setText("Laptop ipHost · not confirmed yet")
            self._verified = False
            self._verified_badge.setText("LAPTOP IP · NOT CONFIRMED")
            self._verified_badge.setObjectName("unverifiedBadge")
            self._set_panel_state("events", False)
            self._set_panel_state("diagnostics", False)
        self.style().unpolish(self._verified_badge)
        self.style().polish(self._verified_badge)
        robot = self.current_robot()
        device = robot.name if robot else (device_name if device_name else "No QBot selected")
        robot_ip = self._ssh_host.text().strip() or (robot.host if robot else "—")
        if address:
            self._device.setText(
                f"{device}\nRobot IP: {robot_ip}\nLaptop IP (ipHost): {address}"
            )
        else:
            self._device.setText(f"{device}\nRobot IP: {robot_ip}\nLaptop IP: not confirmed")

    def set_session_enabled(self, enabled: bool) -> None:
        if not self._listening:
            self._start.setEnabled(enabled)
        self._execute.setEnabled(enabled and not self._listening)
        self._open_platform.setEnabled(True)

    def apply_breakpoint(self, width: int) -> None:
        """Footer stacks on narrow windows; form stays single-column in scroll."""
        stacked = width < 720
        if stacked == self._controls_stacked:
            return
        self._controls_stacked = stacked
        # Rebuild action row direction without depending on mid_layout.
        while self._actions_layout.count():
            item = self._actions_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        if stacked:
            self._actions_layout.setDirection(QBoxLayout.Direction.TopToBottom)
        else:
            self._actions_layout.setDirection(QBoxLayout.Direction.LeftToRight)
        self._actions_layout.addWidget(self._start, 2)
        self._actions_layout.addWidget(self._open_platform, 1)

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
            self.set_confirmed(None, self._confirmed_address())
            return
        self._ssh_host.setText(robot.host)
        self.set_confirmed(robot.name, self._confirmed_address())

    def _confirmed_address(self) -> str | None:
        text = self._ip_host.text()
        marker = "Laptop ipHost · "
        if not text.startswith(marker):
            return None
        value = text[len(marker) :].strip()
        if not value or value == "not confirmed yet":
            return None
        return value

    def _emit_task(self, _index: int) -> None:
        task = self.current_task()
        self.task_changed.emit(task.key)
