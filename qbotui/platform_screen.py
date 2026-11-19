"""Platform screen: observer windows, bash console, and platform health."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from qbotui.feed_workspace import FeedWorkspace
from qbotui.status_board import StatusBoard


def _metric_card(title: str) -> tuple[QFrame, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 14, 14, 14)
    layout.setSpacing(8)
    heading = QLabel(title)
    heading.setObjectName("sectionTitle")
    layout.addWidget(heading)
    return frame, layout


class PlatformScreen(QWidget):
    """Observer feeds plus bash console and voltage / battery monitoring."""

    def __init__(
        self,
        labels: list[str],
        workspace: FeedWorkspace,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("platformScreen")
        self._workspace = workspace

        title = QLabel("PLATFORM MONITORING")
        title.setObjectName("sectionTitle")
        subtitle = QLabel("Observer windows, bash console, and QBot platform health")
        subtitle.setObjectName("mutedLabel")

        header = QVBoxLayout()
        header.setSpacing(2)
        header.addWidget(title)
        header.addWidget(subtitle)

        self._status = StatusBoard(labels)
        self._status.setMinimumHeight(110)
        self._status.setMaximumHeight(180)
        self._status.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum
        )

        info_card, info_layout = _metric_card("PLATFORM INFO")
        info_card.setMaximumHeight(180)
        info_card.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum
        )
        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(10)

        self._voltage_value = QLabel("— V")
        self._voltage_value.setObjectName("metricValue")
        self._voltage_value.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._battery_value = QLabel("— %")
        self._battery_value.setObjectName("metricValue")
        self._battery_bar = QProgressBar()
        self._battery_bar.setObjectName("batteryBar")
        self._battery_bar.setRange(0, 100)
        self._battery_bar.setValue(0)
        self._battery_bar.setTextVisible(False)
        self._battery_bar.setMinimumHeight(14)

        self._device_name = QLabel("Device: —")
        self._device_name.setObjectName("mutedLabel")
        self._ip_host = QLabel("ipHost: —")
        self._ip_host.setObjectName("mutedLabel")
        self._network = QLabel("Network: disconnected")
        self._network.setObjectName("mutedLabel")
        self._task = QLabel("Task: —")
        self._task.setObjectName("mutedLabel")
        self._source = QLabel("Telemetry: waiting for platform data")
        self._source.setObjectName("mutedLabel")
        self._source.setWordWrap(True)

        volt_label = QLabel("BATTERY VOLTAGE")
        volt_label.setObjectName("sectionTitle")
        batt_label = QLabel("BATTERY CHARGE")
        batt_label.setObjectName("sectionTitle")

        grid.addWidget(volt_label, 0, 0)
        grid.addWidget(self._voltage_value, 1, 0)
        grid.addWidget(batt_label, 0, 1)
        grid.addWidget(self._battery_value, 1, 1)
        grid.addWidget(self._battery_bar, 2, 0, 1, 2)
        grid.addWidget(self._device_name, 3, 0, 1, 2)
        grid.addWidget(self._ip_host, 4, 0, 1, 2)
        grid.addWidget(self._network, 5, 0, 1, 2)
        grid.addWidget(self._task, 6, 0, 1, 2)
        grid.addWidget(self._source, 7, 0, 1, 2)
        info_layout.addLayout(grid)

        lower = QHBoxLayout()
        lower.setSpacing(12)
        lower.addWidget(self._status, 3)
        lower.addWidget(info_card, 2)

        self._workspace.setMinimumHeight(360)
        self._workspace.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addLayout(header, 0)
        layout.addWidget(self._workspace, 6)
        layout.addLayout(lower, 1)

        self._voltage: float | None = None
        self._battery_percent: float | None = None

    @property
    def status_board(self) -> StatusBoard:
        return self._status

    @property
    def workspace(self) -> FeedWorkspace:
        return self._workspace

    def set_labels(self, labels: list[str]) -> None:
        self._status.set_labels(labels)

    def show_note(self, text: str) -> None:
        self._status.show_note(text)

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
        self._device_name.setText(f"Device: {device}")
        self._ip_host.setText(f"ipHost: {host}")
        self._network.setText(
            "Network: connected" if network_connected else "Network: disconnected"
        )
        self._task.setText(f"Task: {task_name if task_name else '—'}")

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
