"""Bash-style console for the Platform BASH cell."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class StatusBoard(QWidget):
    """Console that shows notes and listener state as bash output."""

    def __init__(self, labels: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._card = QFrame()
        self._card.setObjectName("consoleCard")
        layout = QVBoxLayout(self._card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        self._header = QWidget()
        header = QHBoxLayout(self._header)
        header.setContentsMargins(0, 0, 0, 0)
        self._title = QLabel("BASH")
        self._title.setObjectName("sectionTitle")
        self._ready = QLabel("READY")
        self._ready.setObjectName("liveBadge")
        header.addWidget(self._title, 1)
        header.addWidget(self._ready)

        self._console = QPlainTextEdit()
        self._console.setObjectName("consoleOutput")
        self._console.setReadOnly(True)
        self._console.setMaximumBlockCount(200)
        self._console.setMinimumHeight(48)
        self._console.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self._note = ""
        self._rows: dict[str, str] = {}
        self._states: dict[str, str] = {}
        self._activity: dict[str, str] = {}
        self._labels: list[str] = []

        layout.addWidget(self._header)
        layout.addWidget(self._console, 1)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._card)
        self.set_labels(labels)

    def set_title(self, title: str) -> None:
        self._title.setText(title)

    def set_chrome_compact(self, compact: bool) -> None:
        """When embedded under a section heading, hide the inner card chrome."""
        if compact:
            self._header.setVisible(False)
            self._card.setObjectName("consoleCardFlat")
            layout = self._card.layout()
            if layout is not None:
                layout.setContentsMargins(0, 0, 0, 0)
        else:
            self._header.setVisible(True)
            self._card.setObjectName("consoleCard")
        self.style().unpolish(self._card)
        self.style().polish(self._card)

    def latest_note(self) -> str:
        return self._note.strip()

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
