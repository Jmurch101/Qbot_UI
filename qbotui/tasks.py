"""Lab tasks bound to exact Quanser startup scripts and observer layouts."""

from __future__ import annotations

from dataclasses import dataclass

from qbotui.contract import ProbeStream
from qbotui.observers import ObserverCatalog, ObserverProfile

# Root of the Quanser tree on each QBot (Desktop/Quanser).
QUANSER_REMOTE_ROOT = "/home/nvidia/Desktop/Quanser"


@dataclass(frozen=True)
class TaskProfile:
    """One Connect target: Quanser observer windows + robot startup script."""

    key: str
    name: str
    observer: ObserverProfile
    startup_script: str
    resource_path: str
    remote_root: str = QUANSER_REMOTE_ROOT

    @property
    def remote_dir(self) -> str:
        if not self.resource_path or self.resource_path == ".":
            return self.remote_root.rstrip("/")
        return f"{self.remote_root.rstrip('/')}/{self.resource_path.strip('/')}"

    @property
    def stream_labels(self) -> tuple[str, ...]:
        return self.observer.stream_labels

    def streams(self) -> tuple[ProbeStream, ...]:
        return self.observer.streams()

    @property
    def window_count(self) -> int:
        return len(self.observer.panels)

    @property
    def remote_command(self) -> str:
        script = self.startup_script.replace("'", "'\"'\"'")
        directory = self.remote_dir.replace("'", "'\"'\"'")
        return (
            f"cd '{directory}' && "
            f"nohup python3 '{script}' > /tmp/qbotui_{self.key}.log 2>&1 & "
            f"echo $!"
        )


class TaskCatalog:
    """Tasks from the local Quanser/ tree that will ship on the QBots."""

    STARTUP = TaskProfile(
        key="startup",
        name="Startup",
        observer=ObserverCatalog.FULL,
        startup_script="quick_start_qbot_platform.py",
        resource_path=".",
    )
    PLAY = TaskProfile(
        key="play",
        name="Play",
        observer=ObserverCatalog.PLAY,
        startup_script="play.py",
        resource_path="6_teaching/3_Robotics/sp0_play/play_qbot/hardware/python",
    )
    FORWARD_KIN = TaskProfile(
        key="forward_kin",
        name="Forward kin.",
        observer=ObserverCatalog.FORWARD_KIN,
        startup_script="for_kin.py",
        resource_path=(
            "6_teaching/3_Robotics/sp1_task_automation/"
            "l1_forward_kinematics/hardware/python"
        ),
    )
    INVERSE_KIN = TaskProfile(
        key="inverse_kin",
        name="Inverse kin.",
        observer=ObserverCatalog.INVERSE_KIN,
        startup_script="inv_kin.py",
        resource_path=(
            "6_teaching/3_Robotics/sp1_task_automation/"
            "l2_inverse_kinematics/hardware/python"
        ),
    )
    LINE_FOLLOW = TaskProfile(
        key="line_follow",
        name="Line follow",
        observer=ObserverCatalog.LINE_FOLLOWING,
        startup_script="line_following.py",
        resource_path=(
            "6_teaching/3_Robotics/sp1_task_automation/"
            "l3_line_following/hardware/python"
        ),
    )
    OBJECT_DETECTION = TaskProfile(
        key="object_detection",
        name="Object detection",
        observer=ObserverCatalog.OBJECT_DETECTION,
        startup_script="obstacle_detection.py",
        resource_path=(
            "6_teaching/3_Robotics/sp1_task_automation/"
            "l4_object_detection/hardware/python"
        ),
    )

    ALL: tuple[TaskProfile, ...] = (
        STARTUP,
        PLAY,
        FORWARD_KIN,
        INVERSE_KIN,
        LINE_FOLLOW,
        OBJECT_DETECTION,
    )

    @classmethod
    def by_key(cls, key: str) -> TaskProfile:
        for task in cls.ALL:
            if task.key == key:
                return task
        raise KeyError(key)

    @classmethod
    def default(cls) -> TaskProfile:
        return cls.STARTUP
