"""Background thread that pings the UR3e robot and emits connection status."""
from __future__ import annotations

import subprocess

from PyQt5.QtCore import QThread, pyqtSignal


class ConnectionMonitor(QThread):
    status_changed = pyqtSignal(bool, float)

    def __init__(self, robot_ip: str, interval_s: float = 2.0, parent=None):
        super().__init__(parent)
        self._robot_ip = robot_ip
        self._interval_s = interval_s
        self._stop_requested = False
        self._last_reachable: bool = False
        self._last_emitted: bool = False
        self._first_emit_pending: bool = True

    def set_robot_ip(self, ip: str) -> None:
        self._robot_ip = ip
        self._first_emit_pending = True

    def request_stop(self) -> None:
        self._stop_requested = True

    def run(self) -> None:
        while not self._stop_requested:
            reachable, rtt = self._ping_once()
            if self._first_emit_pending or reachable != self._last_emitted:
                self.status_changed.emit(reachable, rtt)
                self._last_emitted = reachable
                self._first_emit_pending = False
            self._last_reachable = reachable
            self.msleep(int(self._interval_s * 1000))

    def _ping_once(self) -> tuple[bool, float]:
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", self._robot_ip],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=2.0,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, float("nan")
        if result.returncode != 0:
            return False, float("nan")
        rtt = self._parse_rtt(result.stdout.decode(errors="ignore"))
        return True, rtt

    @staticmethod
    def _parse_rtt(stdout: str) -> float:
        for token in stdout.split():
            if token.startswith("time="):
                try:
                    return float(token.split("=", 1)[1])
                except ValueError:
                    pass
        return float("nan")
