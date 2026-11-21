"""Breakpoint helpers for the control-center layout."""

from __future__ import annotations

# Window width thresholds in pixels.
NARROW = 780
MEDIUM = 1100


def viewer_columns(width: int, feed_count: int) -> int:
    """How many mosaic columns to use for an equal square-style grid.

    Four camera feeds stay in a 2x2 square. Two feeds sit side-by-side.
    Only collapse to a single column when the WINDOWS cell is extremely narrow.
    """
    if feed_count <= 1:
        return 1
    if width < 360:
        return 1
    if feed_count <= 4:
        return 2
    if width >= MEDIUM and feed_count >= 6:
        return 3
    return 2


def stack_controls(width: int) -> bool:
    """True when task/devices and action buttons should stack vertically."""
    return width < NARROW
