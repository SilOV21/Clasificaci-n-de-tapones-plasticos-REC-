"""Process manager: spawns and monitors each ROS node as a separate subprocess."""
from __future__ import annotations

import os
import signal
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock, Thread
from typing import Callable, Dict, List, Optional

from PyQt5.QtCore import QObject, pyqtSignal

from .settings import HmiSettings


class GroupState(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    CRASHED = "crashed"
    STOPPING = "stopping"


@dataclass
class GroupSpec:
    key: str
    label: str
    argv_factory: Callable[[], List[str]]
    section: str = "hardware"
    startup_delay_s: float = 0.0


@dataclass
class GroupRuntime:
    state: GroupState = GroupState.STOPPED
    process: Optional[subprocess.Popen] = None
    pgid: Optional[int] = None
    started_at: Optional[float] = None
    log_lines: List[str] = field(default_factory=list)
    reader_thread: Optional[Thread] = None


class ProcessManager(QObject):
    state_changed = pyqtSignal(str, str)
    log_line = pyqtSignal(str, str)

    MAX_LOG_LINES = 2000

    def __init__(self, settings: Optional[HmiSettings] = None):
        super().__init__()
        self._settings: HmiSettings = settings if settings is not None else HmiSettings()
        self._lock = Lock()

        self._groups: Dict[str, GroupSpec] = {}
        self._runtime: Dict[str, GroupRuntime] = {}
        self._register_default_groups()

    @staticmethod
    def is_sim_mode() -> bool:
        return os.environ.get("LRA_HMI_SIM", "").strip() not in ("", "0", "false", "False")

    def _register_default_groups(self) -> None:
        if self.is_sim_mode():
            self._register_sim_groups()
        else:
            self._register_real_groups()

    def _register_real_groups(self) -> None:
        s = lambda: self._settings  # late-bound lookup so set_settings takes effect

        self._register(GroupSpec(
            key="driver",
            label="UR Driver",
            section="hardware",
            startup_delay_s=2.0,
            argv_factory=lambda: [
                "ros2", "launch", "ur_robot_driver", "ur_control.launch.py",
                f"ur_type:={s().ur_type}",
                f"robot_ip:={s().robot_ip}",
            ],
        ))

        self._register(GroupSpec(
            key="tf",
            label="TF Publisher",
            section="hardware",
            startup_delay_s=0.5,
            argv_factory=lambda: [
                "ros2", "run", "tf2_ros", "static_transform_publisher",
                "0", "0", "0", "0", "0", "0", "world", "base_link",
            ],
        ))

        self._register(GroupSpec(
            key="moveit",
            label="MoveIt",
            section="control",
            startup_delay_s=4.0,
            argv_factory=lambda: [
                "ros2", "launch", "ur_moveit_config", "ur_moveit.launch.py",
                f"ur_type:={s().ur_type}",
                "launch_rviz:=false",
                "launch_servo:=false",
            ],
        ))

        self._register(GroupSpec(
            key="camera",
            label="Camera (v4l2)",
            section="vision",
            startup_delay_s=1.0,
            argv_factory=lambda: _build_camera_argv(s().camera),
        ))

        self._register(GroupSpec(
            key="camera_urdf",
            label="Camera URDF / TF",
            section="vision",
            startup_delay_s=0.5,
            argv_factory=lambda: [
                "ros2", "launch", "lra_vision", "upload_urdf.launch.py",
                f"parent_frame:={s().camera_urdf.parent_frame}",
                f"camera_name:={s().camera_urdf.camera_name}",
            ],
        ))

        self._register(GroupSpec(
            key="calibrator",
            label="Color Calibrator",
            section="vision",
            startup_delay_s=1.0,
            argv_factory=lambda: _build_calibrator_argv(s()),
        ))

        self._register(GroupSpec(
            key="pick_sort",
            label="Pick-Sort",
            section="control",
            startup_delay_s=3.0,
            argv_factory=lambda: [
                "ros2", "run", "ur3_vision_control", "ur3_pick_sort",
                "--ros-args",
                "-p", f"simulate_gripper:={_bool_arg(s().pick_sort.simulate_gripper)}",
                "-p", f"offset_x:={s().pick_sort.offset_x}",
                "-p", f"offset_y:={s().pick_sort.offset_y}",
            ],
        ))

        self._register(GroupSpec(
            key="detector",
            label="Detector",
            section="vision",
            startup_delay_s=2.0,
            argv_factory=lambda: _build_detector_argv(s()),
        ))

    def _register_sim_groups(self) -> None:
        self._register(GroupSpec(
            key="driver",
            label="[SIM] UR Driver",
            section="hardware",
            startup_delay_s=2.0,
            argv_factory=lambda: ["ros2", "run", "lra_hmi_sim", "fake_ur_driver"],
        ))
        self._register(GroupSpec(
            key="tf",
            label="[SIM] TF Publisher",
            section="hardware",
            startup_delay_s=0.5,
            argv_factory=lambda: [
                "ros2", "run", "tf2_ros", "static_transform_publisher",
                "0", "0", "0", "0", "0", "0", "world", "base_link",
            ],
        ))
        self._register(GroupSpec(
            key="vision_pipeline",
            label="[SIM] Vision Pipeline",
            section="vision",
            startup_delay_s=0.0,
            argv_factory=lambda: [
                "ros2", "launch", "lra_hmi_sim", "simulation.launch.py",
            ],
        ))

    def _register(self, spec: GroupSpec) -> None:
        self._groups[spec.key] = spec
        self._runtime[spec.key] = GroupRuntime()

    def keys(self) -> List[str]:
        return list(self._groups.keys())

    def label(self, key: str) -> str:
        return self._groups[key].label

    def section(self, key: str) -> str:
        return self._groups[key].section

    def state(self, key: str) -> GroupState:
        return self._runtime[key].state

    def set_settings(self, settings: HmiSettings) -> None:
        """Update the settings consulted by argv factories (takes effect on next start)."""
        self._settings = settings

    def settings(self) -> HmiSettings:
        return self._settings

    def robot_ip(self) -> str:
        return self._settings.robot_ip

    def start(self, key: str) -> bool:
        with self._lock:
            if key not in self._groups:
                return False
            rt = self._runtime[key]
            if rt.state in (GroupState.RUNNING, GroupState.STARTING):
                return False
            spec = self._groups[key]
            argv = spec.argv_factory()
            try:
                proc = subprocess.Popen(
                    argv,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    bufsize=1,
                    text=True,
                    preexec_fn=os.setsid,
                )
            except FileNotFoundError as exc:
                self._set_state(key, GroupState.CRASHED)
                self.log_line.emit(key, f"[error] launch failed: {exc}")
                return False
            rt.process = proc
            rt.pgid = os.getpgid(proc.pid)
            rt.started_at = time.time()
            self._set_state(key, GroupState.STARTING)
            self.log_line.emit(key, f"[info] started: {' '.join(argv)}")
            rt.reader_thread = Thread(
                target=self._reader_loop,
                args=(key, proc),
                name=f"reader-{key}",
                daemon=True,
            )
            rt.reader_thread.start()
            Thread(
                target=self._promote_to_running,
                args=(key, spec.startup_delay_s),
                daemon=True,
            ).start()
            return True

    def _promote_to_running(self, key: str, delay: float) -> None:
        if delay > 0:
            time.sleep(delay)
        with self._lock:
            rt = self._runtime.get(key)
            if rt and rt.state == GroupState.STARTING and rt.process and rt.process.poll() is None:
                self._set_state(key, GroupState.RUNNING)

    def stop(self, key: str, hard: bool = False, timeout_s: float = 5.0) -> bool:
        with self._lock:
            rt = self._runtime.get(key)
            if not rt or not rt.process:
                return False
            if rt.process.poll() is not None:
                self._set_state(key, GroupState.STOPPED)
                return True
            self._set_state(key, GroupState.STOPPING)
            sig = signal.SIGKILL if hard else signal.SIGTERM
            try:
                os.killpg(rt.pgid, sig)
            except ProcessLookupError:
                pass
            except PermissionError as exc:
                self.log_line.emit(key, f"[error] killpg failed: {exc}")

        if hard:
            self._wait_dead(key, timeout_s=1.0)
            return True

        if not self._wait_dead(key, timeout_s=timeout_s):
            with self._lock:
                rt = self._runtime.get(key)
                if rt and rt.process and rt.process.poll() is None:
                    self.log_line.emit(key, "[warn] SIGTERM ignored, escalating to SIGKILL")
                    try:
                        os.killpg(rt.pgid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
            self._wait_dead(key, timeout_s=2.0)
        return True

    def _wait_dead(self, key: str, timeout_s: float) -> bool:
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            with self._lock:
                rt = self._runtime.get(key)
                if not rt or not rt.process or rt.process.poll() is not None:
                    if rt:
                        self._set_state(key, GroupState.STOPPED)
                        rt.process = None
                        rt.pgid = None
                    return True
            time.sleep(0.1)
        return False

    def restart(self, key: str) -> bool:
        self.stop(key)
        time.sleep(0.3)
        return self.start(key)

    def start_all(self) -> None:
        for key in self.keys():
            self.start(key)
            time.sleep(self._groups[key].startup_delay_s)

    def stop_all(self, hard: bool = False) -> None:
        for key in reversed(self.keys()):
            self.stop(key, hard=hard)

    def emergency_stop(self) -> None:
        self.stop_all(hard=True)

    def _reader_loop(self, key: str, proc: subprocess.Popen) -> None:
        try:
            assert proc.stdout is not None
            for raw in proc.stdout:
                line = raw.rstrip("\n")
                with self._lock:
                    rt = self._runtime.get(key)
                    if rt is None:
                        break
                    rt.log_lines.append(line)
                    if len(rt.log_lines) > self.MAX_LOG_LINES:
                        del rt.log_lines[0:len(rt.log_lines) - self.MAX_LOG_LINES]
                self.log_line.emit(key, line)
        except (ValueError, OSError):
            pass
        finally:
            rc = proc.wait()
            with self._lock:
                rt = self._runtime.get(key)
                if rt is None:
                    return
                expected_stop = rt.state == GroupState.STOPPING
                rt.process = None
                rt.pgid = None
                if expected_stop or rc == 0 or rc == -signal.SIGTERM or rc == -signal.SIGKILL:
                    self._set_state(key, GroupState.STOPPED)
                else:
                    self._set_state(key, GroupState.CRASHED)
                    self.log_line.emit(key, f"[error] process exited with code {rc}")

    def _set_state(self, key: str, new_state: GroupState) -> None:
        rt = self._runtime[key]
        if rt.state == new_state:
            return
        rt.state = new_state
        self.state_changed.emit(key, new_state.value)

    def shutdown(self) -> None:
        for key in self.keys():
            self.stop(key, hard=True, timeout_s=1.0)


def _bool_arg(value: bool) -> str:
    return "true" if value else "false"


def _camera_info_url() -> str:
    """Best-effort lookup of the lra_vision calibration YAML."""
    try:
        from ament_index_python.packages import (
            PackageNotFoundError,
            get_package_share_directory,
        )
        try:
            share = get_package_share_directory("lra_vision")
            return "file://" + os.path.join(share, "calibration_data", "camera_info.yaml")
        except PackageNotFoundError:
            pass
    except ImportError:
        pass
    return ""


def _build_camera_argv(cam) -> List[str]:
    argv = [
        "ros2", "run", "v4l2_camera", "v4l2_camera_node",
        "--ros-args",
        "-p", f"video_device:={cam.video_device}",
        "-p", f"image_size:=[{cam.width},{cam.height}]",
        "-p", f"time_per_frame:=[1,{cam.framerate}]",
        "-p", f"pixel_format:={cam.pixel_format}",
        "-p", f"camera_frame_id:={cam.frame_id}",
    ]
    url = _camera_info_url()
    if url:
        argv.extend(["-p", f"camera_info_url:={url}"])
    argv.extend([
        "-r", "image_raw:=camera/image_raw",
        "-r", "camera_info:=camera/camera_info",
    ])
    return argv


def _build_calibrator_argv(s: HmiSettings) -> List[str]:
    h = s.calibrator.hough
    argv = [
        "ros2", "run", "rec_vision", "color_calibrator_node",
        "--ros-args",
        "-p", f"num_cajas:={s.num_boxes}",
        "-p", f"frames_muestreo:={s.calibrator.frames_muestreo}",
        "-p", f"show_debug:={_bool_arg(s.calibrator.show_debug)}",
        "-p", "image_topic:=camera/image_raw",
        "-p", f"min_radius:={h.min_radius}",
        "-p", f"max_radius:={h.max_radius}",
        "-p", f"min_dist:={h.min_dist}",
        "-p", f"hough_param1:={h.hough_param1}",
        "-p", f"hough_param2:={h.hough_param2}",
    ]
    url = _camera_info_url()
    if url:
        argv.extend(["-p", f"camera_info_yaml:={url.removeprefix('file://')}"])
    return argv


def _build_detector_argv(s: HmiSettings) -> List[str]:
    h = s.detector.hough
    argv = [
        "ros2", "run", "rec_vision", "detector_tapones",
        "--ros-args",
        "-p", f"frames_muestreo:={s.detector.frames_muestreo}",
        "-p", f"show_debug:={_bool_arg(s.detector.show_debug)}",
        "-p", f"target_frame:={s.detector.target_frame}",
        "-p", f"camera_frame:={s.detector.camera_frame}",
        "-p", "image_topic:=camera/image_raw",
        "-p", f"min_radius:={h.min_radius}",
        "-p", f"max_radius:={h.max_radius}",
        "-p", f"min_dist:={h.min_dist}",
        "-p", f"hough_param1:={h.hough_param1}",
        "-p", f"hough_param2:={h.hough_param2}",
    ]
    url = _camera_info_url()
    if url:
        argv.extend(["-p", f"camera_info_yaml:={url.removeprefix('file://')}"])
    return argv
