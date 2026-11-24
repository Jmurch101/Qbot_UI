"""Control-center main window with Init and Platform screens."""

from __future__ import annotations

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtGui import QCloseEvent, QResizeEvent
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from qbotui.bind_policy import BindPolicy, BindRejected
from qbotui.connection_panel import ConnectionPanel
from qbotui.contract import ProbeContract
from qbotui.feed_workspace import FeedWorkspace
from qbotui.frame_codec import FrameCodec
from qbotui.interface_directory import InterfaceDirectory
from qbotui.platform_screen import PlatformScreen
from qbotui.ssh_launcher import SshLaunchError, SshTarget, launch_remote_script
from qbotui.tasks import TaskCatalog, TaskProfile
from qbotui.theme import CONTROL_CENTER_QSS
from qbotui.viewer import Viewer


class _FrameSink(QObject):
    """GUI-thread receiver for one probe's raw frames."""

    def __init__(self, label: str, window: QbotMainWindow) -> None:
        super().__init__(window)
        self._label = label
        self._window = window

    @Slot(bytes)
    def accept(self, payload: bytes) -> None:
        self._window._show_payload(self._label, payload)


class _SshStartWorker(QThread):
    """Run the SSH task start off the GUI thread."""

    succeeded = Signal(str)
    failed = Signal(str)

    def __init__(self, target: SshTarget, task: TaskProfile, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._target = target
        self._task = task

    def run(self) -> None:
        try:
            result = launch_remote_script(
                self._target,
                self._task.remote_command,
                self._task.startup_script,
            )
        except SshLaunchError as exc:
            self.failed.emit(str(exc))
            return
        except Exception as exc:
            self.failed.emit(f"SSH start failed: {exc}")
            return
        self.succeeded.emit(result.detail)


class QbotMainWindow(QMainWindow):
    """Select a task, connect listeners, and start that task on the SSH device."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("QBot Platform - Robotics Control & Management System")
        self.resize(1280, 900)
        self.setMinimumSize(520, 640)
        self.setStyleSheet(CONTROL_CENTER_QSS)
        self._layout_width = 0

        self._directory = InterfaceDirectory()
        self._policy = BindPolicy()
        self._codec = FrameCodec()
        self._viewer = Viewer(self._policy, parent=self)
        self._device_name: str | None = None
        self._task = TaskCatalog.default()
        self._ssh_worker: _SshStartWorker | None = None

        self._connection = ConnectionPanel()
        self._connection.refresh_requested.connect(self._reload_addresses)
        self._connection.confirm_requested.connect(self._confirm_address)
        self._connection.execute_requested.connect(self._execute_task)
        self._connection.start_requested.connect(self._connect_session)
        self._connection.disconnect_requested.connect(self._disconnect_session)
        self._connection.open_platform_requested.connect(lambda: self._show_screen(1))
        self._connection.task_changed.connect(self._on_task_changed)
        self._address_list = self._connection.address_chooser

        self._workspace = FeedWorkspace()
        self._workspace.apply_observer(self._task.observer)

        listen_labels = [stream.label for stream in self._task.streams()]
        self._platform = PlatformScreen(
            listen_labels or list(self._task.stream_labels),
            self._workspace,
        )
        self._platform.back_requested.connect(lambda: self._show_screen(0))
        self._status = self._platform.status_board

        self._sinks: list[_FrameSink] = []
        self._viewer.servers_changed.connect(self._wire_viewer_servers)
        self._wire_viewer_servers()

        self._screens = QStackedWidget()
        self._screens.setObjectName("screenStack")
        self._screens.addWidget(self._connection)
        self._screens.addWidget(self._platform)

        outer = QVBoxLayout()
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(0)
        outer.addWidget(self._screens, 1)

        central = QWidget()
        central.setLayout(outer)
        self.setCentralWidget(central)

        self._viewer.set_streams(self._task.streams())
        self._reload_addresses()
        self._sync_controls()
        self._apply_responsive_layout(self.width())
        self._show_screen(0)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._apply_responsive_layout(event.size().width())

    def _apply_responsive_layout(self, width: int) -> None:
        if width == self._layout_width:
            return
        self._layout_width = width
        self._connection.apply_breakpoint(width)
        # Use half-window width for mosaic column decisions (WINDOWS cell ~50%).
        self._workspace.set_host_width(max(width // 2, 1))

    def _wire_viewer_servers(self) -> None:
        self._sinks = []
        for server in self._viewer.servers:
            server.state_changed.connect(self._status.set_state)
            server.activity.connect(self._status.set_activity)
            sink = _FrameSink(server.label, self)
            self._sinks.append(sink)
            server.frame_ready.connect(sink.accept)

    def _show_screen(self, index: int) -> None:
        self._screens.setCurrentIndex(index)

    def set_platform_power(self, voltage: float | None, battery_percent: float | None) -> None:
        """Update platform voltage (V) and battery charge (%)."""
        self._platform.set_voltage(voltage)
        self._platform.set_battery_percent(battery_percent)

    @Slot(str, bytes)
    def _show_payload(self, label: str, payload: bytes) -> None:
        panel = self._task.observer.panel_for_stream(label)
        if panel is None:
            return
        tile_label = panel.label
        if tile_label not in self._workspace.feeds:
            return
        stream = next(
            (item for item in ProbeContract.STREAMS if item.label == label),
            None,
        )
        if stream is None:
            return
        try:
            presented = self._codec.present(stream, payload)
        except Exception as exc:
            self._workspace.set_detail(tile_label, f"frame error: {exc}")
            return
        self._workspace.show_frame(tile_label, presented.image)
        if presented.detail:
            self._workspace.set_detail(tile_label, presented.detail)

    def closeEvent(self, event: QCloseEvent) -> None:
        self._cancel_ssh_worker()
        self._workspace.shutdown()
        self._viewer.stop()
        event.accept()

    def _show_note(self, message: str) -> None:
        """Show feedback on Init (always) and Platform console."""
        self._connection.show_note(message)
        self._status.show_note(message)

    def _reload_addresses(self) -> None:
        try:
            rows = self._directory.list_addresses()
        except OSError as exc:
            self._address_list.replace_rows([])
            self._show_note(f"Address enumeration failed: {exc}")
            return
        self._address_list.replace_rows(rows)
        if not rows:
            self._show_note("No eligible IPv4 address was enumerated.")
        else:
            self._show_note(
                f"Found {len(rows)} laptop address(es). Pick your Quanser_UVS 192.168.2.x IP."
            )

    def _confirm_address(self) -> None:
        if self._viewer.listeners_active:
            self._show_note("Stop listeners before confirming a new laptop IP.")
            return
        if not self._connection.ssh_target().host:
            self._show_note("Select a QBot first (step 1), then confirm the laptop IP.")
            return
        chosen = self._address_list.chosen_row()
        if chosen is None:
            self._show_note(
                "Select this laptop’s 192.168.2.x address in step 2, then press Confirm laptop IP."
            )
            return
        device_name, address = chosen
        try:
            confirmed = self._viewer.confirm_address(address)
        except BindRejected as exc:
            self._show_note(str(exc))
            return
        self._device_name = device_name
        robot = self._connection.current_robot()
        name = robot.name if robot else device_name
        self._connection.set_confirmed(name, confirmed)
        self._show_note(
            f"Laptop IP confirmed as ipHost {confirmed}. Press START to listen and run the script on the QBot."
        )
        self._sync_controls()

    def _execute_task(self) -> None:
        task = self._connection.current_task()
        if self._viewer.listeners_active:
            self._show_note("Disconnect before switching tasks.")
            return
        self._apply_task(task)
        self._show_note(f"Task ready: {task.name} · {task.startup_script}")

    def _on_task_changed(self, key: str) -> None:
        if self._viewer.listeners_active:
            return
        self._apply_task(TaskCatalog.by_key(key))

    def _apply_task(self, task: TaskProfile) -> None:
        self._task = task
        try:
            self._viewer.set_streams(task.streams())
        except BindRejected as exc:
            self._status.show_note(str(exc))
            return
        self._workspace.apply_observer(task.observer)
        listen_labels = [stream.label for stream in task.streams()]
        self._platform.set_labels(listen_labels or list(task.stream_labels))
        self._show_note(f"{task.name} · {task.startup_script}")
        self._sync_controls()

    def _connect_session(self) -> None:
        if self._ssh_worker is not None and self._ssh_worker.isRunning():
            self._show_note("SSH start is already in progress.")
            return
        ssh_target = self._connection.ssh_target()
        if not ssh_target.host:
            self._show_note("Select a QBot in step 1 (or type the robot IP).")
            return
        if self._viewer.confirmed_address is None:
            self._confirm_address()
            if self._viewer.confirmed_address is None:
                return
        if not ssh_target.username:
            self._show_note("Enter the SSH username (usually nvidia).")
            return

        task = self._connection.current_task()
        self._apply_task(task)
        try:
            self._viewer.set_streams(task.streams())
            self._viewer.start()
        except BindRejected as exc:
            self._show_note(str(exc))
            self._sync_controls()
            return

        robot = self._connection.current_robot()
        name = robot.name if robot else self._device_name
        self._connection.set_confirmed(name, self._viewer.confirmed_address)
        self._show_note(
            f"Listeners up on {self._viewer.confirmed_address}. "
            f"Starting {task.startup_script} on {ssh_target.host}…"
        )
        self._sync_controls()
        self._connection.set_session_enabled(False)
        self._show_screen(1)

        worker = _SshStartWorker(ssh_target, task, parent=self)
        worker.succeeded.connect(self._on_ssh_succeeded)
        worker.failed.connect(self._on_ssh_failed)
        worker.finished.connect(self._on_ssh_finished)
        self._ssh_worker = worker
        worker.start()

    def _disconnect_session(self) -> None:
        self._cancel_ssh_worker()
        self._viewer.stop()
        self._show_note("Disconnected · PC listeners stopped.")
        self._sync_controls()

    @Slot(str)
    def _on_ssh_succeeded(self, detail: str) -> None:
        self._show_note(detail)

    @Slot(str)
    def _on_ssh_failed(self, message: str) -> None:
        self._show_note(message)
        self._show_screen(0)

    @Slot()
    def _on_ssh_finished(self) -> None:
        self._ssh_worker = None
        self._sync_controls()

    def _cancel_ssh_worker(self) -> None:
        worker = self._ssh_worker
        if worker is None:
            return
        if worker.isRunning():
            worker.wait(1000)
        self._ssh_worker = None

    def _sync_controls(self) -> None:
        locked = self._viewer.listeners_active
        busy = self._ssh_worker is not None and self._ssh_worker.isRunning()
        self._connection.set_listening(locked)
        self._connection.set_task_enabled(not locked and not busy)
        self._connection.set_ssh_enabled(not locked and not busy)
        self._connection.set_address_enabled(not locked and not busy)
        self._connection.set_session_enabled(not busy)
        if self._viewer.confirmed_address is not None:
            self._connection.set_confirmed(
                self._device_name,
                self._viewer.confirmed_address,
            )
        self._platform.set_platform_identity(
            device_name=self._device_name,
            ip_host=self._viewer.confirmed_address,
            network_connected=locked,
            task_name=self._task.name,
        )
