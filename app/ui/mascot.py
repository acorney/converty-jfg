"""Arrow mascot widget — displays the correct SVG for each app state."""
import os
from pathlib import Path

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, pyqtProperty, QTimer
from PyQt6.QtGui import QPainter
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QWidget, QVBoxLayout

ASSETS = Path(__file__).parent.parent.parent / "assets"

SVG_MAP = {
    "idle":       ASSETS / "arrow-ready.svg",
    "queued":     ASSETS / "arrow-ready.svg",
    "converting": ASSETS / "arrow-working.svg",
    "done":       ASSETS / "arrow-done.svg",
    "error":      ASSETS / "arrow-oops.svg",
}


class MascotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = "idle"
        self._offset_y = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._svg = QSvgWidget(self)
        self._svg.setFixedSize(60, 42)
        layout.addWidget(self._svg)

        self._anim = QPropertyAnimation(self, b"mascot_y")
        self._anim.setEasingCurve(QEasingCurve.Type.SineCurve)
        self._anim.setLoopCount(-1)

        self._set_svg("idle")
        self._start_bob(4500)

    def set_state(self, state: str):
        if state == self._state:
            return
        self._state = state
        self._set_svg(state)
        if state == "converting":
            self._start_bob(2600)
        elif state in ("idle", "queued"):
            self._start_bob(4500)
        else:
            self._anim.stop()
            self._offset_y = 0
            self._svg.move(self._svg.x(), 0)

    def _set_svg(self, state: str):
        path = SVG_MAP.get(state, SVG_MAP["idle"])
        if path.exists():
            self._svg.load(str(path))

    def _start_bob(self, duration_ms: int):
        self._anim.stop()
        self._anim.setDuration(duration_ms)
        self._anim.setStartValue(0)
        self._anim.setKeyValueAt(0.5, -9)
        self._anim.setEndValue(0)
        self._anim.start()

    def get_mascot_y(self):
        return self._offset_y

    def set_mascot_y(self, val: int):
        self._offset_y = val
        self._svg.move(self._svg.x(), val)

    mascot_y = pyqtProperty(int, get_mascot_y, set_mascot_y)
