"""Operator instructions for the selected task and SSH start path."""

from __future__ import annotations

from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget

from qbotui.tasks import TaskCatalog, TaskProfile


class Coach(QWidget):
    """Show task windows, startup script, and Connect order including SSH."""

    RULES = (
        "ipHost in the robot copy must be the PC address shown here.",
        "On the robot, ipDriver stays localhost.",
        "Do not start the task script on this Windows PC.",
        "Do not run the lab observer.py while this viewer is listening.",
        "Connect starts PC listeners, then starts the task script on the SSH device.",
        "Disconnect stops the PC listeners only. It does not stop the robot script.",
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._view = QPlainTextEdit()
        self._view.setObjectName("coachText")
        self._view.setReadOnly(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self._view)
        self._task = TaskCatalog.default()
        self._awaiting = False
        self._ssh_host: str | None = None
        self.set_ip_host(None)

    def set_task(self, task: TaskProfile) -> None:
        self._task = task
        self._refresh()

    def set_awaiting(self, awaiting: bool) -> None:
        self._awaiting = awaiting
        self._refresh()

    def set_ssh_host(self, host: str | None) -> None:
        self._ssh_host = host
        self._refresh()

    def set_ip_host(self, address: str | None) -> None:
        self._address = address
        self._refresh()

    def _refresh(self) -> None:
        shown = self._address if self._address else "(not confirmed)"
        ssh = self._ssh_host if self._ssh_host else "(enter SSH host)"
        task = self._task
        phase = (
            "Listeners are up. Task script was requested over SSH. Awaiting probe connections."
            if self._awaiting
            else "Select a task and SSH device, choose the PC IP, then press Connect."
        )
        steps = (
            "1. Choose a task. Window count, observer layout, and startup script follow the task.",
            "2. Enter the SSH host for the robot device you want to start.",
            "3. Choose the PC IPv4 that the robot will dial as ipHost.",
            "4. Connect starts listeners for this task's ports, then SSHs to run the startup script.",
            f"5. Remote command directory: {task.remote_dir}",
            f"6. Remote script: python3 {task.startup_script}",
            "7. Disconnect stops the PC listeners only.",
        )
        lines = [
            "Task startup",
            phase,
            "",
            f"Task: {task.name}",
            f"Observer: {task.observer.name}",
            f"Windows: {task.window_count}",
            f"Feeds: {', '.join(task.stream_labels)}",
            f"Startup script: {task.startup_script}",
            f"Quanser path: {task.resource_path}",
            f"Observer summary: {task.observer.summary}",
            f"SSH host: {ssh}",
            "",
            *steps,
            "",
            f"ipHost: {shown}",
            "",
            *self.RULES,
        ]
        self._view.setPlainText("\n".join(lines))
