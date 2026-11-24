"""Known QBot Platform devices on the lab LAN."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RobotProfile:
    """One physical QBot with its SSH address."""

    key: str
    name: str
    host: str

    @property
    def label(self) -> str:
        return f"{self.name}  ·  {self.host}"


class RobotCatalog:
    """The three lab QBots (IPs as used on Quanser_UVS)."""

    QBOT1 = RobotProfile(key="qbot1", name="QBot 1", host="192.168.2.145")
    QBOT2 = RobotProfile(key="qbot2", name="QBot 2", host="192.168.2.25")
    QBOT3 = RobotProfile(key="qbot3", name="QBot 3", host="192.168.2.128")

    ALL: tuple[RobotProfile, ...] = (QBOT1, QBOT2, QBOT3)

    @classmethod
    def by_key(cls, key: str) -> RobotProfile:
        for robot in cls.ALL:
            if robot.key == key:
                return robot
        raise KeyError(key)

    @classmethod
    def by_host(cls, host: str) -> RobotProfile | None:
        needle = host.strip()
        for robot in cls.ALL:
            if robot.host == needle:
                return robot
        return None
