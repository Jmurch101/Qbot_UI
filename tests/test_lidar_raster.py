"""Lidar raster geometry for the Leishen M10P probe."""

from __future__ import annotations

import unittest

import numpy as np

from qbotui.frame_codec import FrameCodec


class LidarRasterTest(unittest.TestCase):
    def test_center_and_one_meter_at_angle_zero(self) -> None:
        points = np.zeros((210, 2), dtype=np.dtype("<f4"))
        points[0, 0] = 0.0
        points[0, 1] = 0.0
        points[1, 0] = 1.0
        points[1, 1] = 0.0
        canvas = FrameCodec().raster_lidar(points)
        self.assertEqual(canvas.shape, (400, 400))
        self.assertEqual(canvas.dtype, np.uint8)
        self.assertEqual(int(canvas[200, 200]), 255)
        self.assertEqual(int(canvas[150, 200]), 255)
        self.assertEqual(int(canvas[200, 150]), 0)
        self.assertEqual(int(canvas.sum()), 255 * 2)
