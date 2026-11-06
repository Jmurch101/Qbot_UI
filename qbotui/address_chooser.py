"""Enumerated IPv4 rows. A row is chosen only by an operator gesture."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFocusEvent, QKeyEvent, QMouseEvent
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget


class AddressChooser(QListWidget):
    """Show interface rows and ignore a current item the operator did not choose."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._operator_chose = False

    @property
    def operator_chose(self) -> bool:
        return self._operator_chose

    def replace_rows(self, rows: list[tuple[str, str]]) -> None:
        self._operator_chose = False
        self.clear()
        for friendly_name, ipv4 in rows:
            item = QListWidgetItem(f"{friendly_name}    {ipv4}")
            item.setData(Qt.ItemDataRole.UserRole, ipv4)
            self.addItem(item)
        self.setCurrentRow(-1)
        self.clearSelection()
        self._operator_chose = False

    def chosen_address(self) -> str | None:
        if not self._operator_chose:
            return None
        item = self.currentItem()
        if item is None:
            return None
        value = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(value, str) or value == "":
            return None
        return value

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self._operator_chose = True
        super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        self._operator_chose = True
        super().keyPressEvent(event)

    def focusInEvent(self, event: QFocusEvent) -> None:
        had_choice = self._operator_chose
        super().focusInEvent(event)
        if had_choice:
            return
        self.setCurrentRow(-1)
        self.clearSelection()
        self._operator_chose = False
