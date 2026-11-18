"""Observer layouts matched to Quanser SP0 Play and SP1 Task Automation labs."""

from __future__ import annotations

from dataclasses import dataclass

from qbotui.contract import ProbeContract, ProbeStream


@dataclass(frozen=True)
class ObserverPanel:
    """One observer window. Optional stream binds a known PC listener port."""

    label: str
    stream: ProbeStream | None = None


@dataclass(frozen=True)
class ObserverProfile:
    """Window set for one lab observer.py."""

    key: str
    name: str
    panels: tuple[ObserverPanel, ...]
    summary: str

    @property
    def stream_labels(self) -> tuple[str, ...]:
        return tuple(panel.label for panel in self.panels)

    def streams(self) -> tuple[ProbeStream, ...]:
        return tuple(panel.stream for panel in self.panels if panel.stream is not None)

    def panel_for_stream(self, stream_label: str) -> ObserverPanel | None:
        for panel in self.panels:
            if panel.stream is not None and panel.stream.label == stream_label:
                return panel
        return None


class ObserverCatalog:
    """Layouts from Quanser_Academic_Resources play_qbot and sp1_task_automation."""

    FULL = ObserverProfile(
        key="full",
        name="Full Platform",
        panels=(
            ObserverPanel("Downward Facing Image", ProbeContract.DOWNWARD),
            ObserverPanel("RealSense RGB Image", ProbeContract.RGB),
            ObserverPanel("RealSense Depth Image", ProbeContract.DEPTH),
            ObserverPanel("Leishen M10P Lidar", ProbeContract.LIDAR),
        ),
        summary="Startup quick-start: four probe windows.",
    )
    PLAY = ObserverProfile(
        key="play",
        name="Play Observer",
        panels=(
            ObserverPanel("RealSense RGB Image", ProbeContract.RGB),
        ),
        summary="SP0 play_qbot observer: RealSense RGB only.",
    )
    FORWARD_KIN = ObserverProfile(
        key="forward_kin",
        name="Forward Kinematics Observer",
        panels=(
            ObserverPanel("Motor Speed Plot"),
            ObserverPanel("Body Speed Plot"),
            ObserverPanel("Downward Facing Raw", ProbeContract.DOWNWARD),
        ),
        summary="SP1 lab 1 observer: two scopes and downward camera.",
    )
    INVERSE_KIN = ObserverProfile(
        key="inverse_kin",
        name="Inverse Kinematics Observer",
        panels=(
            ObserverPanel("Motor Speed Plot"),
            ObserverPanel("Body Speed Plot"),
            ObserverPanel("Downward Facing Raw", ProbeContract.DOWNWARD),
        ),
        summary="SP1 lab 2 observer: two scopes and downward camera.",
    )
    LINE_FOLLOWING = ObserverProfile(
        key="line_following",
        name="Line Following Observer",
        panels=(
            ObserverPanel("Downward Facing Raw", ProbeContract.DOWNWARD),
            ObserverPanel("Downward Facing Binary"),
        ),
        summary="SP1 lab 3 observer: raw and binary downward images.",
    )
    OBJECT_DETECTION = ObserverProfile(
        key="object_detection",
        name="Object Detection Observer",
        panels=(
            ObserverPanel("Leishen M10P Lidar", ProbeContract.LIDAR),
            ObserverPanel("Plotting"),
        ),
        summary="SP1 lab 4 observer: raw lidar and processed lidar plot.",
    )

    ALL: tuple[ObserverProfile, ...] = (
        FULL,
        PLAY,
        FORWARD_KIN,
        INVERSE_KIN,
        LINE_FOLLOWING,
        OBJECT_DETECTION,
    )

    @classmethod
    def by_key(cls, key: str) -> ObserverProfile:
        for profile in cls.ALL:
            if profile.key == key:
                return profile
        raise KeyError(key)
