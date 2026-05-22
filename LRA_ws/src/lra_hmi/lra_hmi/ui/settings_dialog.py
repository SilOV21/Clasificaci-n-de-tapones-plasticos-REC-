"""Settings dialog: robot IP, ur_type, num boxes."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional

from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
)


@dataclass
class HmiSettings:
    robot_ip: str = "169.254.12.28"
    ur_type: str = "ur3e"
    num_boxes: int = 4

    def as_dict(self) -> dict:
        return asdict(self)


class SettingsDialog(QDialog):

    def __init__(self, current: HmiSettings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self._result: Optional[HmiSettings] = None

        form = QFormLayout(self)

        self._ip_edit = QLineEdit(current.robot_ip)
        self._ip_edit.setPlaceholderText("e.g. 169.254.12.28")
        form.addRow("Robot IP:", self._ip_edit)

        self._ur_edit = QLineEdit(current.ur_type)
        form.addRow("UR type:", self._ur_edit)

        self._num_boxes = QSpinBox()
        self._num_boxes.setRange(1, 12)
        self._num_boxes.setValue(current.num_boxes)
        form.addRow("Number of boxes:", self._num_boxes)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _on_accept(self) -> None:
        self._result = HmiSettings(
            robot_ip=self._ip_edit.text().strip() or "169.254.12.28",
            ur_type=self._ur_edit.text().strip() or "ur3e",
            num_boxes=int(self._num_boxes.value()),
        )
        self.accept()

    def result_settings(self) -> Optional[HmiSettings]:
        return self._result
