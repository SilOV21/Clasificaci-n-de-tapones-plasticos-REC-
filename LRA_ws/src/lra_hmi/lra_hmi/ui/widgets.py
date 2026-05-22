"""Small shared widgets: LED indicator, color swatch."""
from __future__ import annotations

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter
from PyQt5.QtWidgets import QLabel, QWidget


STATE_COLORS = {
    "stopped": "#888888",
    "starting": "#ddb000",
    "running": "#2ecc71",
    "crashed": "#e74c3c",
    "stopping": "#cc6600",
    "ok": "#2ecc71",
    "fail": "#e74c3c",
    "unknown": "#888888",
}


class LedIndicator(QWidget):
    """A small circular status LED."""

    def __init__(self, diameter: int = 18, parent=None):
        super().__init__(parent)
        self._diameter = diameter
        self._color = QColor(STATE_COLORS["unknown"])
        self.setFixedSize(QSize(diameter + 4, diameter + 4))

    def set_color(self, color_name: str) -> None:
        if color_name in STATE_COLORS:
            self._color = QColor(STATE_COLORS[color_name])
        else:
            self._color = QColor(color_name)
        self.update()

    def paintEvent(self, _event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self._color))
        painter.setPen(QColor("#222222"))
        m = 2
        painter.drawEllipse(m, m, self._diameter, self._diameter)


class ColorSwatch(QLabel):
    """Label whose background reflects the detected cap color."""

    COLOR_MAP = {
        "rojo": "#e74c3c",
        "red": "#e74c3c",
        "azul": "#3498db",
        "blue": "#3498db",
        "amarillo": "#f1c40f",
        "yellow": "#f1c40f",
        "blanco": "#ecf0f1",
        "white": "#ecf0f1",
        "verde": "#2ecc71",
        "green": "#2ecc71",
        "negro": "#222222",
        "black": "#222222",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(36)
        self.setText("—")
        self._apply_color("#dddddd", text_color="#222222")

    def set_color(self, name: str) -> None:
        key = (name or "").strip().lower()
        bg = self.COLOR_MAP.get(key, "#dddddd")
        text_color = "#222222" if key in ("blanco", "white", "amarillo", "yellow") else "#ffffff"
        self.setText(name.upper() if name else "—")
        self._apply_color(bg, text_color)

    def _apply_color(self, bg: str, text_color: str = "#ffffff") -> None:
        self.setStyleSheet(
            f"background-color: {bg}; color: {text_color}; "
            f"border-radius: 6px; font-weight: bold; padding: 4px;"
        )
