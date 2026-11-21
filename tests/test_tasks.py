"""Tasks expose Quanser SP0/SP1 scripts, observers, and window counts."""

from __future__ import annotations

import unittest
from pathlib import Path

from qbotui.tasks import QUANSER_REMOTE_ROOT, TaskCatalog


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

    def test_remote_command_targets_quanser_lab_folder(self) -> None:
        task = TaskCatalog.PLAY
        command = task.remote_command
        self.assertIn(QUANSER_REMOTE_ROOT, command)
        self.assertIn("play_qbot/hardware/python", command)
        self.assertIn("play.py", command)
        self.assertIn("python3", command)
        startup = TaskCatalog.STARTUP
        self.assertEqual(startup.remote_dir, QUANSER_REMOTE_ROOT)
        self.assertIn("quick_start_qbot_platform.py", startup.remote_command)

    def test_local_quanser_scripts_exist(self) -> None:
        root = Path(__file__).resolve().parents[1] / "Quanser"
        self.assertTrue((root / "quick_start_qbot_platform.py").is_file())
        for task in TaskCatalog.ALL:
            if task.key == "startup":
                script = root / task.startup_script
            else:
                script = root / task.resource_path / task.startup_script
            self.assertTrue(script.is_file(), msg=f"missing {script}")
            if task.observer.observer_script.startswith("6_teaching"):
                observer = root / task.observer.observer_script
                self.assertTrue(observer.is_file(), msg=f"missing {observer}")
