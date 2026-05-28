"""Lanzador por subsistema con botones de Iniciar / Detener / Reiniciar."""
from __future__ import annotations

from typing import Dict, List

from PyQt5.QtCore import pyqtSignal
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


SECTION_ORDER = ["hardware", "vision", "control"]
SECTION_TITLES = {
    "hardware": "Hardware",
    "vision":   "Visión",
    "control":  "Control",
}

STATE_LABELS = {
    "stopped":  "detenido",
    "starting": "iniciando",
    "running":  "en ejecución",
    "crashed":  "caído",
    "stopping": "deteniendo",
    "unknown":  "desconocido",
}


class LauncherPanel(QGroupBox):
    """Lista cada grupo de procesos con sus controles y un LED de estado."""

    start_all_clicked = pyqtSignal()
    stop_all_clicked = pyqtSignal()

    def __init__(self, process_manager: ProcessManager, parent=None):
        super().__init__("Lanzador de Subsistemas", parent)
        self._pm = process_manager
        self._leds: Dict[str, LedIndicator] = {}
        self._state_labels: Dict[str, QLabel] = {}

        outer = QVBoxLayout(self)
        outer.setSpacing(8)

        global_bar = QHBoxLayout()
        self._btn_start_all = QPushButton("▶  Iniciar todo")
        self._btn_start_all.setObjectName("startBtn")
        self._btn_stop_all = QPushButton("■  Detener todo")
        self._btn_stop_all.setObjectName("stopBtn")
        for b in (self._btn_start_all, self._btn_stop_all):
            b.setMinimumHeight(40)
            b.setMinimumWidth(150)
        self._btn_start_all.clicked.connect(self.start_all_clicked)
        self._btn_stop_all.clicked.connect(self.stop_all_clicked)
        global_bar.addWidget(self._btn_start_all)
        global_bar.addWidget(self._btn_stop_all)
        global_bar.addStretch(1)
        outer.addLayout(global_bar)

        sections = self._group_by_section()
        if len(self._pm.keys()) <= 3 or len(sections) <= 1:
            for key in self._pm.keys():
                outer.addWidget(self._build_row(key))
        else:
            for sec in SECTION_ORDER:
                keys = sections.get(sec)
                if not keys:
                    continue
                outer.addWidget(self._build_section(sec, keys))

        outer.addStretch(1)

    def _group_by_section(self) -> Dict[str, List[str]]:
        out: Dict[str, List[str]] = {}
        for key in self._pm.keys():
            sec = self._pm.section(key) if hasattr(self._pm, "section") else "hardware"
            out.setdefault(sec, []).append(key)
        return out

    def _build_section(self, name: str, keys: List[str]) -> QGroupBox:
        box = QGroupBox(SECTION_TITLES.get(name, name.title()))
        layout = QVBoxLayout(box)
        layout.setSpacing(4)
        for key in keys:
            layout.addWidget(self._build_row(key))
        return box

    def _build_row(self, key: str) -> QWidget:
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(4, 4, 4, 4)

        led = LedIndicator()
        led.set_color("stopped")
        self._leds[key] = led

        name = QLabel(self._pm.label(key))
        name.setMinimumWidth(170)

        state = QLabel(STATE_LABELS["stopped"])
        state.setMinimumWidth(110)
        state.setObjectName("mutedLabel")
        self._state_labels[key] = state

        btn_start = QPushButton("Iniciar")
        btn_stop = QPushButton("Detener")
        btn_restart = QPushButton("Reiniciar")
        for b in (btn_start, btn_stop, btn_restart):
            b.setMinimumWidth(96)
            b.setMinimumHeight(34)

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
            self._state_labels[key].setText(STATE_LABELS.get(state, state))
