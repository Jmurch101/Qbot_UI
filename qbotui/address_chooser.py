"""Enumerated IPv4 rows in a dropdown. A row is chosen only by an operator gesture."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFocusEvent, QKeyEvent, QMouseEvent
from PySide6.QtWidgets import QComboBox, QWidget


class AddressChooser(QComboBox):
    """Show interface rows and ignore a current item the operator did not choose."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setEditable(False)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self._operator_chose = False
        self._rows: list[tuple[str, str]] = []
        self.activated.connect(self._mark_operator_chose)

    @property
    def operator_chose(self) -> bool:
        return self._operator_chose

    def replace_rows(self, rows: list[tuple[str, str]]) -> None:
        self._operator_chose = False
        self._rows = list(rows)
        self.blockSignals(True)
        self.clear()
        self.addItem("Select an IPv4 address…")
        self.setItemData(0, None)
        for friendly_name, ipv4 in rows:
            self.addItem(f"{friendly_name}    {ipv4}")
            self.setItemData(self.count() - 1, (friendly_name, ipv4), Qt.ItemDataRole.UserRole)
        self.setCurrentIndex(0)
        self.blockSignals(False)
        self._operator_chose = False

    def chosen_address(self) -> str | None:
        chosen = self.chosen_row()
        if chosen is None:
            return None
        return chosen[1]

    def chosen_row(self) -> tuple[str, str] | None:
        if not self._operator_chose:
            return None
        data = self.currentData(Qt.ItemDataRole.UserRole)
        if not isinstance(data, tuple) or len(data) != 2:
            return None
        friendly_name, ipv4 = data
        if not isinstance(friendly_name, str) or not isinstance(ipv4, str) or ipv4 == "":
            return None
        return friendly_name, ipv4

    def _mark_operator_chose(self, index: int) -> None:
        if index <= 0:
            self._operator_chose = False
            return
        self._operator_chose = True

    def mousePressEvent(self, event: QMouseEvent) -> None:
        super().mousePressEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        super().keyPressEvent(event)
        if self.currentIndex() > 0:
            self._operator_chose = True

    def focusInEvent(self, event: QFocusEvent) -> None:
        had_choice = self._operator_chose
        super().focusInEvent(event)
        if had_choice:
            return
        self.setCurrentIndex(0)
        self._operator_chose = False
