"""Platform monitoring screen shows voltage and battery metrics."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


class PlatformScreenTest(unittest.TestCase):
    def test_voltage_and_battery_update(self) -> None:
        try:
            from PySide6.QtWidgets import QApplication, QLabel, QProgressBar
        except Exception as exc:
            self.skipTest(f"Qt unavailable: {exc}")
        app = QApplication.instance() or QApplication([])
        if app.platformName() != "offscreen":
            self.skipTest(f"Qt platform is {app.platformName()!r}, not offscreen")

        from qbotui.feed_workspace import FeedWorkspace
        from qbotui.platform_screen import PlatformScreen

        workspace = FeedWorkspace()
        screen = PlatformScreen(["Downward Facing Image"], workspace)
        self.assertIs(screen.workspace, workspace)
        screen.set_voltage(12.4)
        screen.set_battery_percent(78)
        screen.set_platform_identity(
            device_name="QBot-01",
            ip_host="10.0.0.8",
            network_connected=True,
            task_name="Startup",
        )
        voltage = screen.findChild(QLabel, "metricValue")
        self.assertIsNotNone(voltage)
        values = [label.text() for label in screen.findChildren(QLabel) if label.objectName() == "metricValue"]
        self.assertIn("12.40 V", values)
        self.assertIn("78 %", values)
        bar = screen.findChild(QProgressBar, "batteryBar")
        self.assertIsNotNone(bar)
        assert bar is not None
        self.assertEqual(bar.value(), 78)
