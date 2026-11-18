"""Breakpoint helpers for the control-center layout."""

from __future__ import annotations

# Window width thresholds in pixels.
NARROW = 780
MEDIUM = 1100


def viewer_columns(width: int, feed_count: int) -> int:
    """How many mosaic columns to use for the current width and feed count."""
    if feed_count <= 1:
        return 1
    if width < NARROW:
        return 1
    if width < MEDIUM and feed_count >= 4:
        return 2
    if feed_count == 3 and width < 980:
        return 1
    return 2


def stack_controls(width: int) -> bool:
    """True when task/devices and action buttons should stack vertically."""
    return width < NARROW
