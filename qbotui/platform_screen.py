"""Platform monitor: WINDOWS | BASH over PLATFORM INFO | SYSTEM ACTIVITY."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from qbotui.feed_workspace import FeedWorkspace
from qbotui.status_board import StatusBoard


def _section(title: str) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("card")
    frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 12, 14, 12)
    layout.setSpacing(8)
    heading = QLabel(title)
    heading.setObjectName("sectionTitle")
    layout.addWidget(heading)
    return frame, layout


class PlatformScreen(QWidget):
    """Mock-aligned platform grid with proportional 70/30 × 50/50 cells."""

    back_requested = Signal()

    # Row stretch mirrors ~70% top / ~20–25% bottom of usable height.
    TOP_ROW_STRETCH = 7
    BOTTOM_ROW_STRETCH = 2

    def __init__(
        self,
        labels: list[str],
        workspace: FeedWorkspace,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("platformScreen")
        self._workspace = workspace
        self._workspace.set_section_title("WINDOWS")
        self._workspace.setMinimumHeight(0)
        self._workspace.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        title = QLabel("QBOT PLATFORM")
        title.setObjectName("platformPageTitle")
        self._back = QPushButton("← INIT")
        self._back.setObjectName("backInitButton")
        self._back.clicked.connect(self.back_requested.emit)
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(title, 1)
        header.addWidget(self._back, 0, Qt.AlignmentFlag.AlignRight)

        # WINDOWS cell — feed mosaic fills the section.
        windows_card, windows_layout = _section("WINDOWS")
        # Workspace already draws its own card; embed grid host content area only.
        # Use the workspace widget directly and hide duplicate outer title via API.
        self._workspace.set_chrome_visible(False)
        windows_layout.addWidget(self._workspace, 1)

        # BASH cell
        bash_card, bash_layout = _section("BASH")
        self._status = StatusBoard(labels)
        self._status.set_title("BASH")
        self._status.set_chrome_compact(True)
        self._status.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        bash_layout.addWidget(self._status, 1)

        # PLATFORM INFO cell
        info_card, info_layout = _section("PLATFORM INFO")
        self._info_summary = QLabel("Device • IP • Hardware • Status")
        self._info_summary.setObjectName("platformInfoLine")
        self._info_summary.setWordWrap(True)
        self._device_name = QLabel("Device: —")
        self._device_name.setObjectName("mutedLabel")
        self._ip_host = QLabel("ipHost: —")
        self._ip_host.setObjectName("mutedLabel")
        self._network = QLabel("Network: disconnected")
        self._network.setObjectName("mutedLabel")
        self._task = QLabel("Task: —")
        self._task.setObjectName("mutedLabel")

        power_row = QHBoxLayout()
        power_row.setSpacing(16)
        self._voltage_value = QLabel("— V")
        self._voltage_value.setObjectName("metricValueCompact")
        self._battery_value = QLabel("— %")
        self._battery_value.setObjectName("metricValueCompact")
        self._battery_bar = QProgressBar()
        self._battery_bar.setObjectName("batteryBar")
        self._battery_bar.setRange(0, 100)
        self._battery_bar.setValue(0)
        self._battery_bar.setTextVisible(False)
        self._battery_bar.setMaximumHeight(10)
        power_row.addWidget(self._voltage_value)
        power_row.addWidget(self._battery_value)
        power_row.addWidget(self._battery_bar, 1)

        self._source = QLabel("Telemetry: waiting for platform data")
        self._source.setObjectName("mutedLabel")
        self._source.setWordWrap(True)

        info_layout.addWidget(self._info_summary)
        info_layout.addWidget(self._device_name)
        info_layout.addWidget(self._ip_host)
        info_layout.addWidget(self._network)
        info_layout.addWidget(self._task)
        info_layout.addLayout(power_row)
        info_layout.addWidget(self._source)
        info_layout.addStretch(1)

        # SYSTEM ACTIVITY cell
        activity_card, activity_layout = _section("SYSTEM ACTIVITY")
        live_row = QHBoxLayout()
        live_row.setSpacing(8)
        self._live_dot = QLabel("●")
        self._live_dot.setObjectName("liveDot")
        self._live_label = QLabel("LIVE")
        self._live_label.setObjectName("liveText")
        live_row.addWidget(self._live_dot)
        live_row.addWidget(self._live_label)
        live_row.addStretch(1)
        self._activity_detail = QLabel("Listener events and diagnostics")
        self._activity_detail.setObjectName("platformInfoLine")
        self._activity_detail.setWordWrap(True)
        activity_layout.addLayout(live_row)
        activity_layout.addWidget(self._activity_detail)
        activity_layout.addStretch(1)

        self._grid = QGridLayout()
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setHorizontalSpacing(12)
        self._grid.setVerticalSpacing(12)
        self._grid.addWidget(windows_card, 0, 0)
        self._grid.addWidget(bash_card, 0, 1)
        self._grid.addWidget(info_card, 1, 0)
        self._grid.addWidget(activity_card, 1, 1)
        self._grid.setRowStretch(0, self.TOP_ROW_STRETCH)
        self._grid.setRowStretch(1, self.BOTTOM_ROW_STRETCH)
        self._grid.setColumnStretch(0, 1)
        self._grid.setColumnStretch(1, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addLayout(header, 0)
        layout.addLayout(self._grid, 1)

        self._voltage: float | None = None
        self._battery_percent: float | None = None
        self._identity = {
            "device": "—",
            "ip": "—",
            "hardware": "QBot",
            "status": "idle",
        }

    @property
    def status_board(self) -> StatusBoard:
        return self._status

    @property
    def workspace(self) -> FeedWorkspace:
        return self._workspace

    @property
    def grid_layout(self) -> QGridLayout:
        return self._grid

    def set_labels(self, labels: list[str]) -> None:
        self._status.set_labels(labels)
        self._refresh_activity()

    def show_note(self, text: str) -> None:
        self._status.show_note(text)
        self._refresh_activity()

    def set_platform_identity(
        self,
        *,
        device_name: str | None,
        ip_host: str | None,
        network_connected: bool,
        task_name: str | None,
    ) -> None:
        device = device_name if device_name else "—"
        host = ip_host if ip_host else "—"
        status = "connected" if network_connected else "disconnected"
        self._identity = {
            "device": device,
            "ip": host,
            "hardware": task_name if task_name else "QBot",
            "status": status,
        }
        self._device_name.setText(f"Device: {device}")
        self._ip_host.setText(f"ipHost: {host}")
        self._network.setText(f"Network: {status}")
        self._task.setText(f"Task: {task_name if task_name else '—'}")
        self._info_summary.setText(
            f"{device} • {host} • {self._identity['hardware']} • {status}"
        )
        self._live_label.setText("LIVE" if network_connected else "IDLE")
        self._live_dot.setObjectName("liveDot" if network_connected else "idleDot")
        self.style().unpolish(self._live_dot)
        self.style().polish(self._live_dot)
        self._refresh_activity()

    def set_voltage(self, volts: float | None) -> None:
        self._voltage = volts
        if volts is None:
            self._voltage_value.setText("— V")
        else:
            self._voltage_value.setText(f"{volts:.2f} V")
        self._refresh_source()

    def set_battery_percent(self, percent: float | None) -> None:
        self._battery_percent = percent
        if percent is None:
            self._battery_value.setText("— %")
            self._battery_bar.setValue(0)
        else:
            clamped = max(0.0, min(100.0, percent))
            self._battery_value.setText(f"{clamped:.0f} %")
            self._battery_bar.setValue(int(round(clamped)))
        self._refresh_source()

    def _refresh_source(self) -> None:
        if self._voltage is None and self._battery_percent is None:
            self._source.setText(
                "Telemetry: waiting for platform data (voltage / battery %)"
            )
        else:
            self._source.setText("Telemetry: platform values updated")

    def _refresh_activity(self) -> None:
        note = self._status.latest_note()
        if note:
            self._activity_detail.setText(note)
        else:
            self._activity_detail.setText("Listener events and diagnostics")
