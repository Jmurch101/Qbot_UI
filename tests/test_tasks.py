"""Tasks expose Quanser SP0/SP1 scripts, observers, and window counts."""

from __future__ import annotations

import unittest

from qbotui.tasks import TaskCatalog


class TaskCatalogTest(unittest.TestCase):
    def test_named_tasks_match_quanser_labs(self) -> None:
        names = [task.name for task in TaskCatalog.ALL]
        self.assertEqual(
            names,
            [
                "Startup",
                "Play",
                "Forward kin.",
                "Inverse kin.",
                "Line follow",
                "Object detection",
            ],
        )
        by_key = {task.key: task for task in TaskCatalog.ALL}
        self.assertEqual(by_key["startup"].window_count, 4)
        self.assertEqual(by_key["startup"].startup_script, "quick_start_qbot_platform.py")
        self.assertEqual(by_key["play"].window_count, 1)
        self.assertEqual(by_key["play"].startup_script, "play.py")
        self.assertIn("play_qbot", by_key["play"].resource_path)
        self.assertEqual(by_key["forward_kin"].window_count, 3)
        self.assertEqual(by_key["forward_kin"].startup_script, "for_kin.py")
        self.assertEqual(by_key["inverse_kin"].window_count, 3)
        self.assertEqual(by_key["inverse_kin"].startup_script, "inv_kin.py")
        self.assertEqual(by_key["line_follow"].window_count, 2)
        self.assertEqual(by_key["line_follow"].startup_script, "line_following.py")
        self.assertIn("l3_line_following", by_key["line_follow"].resource_path)
        self.assertEqual(by_key["object_detection"].window_count, 2)
        self.assertEqual(by_key["object_detection"].startup_script, "obstacle_detection.py")
        scripts = {task.startup_script for task in TaskCatalog.ALL}
        self.assertEqual(len(scripts), len(TaskCatalog.ALL))

    def test_remote_command_targets_desktop_script(self) -> None:
        task = TaskCatalog.PLAY
        command = task.remote_command
        self.assertIn("/home/nvidia/Desktop", command)
        self.assertIn("play.py", command)
        self.assertIn("python3", command)
