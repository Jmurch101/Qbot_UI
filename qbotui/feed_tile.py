"""One labeled image pane styled as a Platform WINDOWS cell."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPixmap, QResizeEvent
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget


class FeedTile(QWidget):
    """Compact camera viewport with a camera-icon placeholder."""

    def __init__(self, label: str, index: int = 1, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._label = label
        self._index = index
        self._last_image: QImage | None = None
        self.setObjectName("viewerCardHost")
        self.setMinimumSize(120, 90)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._frame = QWidget()
        self._frame.setObjectName("viewerCard")

        self._view = QLabel()
        self._view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._view.setMinimumSize(100, 70)
        self._view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._view.setToolTip(label)
        self._placeholder = self._build_placeholder()
        self._view.setPixmap(self._placeholder)

        inner = QVBoxLayout(self._frame)
        inner.setContentsMargins(6, 6, 6, 6)
        inner.setSpacing(0)
        inner.addWidget(self._view, 1)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._frame)

    @property
    def label(self) -> str:
        return self._label

    def set_detail(self, text: str) -> None:
        tip = f"{self._label} · {text}" if text else self._label
        self._view.setToolTip(tip)

    def show_frame(self, image: QImage) -> None:
        self._last_image = image.copy()
        self._paint_current()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._paint_current()

    def _paint_current(self) -> None:
        image = self._last_image
        if image is None:
            size = self._view.size()
            if size.width() >= 40 and size.height() >= 40:
                self._view.setPixmap(self._build_placeholder(size.width(), size.height()))
            else:
                self._view.setPixmap(self._placeholder)
            return
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

    def _build_placeholder(self, width: int = 240, height: int = 160) -> QPixmap:
        width = max(width, 80)
        height = max(height, 60)
        pixmap = QPixmap(width, height)
        pixmap.fill(QColor(8, 28, 56))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(90, 168, 255))
        pen.setWidth(2)
        painter.setPen(pen)
        cx, cy = width // 2, height // 2
        body_w, body_h = min(width, height) // 4, min(width, height) // 5
        painter.drawRoundedRect(cx - body_w, cy - body_h // 2, body_w * 2, body_h, 6, 6)
        lens = max(body_h // 2, 8)
        painter.drawEllipse(cx - lens // 2, cy - lens // 2, lens, lens)
        painter.drawEllipse(cx + body_w - 4, cy - body_h // 2 - 6, 10, 8)
        painter.setPen(QColor(140, 180, 220))
        painter.drawText(
            pixmap.rect().adjusted(0, body_h + 12, 0, 0),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            self._label,
        )
        painter.end()
        return pixmap
