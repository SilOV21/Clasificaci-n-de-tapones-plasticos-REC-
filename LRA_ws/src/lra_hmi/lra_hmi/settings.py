"""HMI settings: nested dataclasses mirroring each node's ROS parameters."""
from dataclasses import asdict, dataclass, field, fields, is_dataclass
from typing import Any, Dict, get_type_hints


@dataclass
class CameraParams:
    video_device: str = "/dev/video2"
    width: int = 640
    height: int = 480
    framerate: int = 30
    pixel_format: str = "YUYV"
    frame_id: str = "camera_optical_frame"


@dataclass
class CameraUrdfParams:
    parent_frame: str = "tool0"
    camera_name: str = "camera"


@dataclass
class HoughParams:
    min_radius: int = 33
    max_radius: int = 54
    min_dist: int = 75
    hough_param1: int = 21
    hough_param2: int = 27


@dataclass
class CalibratorParams:
    frames_muestreo: int = 30
    show_debug: bool = False
    hough: HoughParams = field(default_factory=HoughParams)


@dataclass
class DetectorParams:
    frames_muestreo: int = 30
    show_debug: bool = True
    target_frame: str = "base_link"
    camera_frame: str = "camera_optical_frame"
    hough: HoughParams = field(default_factory=HoughParams)


@dataclass
class PickSortParams:
    simulate_gripper: bool = False
    offset_x: float = 0.0
    offset_y: float = 0.0


@dataclass
class HmiSettings:
    robot_ip: str = "169.254.12.28"
    ur_type: str = "ur3e"
    num_boxes: int = 4
    camera: CameraParams = field(default_factory=CameraParams)
    camera_urdf: CameraUrdfParams = field(default_factory=CameraUrdfParams)
    calibrator: CalibratorParams = field(default_factory=CalibratorParams)
    detector: DetectorParams = field(default_factory=DetectorParams)
    pick_sort: PickSortParams = field(default_factory=PickSortParams)

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HmiSettings":
        return _from_dict(cls, data)


def _from_dict(cls, data):
    if not is_dataclass(cls):
        return data
    if not isinstance(data, dict):
        return cls()
    type_hints = get_type_hints(cls)
    kwargs: Dict[str, Any] = {}
    for f in fields(cls):
        if f.name not in data:
            continue
        value = data[f.name]
        actual_type = type_hints.get(f.name)
        if actual_type is not None and is_dataclass(actual_type):
            kwargs[f.name] = _from_dict(actual_type, value if isinstance(value, dict) else {})
        else:
            kwargs[f.name] = _coerce(actual_type, value)
    return cls(**kwargs)


def _coerce(target_type, value):
    if target_type is bool:
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "yes", "on")
        return bool(value)
    if target_type is int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0
    if target_type is float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
    if target_type is str:
        return str(value)
    return value
