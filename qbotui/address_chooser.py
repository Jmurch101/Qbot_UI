"""Enumerated IPv4 rows in a dropdown; also accepts a typed address."""

from __future__ import annotations

import ipaddress

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QWidget


class AddressChooser(QComboBox):
    """Show interface rows and allow typing a laptop IPv4 when needed."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.lineEdit().setPlaceholderText("Select or type this laptop’s 192.168.2.x IP")
        self._operator_chose = False
        self._rows: list[tuple[str, str]] = []
        self.activated.connect(self._mark_operator_chose)
        self.currentIndexChanged.connect(self._on_index_changed)
        self.editTextChanged.connect(self._on_edit_text_changed)

    @property
    def operator_chose(self) -> bool:
        return self._operator_chose

    def replace_rows(self, rows: list[tuple[str, str]]) -> None:
        previous = self.chosen_address()
        self._operator_chose = False
        self._rows = list(rows)
        self.blockSignals(True)
        self.clear()
        self.addItem("Select or type this laptop’s IP…")
        self.setItemData(0, None)
        for friendly_name, ipv4 in rows:
            self.addItem(f"{friendly_name}    {ipv4}")
            self.setItemData(self.count() - 1, (friendly_name, ipv4), Qt.ItemDataRole.UserRole)
        restored = False
        if previous:
            for index in range(1, self.count()):
                data = self.itemData(index, Qt.ItemDataRole.UserRole)
                if isinstance(data, tuple) and data[1] == previous:
                    self.setCurrentIndex(index)
                    self._operator_chose = True
                    restored = True
                    break
            if not restored:
                self.setEditText(previous)
                self._operator_chose = True
                restored = True
        if not restored:
            self.setCurrentIndex(0)
            self.setEditText("")
        self.blockSignals(False)

    def chosen_address(self) -> str | None:
        chosen = self.chosen_row()
        if chosen is None:
            return None
        return chosen[1]

    def chosen_row(self) -> tuple[str, str] | None:
        data = self.currentData(Qt.ItemDataRole.UserRole)
        if isinstance(data, tuple) and len(data) == 2 and self.currentIndex() > 0:
            friendly_name, ipv4 = data
            if isinstance(friendly_name, str) and isinstance(ipv4, str) and ipv4:
                self._operator_chose = True
                return friendly_name, ipv4

        typed = self._typed_ipv4()
        if typed is not None:
            self._operator_chose = True
            return "Manual", typed

        if not self._operator_chose:
            return None
        return None

    def _typed_ipv4(self) -> str | None:
        text = self.currentText().strip()
        if not text or text.startswith("Select"):
            return None
        # Allow "en0    192.168.2.10" paste/display forms.
        candidate = text.split()[-1]
        try:
            return str(ipaddress.IPv4Address(candidate))
        except ipaddress.AddressValueError:
            return None

    def _mark_operator_chose(self, index: int) -> None:
        if index <= 0:
            self._operator_chose = self._typed_ipv4() is not None
            return
        self._operator_chose = True

    def _on_index_changed(self, index: int) -> None:
        if index > 0:
            self._operator_chose = True

    def _on_edit_text_changed(self, _text: str) -> None:
        if self._typed_ipv4() is not None:
            self._operator_chose = True
