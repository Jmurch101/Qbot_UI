"""Entry point: python -m qbotui"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    from PySide6.QtWidgets import QApplication

    from qbotui.main_window import QbotMainWindow

    app = QApplication(sys.argv if argv is None else argv)
    window = QbotMainWindow()
    window.show()
    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(main())
