"""One labeled image pane. A placeholder stays until a full frame arrives."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class FeedTile(QWidget):
    """Title plus the latest full frame for one probe."""

    def __init__(self, label: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._label = label
        self.setObjectName(label)
        self._title = QLabel(label)
        self._title.setWordWrap(True)
        self._view = QLabel()
        self._view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._view.setMinimumSize(320, 180)
        self._view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._placeholder = self._build_placeholder()
        self._view.setPixmap(self._placeholder)
        layout = QVBoxLayout(self)
        layout.addWidget(self._title)
        layout.addWidget(self._view, 1)

    @property
    def label(self) -> str:
        return self._label

    def set_detail(self, text: str) -> None:
        if text:
            self._title.setText(f"{self._label}\n{text}")
        else:
            self._title.setText(self._label)

    def show_frame(self, image: QImage) -> None:
        pixmap = QPixmap.fromImage(image)
        target = self._view.size()
        if target.width() < 32 or target.height() < 32:
            target = self._view.minimumSize()
        self._view.setPixmap(
            pixmap.scaled(
                target,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation,
            )
        )

    def _build_placeholder(self) -> QPixmap:
        pixmap = QPixmap(320, 180)
        pixmap.fill(QColor(30, 30, 30))
        painter = QPainter(pixmap)
        painter.setPen(QColor(210, 210, 210))
        painter.drawText(
            pixmap.rect(),
            Qt.AlignmentFlag.AlignCenter,
            "Waiting for a full frame",
        )
        painter.end()
        return pixmap
