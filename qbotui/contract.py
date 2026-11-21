"""Probe streams sized and ported to match Quanser/observer.py + robot scripts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProbeStream:
    """One raw TCP probe: label, port, and the exact payload size."""

    label: str
    port: int
    byte_count: int
    kind: str
    shape: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.kind == "lidar":
            rows = self.shape[0]
            expected = rows * 2 * 4
        elif self.kind in ("gray", "bgr", "depth"):
            expected = 1
            for axis in self.shape:
                expected *= axis
        elif self.kind == "scope":
            # float64 timestamp + numSignals values
            expected = self.shape[0] * 8
        else:
            raise ValueError(f"unknown probe kind {self.kind}")
        if self.byte_count != expected:
            raise ValueError(
                f"{self.label} byte count {self.byte_count} does not match {expected}"
            )


class ProbeContract:
    """Streams derived from Quanser observer.py / Probe port rules.

    Displays use 18800+n, plots 18600+n, scopes 18700+n (1-based n in each class).
    Image sizes are post-scalingFactor buffers (what the PC actually receives).
    """

    # --- Startup / quick_start_qbot_platform.py (4 agents) ---
    DOWNWARD = ProbeStream(
        "Downward Facing Image",
        18801,
        64000,
        "gray",
        (200, 320, 1),  # [400,640,1] / scalingFactor 2
    )
    RGB = ProbeStream(
        "RealSense RGB Image",
        18802,
        230400,
        "bgr",
        (240, 320, 3),  # [480,640,3] / 2
    )
    DEPTH = ProbeStream(
        "RealSense Depth Image",
        18803,
        76800,
        "depth",
        (240, 320, 1),  # [480,640,1] / 2
    )
    LIDAR = ProbeStream(
        "Leishen M10P Lidar",
        18601,
        1680,
        "lidar",
        (210, 2),  # 1680 measurements / scalingFactor 8
    )

    # --- SP0 play observer: RGB is the first (only) display → 18801 ---
    PLAY_RGB = ProbeStream(
        "RealSense RGB Image",
        18801,
        230400,
        "bgr",
        (240, 320, 3),
    )

    # --- SP1 l1/l2: scopes then downward display ---
    MOTOR_SCOPE = ProbeStream(
        "Motor Speed Plot",
        18701,
        40,
        "scope",
        (5,),  # timestamp + 4 signals
    )
    BODY_SCOPE = ProbeStream(
        "Body Speed Plot",
        18702,
        32,
        "scope",
        (4,),  # timestamp + 3 signals
    )
    KIN_RAW = ProbeStream(
        "Downward Facing Raw",
        18801,
        16000,
        "gray",
        (100, 160, 1),  # [200,320,1] / 2
    )

    # --- SP1 l3 line following ---
    LINE_RAW = ProbeStream(
        "Downward Facing Raw",
        18801,
        16000,
        "gray",
        (100, 160, 1),  # [200,320,1] / 2
    )
    LINE_BINARY = ProbeStream(
        "Downward Facing Binary",
        18802,
        16000,
        "gray",
        (50, 320, 1),  # scalingFactor 1
    )

    # --- SP1 l4 object detection ---
    OD_LIDAR = ProbeStream(
        "Leishen M10P Lidar",
        18601,
        3360,
        "lidar",
        (420, 2),  # 1680 / scalingFactor 4
    )
    OD_PLOT = ProbeStream(
        "Plotting",
        18602,
        3280,
        "lidar",
        (410, 2),  # scalingFactor 1
    )

    STREAMS: tuple[ProbeStream, ...] = (DOWNWARD, RGB, DEPTH, LIDAR)

    ALL_STREAMS: tuple[ProbeStream, ...] = (
        DOWNWARD,
        RGB,
        DEPTH,
        LIDAR,
        PLAY_RGB,
        MOTOR_SCOPE,
        BODY_SCOPE,
        KIN_RAW,
        LINE_RAW,
        LINE_BINARY,
        OD_LIDAR,
        OD_PLOT,
    )

    @classmethod
    def ports(cls) -> frozenset[int]:
        return frozenset(stream.port for stream in cls.ALL_STREAMS)
