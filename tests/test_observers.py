"""Observer layouts match Quanser SP0/SP1 lab observer window counts and ports."""

from __future__ import annotations

import unittest

from qbotui.contract import ProbeContract
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
        self.assertEqual(play.streams()[0].port, 18801)
        self.assertEqual(play.streams()[0].byte_count, ProbeContract.PLAY_RGB.byte_count)
        line = ObserverCatalog.LINE_FOLLOWING
        self.assertEqual(
            [panel.label for panel in line.panels],
            ["Downward Facing Raw", "Downward Facing Binary"],
        )
        ports = [stream.port for stream in line.streams()]
        self.assertEqual(ports, [18801, 18802])
        self.assertEqual(line.streams()[0].shape, (100, 160, 1))
        self.assertEqual(line.streams()[1].shape, (50, 320, 1))
        od = ObserverCatalog.OBJECT_DETECTION
        self.assertEqual([stream.port for stream in od.streams()], [18601, 18602])
        kin = ObserverCatalog.FORWARD_KIN
        self.assertEqual(
            [stream.port for stream in kin.streams()],
            [18701, 18702, 18801],
        )
