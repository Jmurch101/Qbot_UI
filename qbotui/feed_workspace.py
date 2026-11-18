"""Feed display that toggles mosaic vs separate windows and reflows with size."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCloseEvent, QImage, QResizeEvent
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from qbotui.feed_tile import FeedTile
from qbotui.observers import ObserverProfile
from qbotui.responsive import viewer_columns


class _DetachedFeedWindow(QMainWindow):
    """One probe feed in its own top-level window."""

    closed = Signal(str)

    def __init__(self, tile: FeedTile) -> None:
        super().__init__()
        self._label = tile.label
        self.setWindowTitle(tile.label)
        self.resize(520, 360)
        host = QWidget()
        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(tile)
        self.setCentralWidget(host)

    @property
    def feed_label(self) -> str:
        return self._label

    def closeEvent(self, event: QCloseEvent) -> None:
        self.closed.emit(self._label)
        event.accept()


class FeedWorkspace(QWidget):
    """Holds observer feeds; mosaic columns change with window width."""

    MODE_MOSAIC = "mosaic"
    MODE_WINDOWS = "windows"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._mode = self.MODE_MOSAIC
        self._feeds: dict[str, FeedTile] = {}
        self._detached: dict[str, _DetachedFeedWindow] = {}
        self._columns = 2
        self._host_width = 1280

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 14, 14, 14)
        card_layout.setSpacing(10)

        title = QLabel("CAMERA VIEWERS")
        title.setObjectName("sectionTitle")
        self._toggle = QPushButton("Separate windows")
        self._toggle.setObjectName("windowModeButton")
        self._toggle.clicked.connect(self.toggle_mode)
        header = QHBoxLayout()
        header.addWidget(title, 1)
        header.addWidget(self._toggle)

        self._grid_host = QWidget()
        self._grid = QGridLayout(self._grid_host)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(10)

        card_layout.addLayout(header)
        card_layout.addWidget(self._grid_host, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(card)

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def feeds(self) -> dict[str, FeedTile]:
        return self._feeds

    def apply_observer(self, profile: ObserverProfile) -> None:
        self._close_detached()
        while self._grid.count():
            item = self._grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        for tile in self._feeds.values():
            tile.deleteLater()
        self._feeds = {}
        for index, panel in enumerate(profile.panels, start=1):
            self._feeds[panel.label] = FeedTile(panel.label, index=index)
        self._relayout(force=True)

    def show_frame(self, label: str, image: QImage) -> None:
        tile = self._feeds.get(label)
        if tile is not None:
            tile.show_frame(image)

    def set_detail(self, label: str, text: str) -> None:
        tile = self._feeds.get(label)
        if tile is not None:
            tile.set_detail(text)

    def set_host_width(self, width: int) -> None:
        self._host_width = max(width, 1)
        if self._mode == self.MODE_MOSAIC:
            self._relayout()

    def toggle_mode(self) -> None:
        if self._mode == self.MODE_MOSAIC:
            self.set_mode(self.MODE_WINDOWS)
        else:
            self.set_mode(self.MODE_MOSAIC)

    def set_mode(self, mode: str) -> None:
        if mode not in (self.MODE_MOSAIC, self.MODE_WINDOWS):
            raise ValueError(mode)
        if mode == self._mode and (
            (mode == self.MODE_MOSAIC and not self._detached)
            or (mode == self.MODE_WINDOWS and len(self._detached) == len(self._feeds))
        ):
            return
        self._mode = mode
        self._relayout(force=True)

    def shutdown(self) -> None:
        self._close_detached()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self.set_host_width(event.size().width())

    def _relayout(self, force: bool = False) -> None:
        labels = list(self._feeds.keys())
        if self._mode == self.MODE_MOSAIC:
            columns = viewer_columns(self._host_width, len(labels))
            if not force and columns == self._columns and self._grid.count() == len(labels):
                return
            self._columns = columns

        self._close_detached()
        while self._grid.count():
            item = self._grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        for column in range(4):
            self._grid.setColumnStretch(column, 0)
        for row in range(8):
            self._grid.setRowStretch(row, 0)

        if self._mode == self.MODE_MOSAIC:
            self._toggle.setText("Separate windows")
            columns = self._columns
            for index, label in enumerate(labels):
                tile = self._feeds[label]
                tile.setParent(self._grid_host)
                self._grid.addWidget(tile, index // columns, index % columns)
            for column in range(max(columns, 1)):
                self._grid.setColumnStretch(column, 1)
            rows = max((len(labels) + columns - 1) // columns, 1) if labels else 1
            for row in range(rows):
                self._grid.setRowStretch(row, 1)
            return

        self._toggle.setText("Mosaic")
        hint = QLabel("Feeds opened in separate windows.")
        hint.setObjectName("mutedLabel")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._grid.addWidget(hint, 0, 0)
        self._grid.setColumnStretch(0, 1)
        self._grid.setRowStretch(0, 1)
        for label, tile in self._feeds.items():
            window = _DetachedFeedWindow(tile)
            window.closed.connect(self._on_detached_closed)
            self._detached[label] = window
            window.show()

    def _on_detached_closed(self, label: str) -> None:
        window = self._detached.pop(label, None)
        tile = self._feeds.get(label)
        if tile is not None:
            tile.setParent(None)
        if window is not None:
            window.deleteLater()

    def _close_detached(self) -> None:
        for label, window in list(self._detached.items()):
            window.closed.disconnect(self._on_detached_closed)
            tile = self._feeds.get(label)
            if tile is not None:
                tile.setParent(None)
            window.close()
            window.deleteLater()
        self._detached.clear()
