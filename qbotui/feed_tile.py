"""One labeled image pane styled as a control-center viewer card."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap, QResizeEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget


class FeedTile(QWidget):
    """Viewer card: title, LIVE badge, and the latest full frame."""

    def __init__(self, label: str, index: int = 1, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._label = label
        self._index = index
        self._last_image: QImage | None = None
        self.setObjectName("viewerCardHost")
        self.setProperty("class", "viewerCard")

        self._frame = QWidget()
        self._frame.setObjectName("viewerCard")
        self._frame.setStyleSheet(
            "QWidget#viewerCard {"
            "background-color: #062E5A;"
            "border: 1px solid #1F6FB5;"
            "border-radius: 12px;"
            "}"
        )

        title = f"VIEWER {index:02d}"
        self._title = QLabel(title)
        self._title.setObjectName("sectionTitle")
        self._subtitle = QLabel(label)
        self._subtitle.setObjectName("mutedLabel")
        self._subtitle.setWordWrap(True)

        self._live = QLabel("LIVE")
        self._live.setObjectName("liveBadge")
        self._live.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_col.addWidget(self._title)
        title_col.addWidget(self._subtitle)
        header.addLayout(title_col, 1)
        header.addWidget(self._live, 0, Qt.AlignmentFlag.AlignTop)

        self._view = QLabel()
        self._view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._view.setMinimumSize(160, 100)
        self._view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._view.setStyleSheet("background-color: #001633; border-radius: 8px;")
        self._placeholder = self._build_placeholder()
        self._view.setPixmap(self._placeholder)

        inner = QVBoxLayout(self._frame)
        inner.setContentsMargins(12, 12, 12, 12)
        inner.setSpacing(8)
        inner.addLayout(header)
        inner.addWidget(self._view, 1)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._frame)

    @property
    def label(self) -> str:
        return self._label

    def set_detail(self, text: str) -> None:
        if text:
            self._subtitle.setText(f"{self._label} · {text}")
        else:
            self._subtitle.setText(self._label)

    def show_frame(self, image: QImage) -> None:
        self._last_image = image.copy()
        self._paint_current()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._paint_current()

    def _paint_current(self) -> None:
        image = self._last_image
        if image is None:
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

    def _build_placeholder(self) -> QPixmap:
        pixmap = QPixmap(320, 180)
        pixmap.fill(QColor(0, 22, 51))
        painter = QPainter(pixmap)
        painter.setPen(QColor(176, 183, 188))
        painter.drawText(
            pixmap.rect(),
            Qt.AlignmentFlag.AlignCenter,
            "Camera feed",
        )
        painter.end()
        return pixmap
