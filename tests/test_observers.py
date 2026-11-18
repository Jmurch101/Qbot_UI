"""Observer layouts match Quanser SP0/SP1 lab observer window counts."""

from __future__ import annotations

import unittest

from qbotui.observers import ObserverCatalog


class ObserverCatalogTest(unittest.TestCase):
    def test_observers_match_lab_window_counts(self) -> None:
        counts = {profile.key: len(profile.panels) for profile in ObserverCatalog.ALL}
        self.assertEqual(counts["full"], 4)
        self.assertEqual(counts["play"], 1)
        self.assertEqual(counts["forward_kin"], 3)
        self.assertEqual(counts["inverse_kin"], 3)
        self.assertEqual(counts["line_following"], 2)
        self.assertEqual(counts["object_detection"], 2)
        play = ObserverCatalog.PLAY
        self.assertEqual(
            [panel.label for panel in play.panels],
            ["RealSense RGB Image"],
        )
        line = ObserverCatalog.LINE_FOLLOWING
        self.assertEqual(
            [panel.label for panel in line.panels],
            ["Downward Facing Raw", "Downward Facing Binary"],
        )
