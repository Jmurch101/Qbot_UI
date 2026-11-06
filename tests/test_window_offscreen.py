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
            from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QTextEdit
        except Exception as exc:
            self.skipTest(f"Qt offscreen platform is unavailable: {exc}")
        plugin = Path(PySide6.__file__).resolve().parent / "plugins" / "platforms" / "qoffscreen.dll"
        if not plugin.is_file():
            self.skipTest(f"Qt offscreen platform plugin is missing: {plugin}")
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

        window = QbotMainWindow()
        try:
            window.show()
            app.processEvents()
            self.assertEqual(len(window.findChildren(FeedTile)), 4)
            self.assertFalse(window._address_list.operator_chose)
            window._confirm_address()
            self.assertIsNone(window._viewer.confirmed_address)
            self.assertFalse(window._viewer.listeners_active)
            self.assertIsNone(window._address_list.currentItem())
            host = window.findChild(QLabel, "ipHostLabel")
            self.assertIsNotNone(host)
            assert host is not None
            self.assertTrue(host.text().startswith("ipHost:"))
            scope = window.findChild(QLabel, "stopScopeLabel")
            self.assertIsNotNone(scope)
            assert scope is not None
            self.assertEqual(scope.text(), "This stops the PC viewer servers only.")
            stop_buttons = [
                button for button in window.findChildren(QPushButton) if button.text() == "Stop"
            ]
            self.assertEqual(len(stop_buttons), 1)
            for button in window.findChildren(QPushButton):
                lowered = button.text().lower()
                self.assertNotIn("e-stop", lowered)
                self.assertNotIn("emergency", lowered)
            checklist = window.findChild(QTextEdit, "safetyText")
            self.assertIsNotNone(checklist)
            assert checklist is not None
            text = checklist.toPlainText()
            self.assertIn("The floor is clear.", text)
            self.assertIn("Closing this window does not disarm the robot.", text)
            self.assertIn("The robot script stops its own loop at 90 seconds.", text)
        finally:
            window.close()
            app.processEvents()
