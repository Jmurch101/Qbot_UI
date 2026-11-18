"""Console-style status output for the control center."""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPlainTextEdit, QVBoxLayout, QWidget


class StatusBoard(QWidget):
    """Bash-style console that shows notes and listener state."""

    def __init__(self, labels: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        card = QFrame()
        card.setObjectName("consoleCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        header = QHBoxLayout()
        title = QLabel("BASH / COMMAND CONSOLE")
        title.setObjectName("sectionTitle")
        ready = QLabel("READY")
        ready.setObjectName("liveBadge")
        header.addWidget(title, 1)
        header.addWidget(ready)

        self._console = QPlainTextEdit()
        self._console.setObjectName("consoleOutput")
        self._console.setReadOnly(True)
        self._console.setMaximumBlockCount(200)
        self._console.setMinimumHeight(90)

        self._note = ""
        self._rows: dict[str, str] = {}
        self._states: dict[str, str] = {}
        self._activity: dict[str, str] = {}
        self._labels: list[str] = []

        layout.addLayout(header)
        layout.addWidget(self._console)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(card)
        self.set_labels(labels)

    def set_labels(self, labels: list[str]) -> None:
        self._labels = list(labels)
        kept_states = {label: self._states[label] for label in labels if label in self._states}
        kept_activity = {
            label: self._activity[label] for label in labels if label in self._activity
        }
        self._states = kept_states
        self._activity = kept_activity
        self._rows = {label: f"{label}: stopped" for label in labels}
        for label in labels:
            self._render(label)
        self._refresh_console()

    def set_state(self, label: str, state: str) -> None:
        if label not in self._rows:
            return
        self._states[label] = state
        self._render(label)
        self._refresh_console()

    def set_activity(self, label: str, text: str) -> None:
        if label not in self._rows:
            return
        self._activity[label] = text
        self._render(label)
        self._refresh_console()

    def _render(self, label: str) -> None:
        state = self._states.get(label, "stopped")
        extra = self._activity.get(label, "")
        if extra:
            self._rows[label] = f"{label}: {state} — {extra}"
        else:
            self._rows[label] = f"{label}: {state}"

    def show_note(self, text: str) -> None:
        self._note = text
        self._refresh_console()

    def _refresh_console(self) -> None:
        note = self._note.strip() if self._note else "Waiting for command..."
        lines = [f"qbot@platform:~$ {note}"]
        for label in self._labels:
            lines.append(self._rows.get(label, f"{label}: stopped"))
        self._console.setPlainText("\n".join(lines))
        self._console.verticalScrollBar().setValue(self._console.verticalScrollBar().maximum())
