"""Per-box and total cap counters with reset and session report."""
from __future__ import annotations

import json
import os
import time
from typing import Dict

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class _BoxCard(QGroupBox):

    def __init__(self, box_id: int, parent=None):
        super().__init__(f"Box {box_id}", parent)
        self._count = 0
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        self._count_label = QLabel("0")
        self._count_label.setAlignment(Qt.AlignCenter)
        self._count_label.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #2c3e50;"
        )
        layout.addWidget(self._count_label)

    def increment(self) -> None:
        self._count += 1
        self._count_label.setText(str(self._count))

    def reset(self) -> None:
        self._count = 0
        self._count_label.setText("0")

    def value(self) -> int:
        return self._count


class CountersPanel(QGroupBox):

    reset_requested = pyqtSignal()

    def __init__(self, default_boxes: int = 4, parent=None):
        super().__init__("Counters", parent)
        self._total = 0
        self._boxes: Dict[int, _BoxCard] = {}
        self._session_started_at: float = time.time()

        outer = QVBoxLayout(self)

        top = QHBoxLayout()
        self._total_label = QLabel("Total: 0")
        self._total_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2c3e50;"
        )
        self._rate_label = QLabel("0.00 caps/min")
        self._rate_label.setStyleSheet("color:#666;")
        top.addWidget(self._total_label)
        top.addStretch(1)
        top.addWidget(self._rate_label)
        outer.addLayout(top)

        self._grid_widget = QWidget()
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(6)
        outer.addWidget(self._grid_widget)

        self._rebuild_grid(default_boxes)

        bottom = QHBoxLayout()
        btn_reset = QPushButton("Reset counters")
        btn_reset.clicked.connect(self._on_reset_clicked)
        bottom.addWidget(btn_reset)
        btn_save = QPushButton("Save session report…")
        btn_save.clicked.connect(self._save_report)
        bottom.addWidget(btn_save)
        bottom.addStretch(1)
        outer.addLayout(bottom)

        outer.addStretch(1)

    def _rebuild_grid(self, num_boxes: int) -> None:
        for i in reversed(range(self._grid.count())):
            item = self._grid.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        self._boxes.clear()

        cols = min(max(num_boxes, 1), 3)
        for box_id in range(1, num_boxes + 1):
            card = _BoxCard(box_id)
            row = (box_id - 1) // cols
            col = (box_id - 1) % cols
            self._grid.addWidget(card, row, col)
            self._boxes[box_id] = card

    def on_num_boxes(self, num: int) -> None:
        if num < 1:
            return
        if num != len(self._boxes):
            self._rebuild_grid(num)

    def on_box_assigned(self, box_id: int) -> None:
        if box_id in self._boxes:
            self._boxes[box_id].increment()
        self._total += 1
        self._total_label.setText(f"Total: {self._total}")
        self._update_rate()

    def on_total_caps(self, total: int) -> None:
        if total < self._total:
            self._total = total
            self._total_label.setText(f"Total: {self._total}")
            self._update_rate()

    def _update_rate(self) -> None:
        elapsed_min = max((time.time() - self._session_started_at) / 60.0, 1e-6)
        rate = self._total / elapsed_min
        self._rate_label.setText(f"{rate:.2f} caps/min")

    def _on_reset_clicked(self) -> None:
        self._total = 0
        self._session_started_at = time.time()
        self._total_label.setText("Total: 0")
        self._rate_label.setText("0.00 caps/min")
        for card in self._boxes.values():
            card.reset()
        self.reset_requested.emit()

    def _save_report(self) -> None:
        default_name = time.strftime("lra_session_%Y%m%d_%H%M%S.json")
        default_path = os.path.join(os.path.expanduser("~"), default_name)
        path, _ = QFileDialog.getSaveFileName(
            self, "Save session report", default_path, "JSON (*.json)"
        )
        if not path:
            return
        report = {
            "session_started_at": self._session_started_at,
            "saved_at": time.time(),
            "duration_seconds": time.time() - self._session_started_at,
            "total_caps": self._total,
            "per_box": {str(k): v.value() for k, v in self._boxes.items()},
        }
        try:
            with open(path, "w") as f:
                json.dump(report, f, indent=2)
        except OSError as exc:
            QMessageBox.warning(self, "Save failed", str(exc))
            return
        QMessageBox.information(self, "Saved", f"Report saved to {path}")
