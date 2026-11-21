"""Observer layouts matched exactly to Quanser/*/hardware/python/observer.py."""

from __future__ import annotations

from dataclasses import dataclass

from qbotui.contract import ProbeContract, ProbeStream


@dataclass(frozen=True)
class ObserverPanel:
    """One observer window. Optional stream binds a PC listener port."""

    label: str
    stream: ProbeStream | None = None


@dataclass(frozen=True)
class ObserverProfile:
    """Window set for one lab observer.py."""

    key: str
    name: str
    panels: tuple[ObserverPanel, ...]
    summary: str
    observer_script: str

    @property
    def stream_labels(self) -> tuple[str, ...]:
        return tuple(panel.label for panel in self.panels)

    def streams(self) -> tuple[ProbeStream, ...]:
        return tuple(panel.stream for panel in self.panels if panel.stream is not None)

    def panel_for_stream(self, stream_label: str) -> ObserverPanel | None:
        for panel in self.panels:
            if panel.stream is not None and panel.stream.label == stream_label:
                return panel
            if panel.label == stream_label:
                return panel
        return None


class ObserverCatalog:
    """Layouts from Quanser SP0 play_qbot and SP1 task-automation observers."""

    FULL = ObserverProfile(
        key="full",
        name="Full Platform",
        panels=(
            ObserverPanel("Downward Facing Image", ProbeContract.DOWNWARD),
            ObserverPanel("RealSense RGB Image", ProbeContract.RGB),
            ObserverPanel("RealSense Depth Image", ProbeContract.DEPTH),
            ObserverPanel("Leishen M10P Lidar", ProbeContract.LIDAR),
        ),
        summary="quick_start_qbot_platform.py probes (no separate observer.py).",
        observer_script="(embedded in Qbot UI / quick_start probes)",
    )
    PLAY = ObserverProfile(
        key="play",
        name="Play Observer",
        panels=(
            ObserverPanel("RealSense RGB Image", ProbeContract.PLAY_RGB),
        ),
        summary="sp0_play/play_qbot observer: RealSense RGB on 18801.",
        observer_script=(
            "6_teaching/3_Robotics/sp0_play/play_qbot/hardware/python/observer.py"
        ),
    )
    FORWARD_KIN = ObserverProfile(
        key="forward_kin",
        name="Forward Kinematics Observer",
        panels=(
            ObserverPanel("Motor Speed Plot", ProbeContract.MOTOR_SCOPE),
            ObserverPanel("Body Speed Plot", ProbeContract.BODY_SCOPE),
            ObserverPanel("Downward Facing Raw", ProbeContract.KIN_RAW),
        ),
        summary="l1_forward_kinematics observer: two scopes + downward raw.",
        observer_script=(
            "6_teaching/3_Robotics/sp1_task_automation/"
            "l1_forward_kinematics/hardware/python/observer.py"
        ),
    )
    INVERSE_KIN = ObserverProfile(
        key="inverse_kin",
        name="Inverse Kinematics Observer",
        panels=(
            ObserverPanel("Motor Speed Plot", ProbeContract.MOTOR_SCOPE),
            ObserverPanel("Body Speed Plot", ProbeContract.BODY_SCOPE),
            ObserverPanel("Downward Facing Raw", ProbeContract.KIN_RAW),
        ),
        summary="l2_inverse_kinematics observer: two scopes + downward raw.",
        observer_script=(
            "6_teaching/3_Robotics/sp1_task_automation/"
            "l2_inverse_kinematics/hardware/python/observer.py"
        ),
    )
    LINE_FOLLOWING = ObserverProfile(
        key="line_following",
        name="Line Following Observer",
        panels=(
            ObserverPanel("Downward Facing Raw", ProbeContract.LINE_RAW),
            ObserverPanel("Downward Facing Binary", ProbeContract.LINE_BINARY),
        ),
        summary="l3_line_following observer: raw + binary downward images.",
        observer_script=(
            "6_teaching/3_Robotics/sp1_task_automation/"
            "l3_line_following/hardware/python/observer.py"
        ),
    )
    OBJECT_DETECTION = ObserverProfile(
        key="object_detection",
        name="Object Detection Observer",
        panels=(
            ObserverPanel("Leishen M10P Lidar", ProbeContract.OD_LIDAR),
            ObserverPanel("Plotting", ProbeContract.OD_PLOT),
        ),
        summary="l4_object_detection observer: raw lidar + plotting lidar.",
        observer_script=(
            "6_teaching/3_Robotics/sp1_task_automation/"
            "l4_object_detection/hardware/python/observer.py"
        ),
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
