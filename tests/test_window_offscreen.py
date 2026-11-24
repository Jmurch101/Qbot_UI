"""Construct the main window without opening an interactive desktop session."""

from __future__ import annotations

import os
import unittest
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"


class OffscreenWindowTest(unittest.TestCase):
    def test_main_window_constructs(self) -> None:
        try:
            import PySide6
            from PySide6.QtWidgets import (
                QApplication,
                QComboBox,
                QLabel,
                QLineEdit,
                QPushButton,
            )
        except Exception as exc:
            self.skipTest(f"Qt offscreen platform is unavailable: {exc}")
        platforms = Path(PySide6.__file__).resolve().parent / "plugins" / "platforms"
        names = {path.name for path in platforms.glob("qoffscreen*")} if platforms.is_dir() else set()
        if not names:
            self.skipTest(f"Qt offscreen platform plugin is missing under {platforms}")
        try:
            app = QApplication.instance() or QApplication([])
        except Exception as exc:
            self.skipTest(f"Qt offscreen platform is unavailable: {exc}")
        if app.platformName() != "offscreen":
            self.skipTest(
                f"Qt platform is {app.platformName()!r}, not offscreen. "
                "Skipping window construct so a missing offscreen plugin does not fail the suite."
            )

        from qbotui.feed_tile import FeedTile
        from qbotui.main_window import QbotMainWindow
        from qbotui.platform_screen import PlatformScreen
        from qbotui.tasks import TaskCatalog

        window = QbotMainWindow()
        try:
            window.show()
            app.processEvents()
            self.assertEqual(len(window.findChildren(FeedTile)), 4)
            self.assertFalse(window._address_list.operator_chose)
            window._connect_session()
            self.assertIsNone(window._viewer.confirmed_address)
            self.assertFalse(window._viewer.listeners_active)
            self.assertEqual(window._address_list.currentIndex(), 0)
            host = window.findChild(QLabel, "ipHostLabel")
            self.assertIsNotNone(host)
            assert host is not None
            self.assertIn("ipHost", host.text().lower())
            device = window.findChild(QLabel, "deviceAddressLabel")
            self.assertIsNotNone(device)
            note = window.findChild(QLabel, "initStatusNote")
            self.assertIsNotNone(note)
            task_combo = window.findChild(QComboBox, "taskCombo")
            self.assertIsNotNone(task_combo)
            assert task_combo is not None
            self.assertEqual(task_combo.count(), len(TaskCatalog.ALL))
            robot_combo = window.findChild(QComboBox, "robotCombo")
            self.assertIsNotNone(robot_combo)
            assert robot_combo is not None
            from qbotui.robots import RobotCatalog

            self.assertEqual(robot_combo.count(), len(RobotCatalog.ALL) + 1)
            ssh_host = window.findChild(QLineEdit, "sshHostEdit")
            self.assertIsNotNone(ssh_host)
            assert ssh_host is not None
            robot_combo.setCurrentIndex(1)
            app.processEvents()
            self.assertEqual(ssh_host.text(), RobotCatalog.ALL[0].host)
            start = window.findChild(QPushButton, "startListenersButton")
            self.assertIsNotNone(start)
            assert start is not None
            self.assertIn("START", start.text())
            open_platform = window.findChild(QPushButton, "openPlatformButton")
            self.assertIsNotNone(open_platform)
            assert open_platform is not None
            self.assertIn("platform", open_platform.text().lower())
            confirm = window.findChild(QPushButton, "verifySshButton")
            self.assertIsNotNone(confirm)
            assert confirm is not None
            self.assertIn("laptop", confirm.text().lower())
            confirm.click()
            app.processEvents()
            assert note is not None
            self.assertTrue(len(note.text()) > 10)
            emergency = window.findChild(QPushButton, "emergencyDisconnectButton")
            self.assertIsNotNone(emergency)
            open_platform.click()
            app.processEvents()
            self.assertEqual(window._screens.currentIndex(), 1)
            self.assertIs(window._platform.workspace, window._workspace)
            self.assertEqual(
                window._platform.grid_layout.rowStretch(0),
                PlatformScreen.TOP_ROW_STRETCH,
            )
            self.assertEqual(
                window._platform.grid_layout.rowStretch(1),
                PlatformScreen.BOTTOM_ROW_STRETCH,
            )
            self.assertEqual(len(window.findChildren(FeedTile)), 4)
            window.set_platform_power(11.9, 64)
            self.assertEqual(window._platform._battery_bar.value(), 64)
            back = window.findChild(QPushButton, "backInitButton")
            self.assertIsNotNone(back)
            assert back is not None
            back.click()
            app.processEvents()
            self.assertEqual(window._screens.currentIndex(), 0)
            for button in window.findChildren(QPushButton):
                lowered = button.text().lower()
                self.assertNotIn("e-stop", lowered)

            line_index = next(
                i
                for i in range(task_combo.count())
                if task_combo.itemData(i) == TaskCatalog.LINE_FOLLOW.key
            )
            task_combo.setCurrentIndex(line_index)
            app.processEvents()
            self.assertEqual(len(window.findChildren(FeedTile)), 2)
            self.assertEqual(window._task.startup_script, "line_following.py")
            self.assertEqual(window._task.observer.key, "line_following")
        finally:
            window.close()
            app.processEvents()
