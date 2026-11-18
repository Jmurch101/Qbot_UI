"""Responsive breakpoint helpers for mosaic columns and stacked controls."""

from __future__ import annotations

import unittest

from qbotui.responsive import stack_controls, viewer_columns


class ResponsiveLayoutTest(unittest.TestCase):
    def test_viewer_columns_by_width_and_count(self) -> None:
        self.assertEqual(viewer_columns(1400, 4), 2)
        self.assertEqual(viewer_columns(1400, 1), 1)
        self.assertEqual(viewer_columns(700, 4), 1)
        self.assertEqual(viewer_columns(700, 2), 1)
        self.assertEqual(viewer_columns(1000, 4), 2)
        self.assertEqual(viewer_columns(900, 3), 1)

    def test_controls_stack_when_narrow(self) -> None:
        self.assertFalse(stack_controls(1280))
        self.assertTrue(stack_controls(700))
