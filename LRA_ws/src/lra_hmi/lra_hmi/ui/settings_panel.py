"""Pestaña de ajustes: formularios editables por cada nodo de ROS."""
from __future__ import annotations

from typing import Dict, List, Tuple

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..settings import (
    CalibratorParams,
    CameraParams,
    CameraUrdfParams,
    DetectorParams,
    HmiSettings,
    HoughParams,
    PickSortParams,
)


PIXEL_FORMATS = ["YUYV", "MJPG", "RGB3", "YUV2", "GREY"]
UR_TYPES = ["ur3", "ur3e", "ur5", "ur5e", "ur10", "ur10e", "ur16e", "ur20", "ur30"]


class SettingsPanel(QWidget):
    """Área desplazable con formularios enlazados al dataclass HmiSettings."""

    applied = pyqtSignal(object)        # emite los nuevos HmiSettings
    changed_keys = pyqtSignal(list)     # emite la lista de grupos afectados

    def __init__(self, settings: HmiSettings, parent=None):
        super().__init__(parent)
        self._initial = settings
        self._current = _deepcopy_settings(settings)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll.setWidget(container)
        self._form_layout = QVBoxLayout(container)
        self._form_layout.setSpacing(10)

        self._build_global(self._form_layout, settings)
        self._build_camera(self._form_layout, settings.camera)
        self._build_camera_urdf(self._form_layout, settings.camera_urdf)
        self._build_calibrator(self._form_layout, settings)
        self._build_detector(self._form_layout, settings.detector)
        self._build_pick_sort(self._form_layout, settings.pick_sort)
        self._form_layout.addStretch(1)

        outer.addWidget(scroll, 1)
        outer.addLayout(self._build_footer())


    def _build_global(self, layout: QVBoxLayout, s: HmiSettings) -> None:
        box = QGroupBox("General")
        form = QFormLayout(box)
        self._ip = QLineEdit(s.robot_ip)
        self._ip.setPlaceholderText("p. ej. 169.254.12.28")
        form.addRow("IP del robot:", self._ip)

        self._ur_type = QComboBox()
        self._ur_type.addItems(UR_TYPES)
        self._ur_type.setEditable(True)
        self._ur_type.setCurrentText(s.ur_type)
        form.addRow("Modelo UR:", self._ur_type)

        layout.addWidget(box)

    def _build_camera(self, layout: QVBoxLayout, c: CameraParams) -> None:
        box = QGroupBox("Cámara (v4l2)")
        form = QFormLayout(box)
        self._cam_device = QLineEdit(c.video_device)
        form.addRow("video_device:", self._cam_device)
        self._cam_w = QSpinBox()
        self._cam_w.setRange(160, 4096)
        self._cam_w.setValue(c.width)
        form.addRow("ancho:", self._cam_w)
        self._cam_h = QSpinBox()
        self._cam_h.setRange(120, 2160)
        self._cam_h.setValue(c.height)
        form.addRow("alto:", self._cam_h)
        self._cam_fps = QSpinBox()
        self._cam_fps.setRange(1, 120)
        self._cam_fps.setValue(c.framerate)
        form.addRow("fps:", self._cam_fps)
        self._cam_fmt = QComboBox()
        self._cam_fmt.addItems(PIXEL_FORMATS)
        if c.pixel_format in PIXEL_FORMATS:
            self._cam_fmt.setCurrentText(c.pixel_format)
        else:
            self._cam_fmt.setEditable(True)
            self._cam_fmt.setCurrentText(c.pixel_format)
        form.addRow("formato de píxel:", self._cam_fmt)
        self._cam_frame_id = QLineEdit(c.frame_id)
        form.addRow("camera_frame_id:", self._cam_frame_id)
        layout.addWidget(box)

    def _build_camera_urdf(self, layout: QVBoxLayout, c: CameraUrdfParams) -> None:
        box = QGroupBox("Cámara URDF / TF")
        form = QFormLayout(box)
        self._urdf_parent = QLineEdit(c.parent_frame)
        form.addRow("parent_frame:", self._urdf_parent)
        self._urdf_name = QLineEdit(c.camera_name)
        form.addRow("camera_name:", self._urdf_name)
        layout.addWidget(box)

    def _build_calibrator(self, layout: QVBoxLayout, s: HmiSettings) -> None:
        c = s.calibrator
        box = QGroupBox("Calibrador de Color")
        form = QFormLayout(box)
        self._num_boxes = QSpinBox()
        self._num_boxes.setRange(1, 6)
        self._num_boxes.setValue(s.num_boxes)
        form.addRow("num_cajas (número de cajas):", self._num_boxes)
        self._cal_frames = QSpinBox()
        self._cal_frames.setRange(1, 500)
        self._cal_frames.setValue(c.frames_muestreo)
        form.addRow("frames de muestreo:", self._cal_frames)
        self._cal_debug = QCheckBox()
        self._cal_debug.setChecked(c.show_debug)
        form.addRow("mostrar depuración:", self._cal_debug)
        (self._cal_min_r, self._cal_max_r, self._cal_min_d,
         self._cal_h1, self._cal_h2) = _build_hough_form(form, c.hough)
        layout.addWidget(box)

    def _build_detector(self, layout: QVBoxLayout, d: DetectorParams) -> None:
        box = QGroupBox("Detector")
        form = QFormLayout(box)
        self._det_frames = QSpinBox()
        self._det_frames.setRange(1, 500)
        self._det_frames.setValue(d.frames_muestreo)
        form.addRow("frames de muestreo:", self._det_frames)
        self._det_debug = QCheckBox()
        self._det_debug.setChecked(d.show_debug)
        form.addRow("mostrar depuración:", self._det_debug)
        self._det_target = QLineEdit(d.target_frame)
        form.addRow("target_frame:", self._det_target)
        self._det_camera = QLineEdit(d.camera_frame)
        form.addRow("camera_frame:", self._det_camera)
        (self._det_min_r, self._det_max_r, self._det_min_d,
         self._det_h1, self._det_h2) = _build_hough_form(form, d.hough)
        layout.addWidget(box)

    def _build_pick_sort(self, layout: QVBoxLayout, p: PickSortParams) -> None:
        box = QGroupBox("Recoger y Clasificar")
        form = QFormLayout(box)
        self._ps_sim = QCheckBox()
        self._ps_sim.setChecked(p.simulate_gripper)
        form.addRow("simular pinza:", self._ps_sim)
        self._ps_ox = QDoubleSpinBox()
        self._ps_ox.setRange(-1.0, 1.0)
        self._ps_ox.setDecimals(4)
        self._ps_ox.setSingleStep(0.001)
        self._ps_ox.setValue(p.offset_x)
        form.addRow("offset X (m):", self._ps_ox)
        self._ps_oy = QDoubleSpinBox()
        self._ps_oy.setRange(-1.0, 1.0)
        self._ps_oy.setDecimals(4)
        self._ps_oy.setSingleStep(0.001)
        self._ps_oy.setValue(p.offset_y)
        form.addRow("offset Y (m):", self._ps_oy)
        layout.addWidget(box)

    def _build_footer(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        self._status = QLabel("")
        self._status.setObjectName("mutedLabel")
        bar.addWidget(self._status, 1)

        btn_reset = QPushButton("Restablecer valores")
        btn_reload = QPushButton("Recargar desde disco")
        btn_apply = QPushButton("Aplicar")
        btn_apply.setObjectName("applyBtn")
        btn_reset.clicked.connect(self._on_reset)
        btn_reload.clicked.connect(self._on_reload)
        btn_apply.clicked.connect(self._on_apply)
        bar.addWidget(btn_reset)
        bar.addWidget(btn_reload)
        bar.addWidget(btn_apply)
        return bar


    def _on_apply(self) -> None:
        new = self._read_form()
        changed_groups = _diff_groups(self._current, new)
        self._current = new
        self.applied.emit(new)
        if changed_groups:
            self.changed_keys.emit(changed_groups)
            self._status.setText(
                "Aplicado. Reinicie para aplicar: " + ", ".join(changed_groups)
            )
        else:
            self._status.setText("Aplicado (sin cambios de parámetros).")

    def _on_reset(self) -> None:
        self._populate(HmiSettings())
        self._status.setText("Valores por defecto cargados. Pulse Aplicar para guardar.")

    def _on_reload(self) -> None:
        from ..config_io import load_settings
        try:
            loaded = load_settings()
        except Exception as exc:
            self._status.setText(f"Recarga fallida: {exc}")
            return
        self._populate(loaded)
        self._status.setText("Recargado desde disco. Pulse Aplicar para guardar.")


    def _read_form(self) -> HmiSettings:
        return HmiSettings(
            robot_ip=self._ip.text().strip() or "169.254.12.28",
            ur_type=self._ur_type.currentText().strip() or "ur3e",
            num_boxes=int(self._num_boxes.value()),
            camera=CameraParams(
                video_device=self._cam_device.text().strip() or "/dev/video0",
                width=int(self._cam_w.value()),
                height=int(self._cam_h.value()),
                framerate=int(self._cam_fps.value()),
                pixel_format=self._cam_fmt.currentText().strip() or "YUYV",
                frame_id=self._cam_frame_id.text().strip() or "camera_optical_frame",
            ),
            camera_urdf=CameraUrdfParams(
                parent_frame=self._urdf_parent.text().strip() or "tool0",
                camera_name=self._urdf_name.text().strip() or "camera",
            ),
            calibrator=CalibratorParams(
                frames_muestreo=int(self._cal_frames.value()),
                show_debug=bool(self._cal_debug.isChecked()),
                hough=HoughParams(
                    min_radius=int(self._cal_min_r.value()),
                    max_radius=int(self._cal_max_r.value()),
                    min_dist=int(self._cal_min_d.value()),
                    hough_param1=int(self._cal_h1.value()),
                    hough_param2=int(self._cal_h2.value()),
                ),
            ),
            detector=DetectorParams(
                frames_muestreo=int(self._det_frames.value()),
                show_debug=bool(self._det_debug.isChecked()),
                target_frame=self._det_target.text().strip() or "base_link",
                camera_frame=self._det_camera.text().strip() or "camera_optical_frame",
                hough=HoughParams(
                    min_radius=int(self._det_min_r.value()),
                    max_radius=int(self._det_max_r.value()),
                    min_dist=int(self._det_min_d.value()),
                    hough_param1=int(self._det_h1.value()),
                    hough_param2=int(self._det_h2.value()),
                ),
            ),
            pick_sort=PickSortParams(
                simulate_gripper=bool(self._ps_sim.isChecked()),
                offset_x=float(self._ps_ox.value()),
                offset_y=float(self._ps_oy.value()),
            ),
        )

    def _populate(self, s: HmiSettings) -> None:
        self._ip.setText(s.robot_ip)
        self._ur_type.setCurrentText(s.ur_type)
        self._num_boxes.setValue(s.num_boxes)

        self._cam_device.setText(s.camera.video_device)
        self._cam_w.setValue(s.camera.width)
        self._cam_h.setValue(s.camera.height)
        self._cam_fps.setValue(s.camera.framerate)
        self._cam_fmt.setCurrentText(s.camera.pixel_format)
        self._cam_frame_id.setText(s.camera.frame_id)

        self._urdf_parent.setText(s.camera_urdf.parent_frame)
        self._urdf_name.setText(s.camera_urdf.camera_name)

        self._cal_frames.setValue(s.calibrator.frames_muestreo)
        self._cal_debug.setChecked(s.calibrator.show_debug)
        self._cal_min_r.setValue(s.calibrator.hough.min_radius)
        self._cal_max_r.setValue(s.calibrator.hough.max_radius)
        self._cal_min_d.setValue(s.calibrator.hough.min_dist)
        self._cal_h1.setValue(s.calibrator.hough.hough_param1)
        self._cal_h2.setValue(s.calibrator.hough.hough_param2)

        self._det_frames.setValue(s.detector.frames_muestreo)
        self._det_debug.setChecked(s.detector.show_debug)
        self._det_target.setText(s.detector.target_frame)
        self._det_camera.setText(s.detector.camera_frame)
        self._det_min_r.setValue(s.detector.hough.min_radius)
        self._det_max_r.setValue(s.detector.hough.max_radius)
        self._det_min_d.setValue(s.detector.hough.min_dist)
        self._det_h1.setValue(s.detector.hough.hough_param1)
        self._det_h2.setValue(s.detector.hough.hough_param2)

        self._ps_sim.setChecked(s.pick_sort.simulate_gripper)
        self._ps_ox.setValue(s.pick_sort.offset_x)
        self._ps_oy.setValue(s.pick_sort.offset_y)


def _build_hough_form(form: QFormLayout, h: HoughParams) -> Tuple[QSpinBox, QSpinBox, QSpinBox, QSpinBox, QSpinBox]:
    sub = QGroupBox("Detector de círculos Hough")
    sub_form = QFormLayout(sub)
    min_r = QSpinBox(); min_r.setRange(1, 500); min_r.setValue(h.min_radius)
    max_r = QSpinBox(); max_r.setRange(1, 500); max_r.setValue(h.max_radius)
    min_d = QSpinBox(); min_d.setRange(1, 1000); min_d.setValue(h.min_dist)
    h1 = QSpinBox(); h1.setRange(1, 500); h1.setValue(h.hough_param1)
    h2 = QSpinBox(); h2.setRange(1, 500); h2.setValue(h.hough_param2)
    sub_form.addRow("min_radius:", min_r)
    sub_form.addRow("max_radius:", max_r)
    sub_form.addRow("min_dist:", min_d)
    sub_form.addRow("hough_param1:", h1)
    sub_form.addRow("hough_param2:", h2)
    form.addRow(sub)
    return min_r, max_r, min_d, h1, h2


def _deepcopy_settings(s: HmiSettings) -> HmiSettings:
    return HmiSettings.from_dict(s.as_dict())


_GROUP_FIELDS: Dict[str, List[str]] = {
    "driver":      ["robot_ip", "ur_type"],
    "moveit":      ["ur_type"],
    "camera":      ["camera"],
    "camera_urdf": ["camera_urdf"],
    "calibrator":  ["num_boxes", "calibrator"],
    "detector":    ["detector"],
    "pick_sort":   ["pick_sort"],
}


def _diff_groups(old: HmiSettings, new: HmiSettings) -> List[str]:
    """Devuelve la lista de grupos cuyos parámetros han cambiado."""
    if old.as_dict() == new.as_dict():
        return []
    old_d = old.as_dict()
    new_d = new.as_dict()
    changed = []
    for group, paths in _GROUP_FIELDS.items():
        for p in paths:
            if old_d.get(p) != new_d.get(p):
                changed.append(group)
                break
    return changed
