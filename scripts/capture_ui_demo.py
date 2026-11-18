"""Capture demo screenshots of the QBot UI for review."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("QT_QPA_PLATFORM", "cocoa")

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from qbotui.main_window import QbotMainWindow
from qbotui.tasks import TaskCatalog


def _grab(window: QbotMainWindow, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pixmap = window.grab()
    if not pixmap.save(str(path), "PNG"):
        raise RuntimeError(f"Failed to save {path}")
    print(f"saved {path}")


def main() -> int:
    app = QApplication.instance() or QApplication([])
    out = ROOT / "demo_shots"
    window = QbotMainWindow()
    window.resize(1280, 860)
    window.show()
    app.processEvents()

    def shot_startup() -> None:
        _grab(window, out / "01_startup.png")
        # Switch to Play (1 RGB window)
        combo = window._connection._task
        play_index = next(
            i for i in range(combo.count()) if combo.itemData(i) == TaskCatalog.PLAY.key
        )
        combo.setCurrentIndex(play_index)
        app.processEvents()
        QTimer.singleShot(150, shot_play)

    def shot_play() -> None:
        _grab(window, out / "02_play.png")
        combo = window._connection._task
        line_index = next(
            i
            for i in range(combo.count())
            if combo.itemData(i) == TaskCatalog.LINE_FOLLOW.key
        )
        combo.setCurrentIndex(line_index)
        app.processEvents()
        QTimer.singleShot(150, shot_line)

    def shot_line() -> None:
        _grab(window, out / "03_line_follow.png")
        window.close()
        app.quit()

    QTimer.singleShot(300, shot_startup)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
