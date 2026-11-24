"""Lab QBot presets expose the three known SSH addresses."""

from __future__ import annotations

import unittest

from qbotui.robots import RobotCatalog


class RobotCatalogTest(unittest.TestCase):
    def test_three_qbots_on_lab_lan(self) -> None:
        self.assertEqual(len(RobotCatalog.ALL), 3)
        by_key = {robot.key: robot for robot in RobotCatalog.ALL}
        self.assertEqual(by_key["qbot1"].host, "192.168.2.145")
        self.assertEqual(by_key["qbot2"].host, "192.168.2.25")
        self.assertEqual(by_key["qbot3"].host, "192.168.2.128")
        self.assertEqual(by_key["qbot1"].name, "QBot 1")
        self.assertIn("192.168.2.25", by_key["qbot2"].label)

    def test_lookup_helpers(self) -> None:
        self.assertEqual(RobotCatalog.by_key("qbot3").name, "QBot 3")
        self.assertEqual(RobotCatalog.by_host("192.168.2.145"), RobotCatalog.QBOT1)
        self.assertIsNone(RobotCatalog.by_host("10.0.0.1"))
        with self.assertRaises(KeyError):
            RobotCatalog.by_key("missing")
