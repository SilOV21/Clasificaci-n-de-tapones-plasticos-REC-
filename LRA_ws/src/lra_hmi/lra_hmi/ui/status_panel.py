"""Estado del robot: conexión, articulaciones y último color detectado."""
from __future__ import annotations

import math
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)

from .widgets import ColorSwatch, LedIndicator


JOINT_LABELS = [
    "Hombro (pan)",
    "Hombro (lift)",
    "Codo",
    "Muñeca 1",
    "Muñeca 2",
    "Muñeca 3",
]


class StatusPanel(QGroupBox):

    def __init__(self, parent=None):
        super().__init__("Estado del Robot", parent)
        outer = QVBoxLayout(self)

        conn_row = QHBoxLayout()
        self._conn_led = LedIndicator(diameter=22)
        self._conn_label = QLabel("UR3e: desconocido")
        self._rtt_label = QLabel("rtt: —")
        self._rtt_label.setObjectName("mutedLabel")
        conn_row.addWidget(self._conn_led)
        conn_row.addWidget(self._conn_label)
        conn_row.addStretch(1)
        conn_row.addWidget(self._rtt_label)
        outer.addLayout(conn_row)

        joint_row = QHBoxLayout()
        self._joint_led = LedIndicator(diameter=16)
        joint_row.addWidget(self._joint_led)
        joint_row.addWidget(QLabel("Flujo de articulaciones:"))
        self._joint_stream_label = QLabel("sin datos")
        joint_row.addWidget(self._joint_stream_label)
        joint_row.addStretch(1)
        outer.addLayout(joint_row)

        joints_group = QGroupBox("Ángulos articulares (°)")
        form = QFormLayout(joints_group)
        form.setLabelAlignment(Qt.AlignRight)
        self._joint_value_labels: List[QLabel] = []
        for label in JOINT_LABELS:
            v = QLabel("—")
            v.setObjectName("monoLabel")
            v.setMinimumWidth(90)
            self._joint_value_labels.append(v)
            form.addRow(label + ":", v)
        outer.addWidget(joints_group)

        color_group = QGroupBox("Último tapón detectado")
        cgl = QVBoxLayout(color_group)
        self._swatch = ColorSwatch()
        cgl.addWidget(self._swatch)
        outer.addWidget(color_group)

        vision_row = QHBoxLayout()
        self._vision_enable_cb = QCheckBox("Visión activa")
        self._vision_enable_cb.setChecked(True)
        vision_row.addWidget(self._vision_enable_cb)
        vision_row.addStretch(1)
        outer.addLayout(vision_row)

        outer.addStretch(1)

    @property
    def vision_enable_checkbox(self) -> QCheckBox:
        return self._vision_enable_cb

    def set_connection(self, reachable: bool, rtt_ms: float) -> None:
        if reachable:
            self._conn_led.set_color("ok")
            self._conn_label.setText("UR3e: accesible")
            if math.isnan(rtt_ms):
                self._rtt_label.setText("rtt: —")
            else:
                self._rtt_label.setText(f"rtt: {rtt_ms:.1f} ms")
        else:
            self._conn_led.set_color("fail")
            self._conn_label.setText("UR3e: inaccesible")
            self._rtt_label.setText("rtt: —")

    def set_joint_stream_stale(self, stale: bool) -> None:
        if stale:
            self._joint_led.set_color("fail")
            self._joint_stream_label.setText("sin datos (¿driver caído?)")
        else:
            self._joint_led.set_color("ok")
            self._joint_stream_label.setText("activo")

    def set_joint_angles(self, degrees: List[float]) -> None:
        for label, value in zip(self._joint_value_labels, degrees):
            if math.isnan(value):
                label.setText("—")
            else:
                label.setText(f"{value:+7.2f}")

    def set_color(self, name: str) -> None:
        self._swatch.set_color(name)
