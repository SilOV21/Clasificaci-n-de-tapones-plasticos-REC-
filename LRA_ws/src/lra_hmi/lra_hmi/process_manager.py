"""Process manager for the three launch groups: UR driver, TF publisher, vision stack."""
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

    def __init__(self, robot_ip: str = "169.254.12.28", ur_type: str = "ur3e"):
        super().__init__()
        self._robot_ip = robot_ip
        self._ur_type = ur_type
        self._lock = Lock()

        self._groups: Dict[str, GroupSpec] = {}
        self._runtime: Dict[str, GroupRuntime] = {}
        self._register_default_groups()

    @staticmethod
    def is_sim_mode() -> bool:
        return os.environ.get("LRA_HMI_SIM", "").strip() not in ("", "0", "false", "False")

    def _register_default_groups(self) -> None:
        sim = self.is_sim_mode()
        prefix = "[SIM] " if sim else ""

        if sim:
            driver_argv = lambda: ["ros2", "run", "lra_hmi_sim", "fake_ur_driver"]
            vision_argv = lambda: [
                "ros2", "launch", "lra_hmi_sim", "simulation.launch.py",
            ]
        else:
            driver_argv = lambda: [
                "ros2", "launch", "ur_robot_driver", "ur_control.launch.py",
                f"ur_type:={self._ur_type}",
                f"robot_ip:={self._robot_ip}",
            ]
            vision_argv = lambda: [
                "ros2", "launch", "ur3_vision_control", "launch.py",
            ]

        self._register(
            GroupSpec(
                key="driver",
                label=f"{prefix}UR Driver",
                argv_factory=driver_argv,
                startup_delay_s=2.0,
            )
        )
        self._register(
            GroupSpec(
                key="tf",
                label=f"{prefix}TF Publisher",
                argv_factory=lambda: [
                    "ros2", "run", "tf2_ros", "static_transform_publisher",
                    "0", "0", "0", "0", "0", "0", "world", "base_link",
                ],
                startup_delay_s=0.5,
            )
        )
        self._register(
            GroupSpec(
                key="vision",
                label=f"{prefix}Vision & MoveIt",
                argv_factory=vision_argv,
                startup_delay_s=0.0,
            )
        )

    def _register(self, spec: GroupSpec) -> None:
        self._groups[spec.key] = spec
        self._runtime[spec.key] = GroupRuntime()

    def keys(self) -> List[str]:
        return list(self._groups.keys())

    def label(self, key: str) -> str:
        return self._groups[key].label

    def state(self, key: str) -> GroupState:
        return self._runtime[key].state

    def set_robot_ip(self, ip: str) -> None:
        self._robot_ip = ip

    def set_ur_type(self, ur_type: str) -> None:
        self._ur_type = ur_type

    def robot_ip(self) -> str:
        return self._robot_ip

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
