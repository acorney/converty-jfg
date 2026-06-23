"""Converty — Jade PDF Converter entry point."""
import sys
import os
from pathlib import Path

# When frozen by PyInstaller, resolve asset paths relative to the executable
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

os.chdir(BASE_DIR)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont, QIcon
from PyQt6.QtCore import Qt

from app.ui.window import MainWindow
from app.ui.styles import APP_STYLESHEET


def load_fonts():
    font_dir = BASE_DIR / "fonts"
    if font_dir.exists():
        for ttf in font_dir.glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(ttf))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Jade PDF Converter")
    app.setOrganizationName("Jade Financial Group")

    load_fonts()

    font = QFont("Montserrat", 13)
    if not font.exactMatch():
        font = QFont("Segoe UI", 13)
    app.setFont(font)

    app.setStyleSheet(APP_STYLESHEET)

    icon_path = BASE_DIR / "assets" / "mark-flower.svg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
