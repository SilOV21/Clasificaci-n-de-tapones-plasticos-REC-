"""Per-subsystem launch / stop / restart row, plus global controls."""
from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..process_manager import ProcessManager
from .widgets import LedIndicator


class LauncherPanel(QGroupBox):
    """Lists each process group with start/stop/restart buttons and a status LED."""

    start_all_clicked = pyqtSignal()
    stop_all_clicked = pyqtSignal()

    def __init__(self, process_manager: ProcessManager, parent=None):
        super().__init__("System Launcher", parent)
        self._pm = process_manager
        self._leds: dict[str, LedIndicator] = {}
        self._state_labels: dict[str, QLabel] = {}

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        global_bar = QHBoxLayout()
        self._btn_start_all = QPushButton("▶  Start All")
        self._btn_start_all.setStyleSheet(self._primary_button_qss("#27ae60"))
        self._btn_stop_all = QPushButton("■  Stop All")
        self._btn_stop_all.setStyleSheet(self._primary_button_qss("#c0392b"))
        self._btn_start_all.clicked.connect(self.start_all_clicked)
        self._btn_stop_all.clicked.connect(self.stop_all_clicked)
        global_bar.addWidget(self._btn_start_all)
        global_bar.addWidget(self._btn_stop_all)
        global_bar.addStretch(1)
        layout.addLayout(global_bar)

        for key in self._pm.keys():
            layout.addWidget(self._build_row(key))

        layout.addStretch(1)

    def _build_row(self, key: str) -> QWidget:
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(4, 4, 4, 4)

        led = LedIndicator()
        led.set_color("stopped")
        self._leds[key] = led

        name = QLabel(self._pm.label(key))
        name.setMinimumWidth(140)
        name.setStyleSheet("font-weight: bold;")

        state = QLabel("stopped")
        state.setMinimumWidth(80)
        state.setStyleSheet("color: #777;")
        self._state_labels[key] = state

        btn_start = QPushButton("Start")
        btn_stop = QPushButton("Stop")
        btn_restart = QPushButton("Restart")
        for b in (btn_start, btn_stop, btn_restart):
            b.setMinimumWidth(70)

        btn_start.clicked.connect(lambda _=False, k=key: self._pm.start(k))
        btn_stop.clicked.connect(lambda _=False, k=key: self._pm.stop(k))
        btn_restart.clicked.connect(lambda _=False, k=key: self._pm.restart(k))

        h.addWidget(led)
        h.addWidget(name)
        h.addWidget(state)
        h.addStretch(1)
        h.addWidget(btn_start)
        h.addWidget(btn_stop)
        h.addWidget(btn_restart)
        return row

    def on_state_changed(self, key: str, state: str) -> None:
        if key in self._leds:
            self._leds[key].set_color(state)
        if key in self._state_labels:
            self._state_labels[key].setText(state)

    @staticmethod
    def _primary_button_qss(bg: str) -> str:
        return (
            f"QPushButton {{ background:{bg}; color:white; font-weight:bold; "
            f"padding:6px 14px; border-radius:4px; }}"
            f"QPushButton:hover {{ background:#222; }}"
        )
