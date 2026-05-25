"""Visor de cámara: renderiza /image_raw o /tapones/imagen_debug."""
from __future__ import annotations

import cv2
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)


class CameraPanel(QGroupBox):

    SOURCE_RAW = "Cámara cruda (/image_raw)"
    SOURCE_DEBUG = "Superposición del detector (/tapones/imagen_debug)"

    def __init__(self, title: str = "Cámara", parent=None):
        super().__init__(title, parent)
        self._latest_raw: np.ndarray | None = None
        self._latest_debug: np.ndarray | None = None

        outer = QVBoxLayout(self)

        top = QHBoxLayout()
        top.addWidget(QLabel("Fuente:"))
        self._source = QComboBox()
        self._source.addItems([self.SOURCE_DEBUG, self.SOURCE_RAW])
        self._source.currentIndexChanged.connect(self._refresh)
        top.addWidget(self._source)
        top.addStretch(1)
        self._size_label = QLabel("—")
        self._size_label.setObjectName("mutedLabel")
        top.addWidget(self._size_label)
        outer.addLayout(top)

        self._view = QLabel()
        self._view.setObjectName("cameraView")
        self._view.setAlignment(Qt.AlignCenter)
        self._view.setMinimumSize(320, 240)
        self._view.setStyleSheet("background-color:#000;")
        self._view.setText("(sin imagen aún)")
        outer.addWidget(self._view, 1)

    def on_image_raw(self, image: np.ndarray) -> None:
        self._latest_raw = image
        if self._source.currentText() == self.SOURCE_RAW:
            self._render(image)

    def on_image_debug(self, image: np.ndarray) -> None:
        self._latest_debug = image
        if self._source.currentText() == self.SOURCE_DEBUG:
            self._render(image)

    def _refresh(self) -> None:
        if self._source.currentText() == self.SOURCE_RAW and self._latest_raw is not None:
            self._render(self._latest_raw)
        elif self._source.currentText() == self.SOURCE_DEBUG and self._latest_debug is not None:
            self._render(self._latest_debug)
        else:
            self._view.setText("(sin imagen aún)")

    def _render(self, bgr: np.ndarray) -> None:
        if bgr is None or bgr.size == 0:
            return
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        h, w, _ = rgb.shape
        self._size_label.setText(f"{w}×{h}")
        qimg = QImage(rgb.data, w, h, w * 3, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qimg)
        scaled = pix.scaled(
            self._view.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self._view.setPixmap(scaled)
