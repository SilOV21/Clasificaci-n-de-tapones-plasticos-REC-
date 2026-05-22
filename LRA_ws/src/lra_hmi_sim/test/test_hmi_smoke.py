"""Headless smoke tests for lra_hmi.

Runs the GUI with QT_QPA_PLATFORM=offscreen and a stub ProcessManager
that records calls instead of spawning subprocesses. A real RosBridge is
connected to an in-process publisher node so we can verify the data flow
from /topic → Qt signal → widget state.
"""
from __future__ import annotations

import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
import rclpy
from cv_bridge import CvBridge
from PyQt5.QtCore import QObject, Qt, pyqtSignal
from rclpy.node import Node
from sensor_msgs.msg import Image, JointState
from std_msgs.msg import Bool, Int32, String

from lra_hmi.process_manager import GroupState, ProcessManager
from lra_hmi.ros_bridge import RosBridge
from lra_hmi.ui.main_window import MainWindow
from lra_hmi.ui.settings_dialog import HmiSettings
from lra_hmi.ui.widgets import STATE_COLORS

from lra_hmi_sim.image_factory import make_cap_frame


class StubProcessManager(ProcessManager):
    """A ProcessManager that never spawns real processes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calls: list[tuple[str, str | None]] = []

    def start(self, key: str) -> bool:
        self.calls.append(("start", key))
        self._set_state(key, GroupState.RUNNING)
        return True

    def stop(self, key: str, hard: bool = False, timeout_s: float = 5.0) -> bool:
        self.calls.append(("stop", key))
        self._set_state(key, GroupState.STOPPED)
        return True

    def restart(self, key: str) -> bool:
        self.calls.append(("restart", key))
        self._set_state(key, GroupState.RUNNING)
        return True

    def start_all(self) -> None:
        self.calls.append(("start_all", None))
        for k in self.keys():
            self._set_state(k, GroupState.RUNNING)

    def stop_all(self, hard: bool = False) -> None:
        self.calls.append(("stop_all", None))
        for k in self.keys():
            self._set_state(k, GroupState.STOPPED)

    def emergency_stop(self) -> None:
        self.calls.append(("emergency_stop", None))
        for k in self.keys():
            self._set_state(k, GroupState.STOPPED)

    def shutdown(self) -> None:
        pass


class _Publisher(Node):
    """In-process publisher used to drive the HMI's RosBridge."""

    def __init__(self):
        super().__init__("hmi_smoke_test_publisher")
        self._bridge = CvBridge()
        self._caja_pub = self.create_publisher(Int32, "/tapones/caja_asignada", 10)
        self._color_pub = self.create_publisher(String, "/vision_color", 10)
        self._joint_pub = self.create_publisher(JointState, "/joint_states", 10)
        self._image_pub = self.create_publisher(Image, "/image_raw", 5)
        self._debug_pub = self.create_publisher(Image, "/tapones/imagen_debug", 5)
        self._enable_received: list[bool] = []
        self._enable_sub = self.create_subscription(
            Bool, "/vision_enable", self._on_enable, 10
        )

    def _on_enable(self, msg: Bool) -> None:
        self._enable_received.append(bool(msg.data))

    def publish_box(self, box_id: int) -> None:
        m = Int32()
        m.data = box_id
        self._caja_pub.publish(m)

    def publish_color(self, color: str) -> None:
        m = String()
        m.data = color
        self._color_pub.publish(m)

    def publish_joints(self) -> None:
        m = JointState()
        m.name = [
            "shoulder_pan_joint",
            "shoulder_lift_joint",
            "elbow_joint",
            "wrist_1_joint",
            "wrist_2_joint",
            "wrist_3_joint",
        ]
        m.position = [0.1, -1.4, 0.5, -1.2, 1.5, 0.8]
        self._joint_pub.publish(m)

    def publish_image(self) -> None:
        frame = make_cap_frame("rojo", 0.0)
        msg = self._bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        self._image_pub.publish(msg)
        self._debug_pub.publish(msg)


class _StubConnMonitor(QObject):
    """Stand-in for ConnectionMonitor that never pings or starts threads."""

    status_changed = pyqtSignal(bool, float)

    def set_robot_ip(self, _ip: str) -> None:
        pass

    def start(self) -> None:
        pass

    def request_stop(self) -> None:
        pass

    def wait(self, _ms: int) -> None:
        pass


@pytest.fixture
def hmi(qtbot, rclpy_session):
    """Build a MainWindow plus the in-process test publisher."""
    settings = HmiSettings(robot_ip="127.0.0.1", ur_type="ur3e", num_boxes=4)
    ros_bridge = RosBridge(node_name=f"lra_hmi_test_{int(time.time()*1000)%10**9}")
    pm = StubProcessManager(robot_ip="127.0.0.1", ur_type="ur3e")
    conn = _StubConnMonitor()

    window = MainWindow(
        ros_bridge=ros_bridge,
        process_manager=pm,
        connection_monitor=conn,
        settings=settings,
    )
    qtbot.addWidget(window)
    window.show()

    publisher = _Publisher()

    def pump():
        for _ in range(5):
            rclpy.spin_once(publisher, timeout_sec=0.0)
            ros_bridge.spin_once(timeout_sec=0.0)
            qtbot.wait(10)

    yield window, pm, publisher, ros_bridge, pump

    publisher.destroy_node()
    try:
        ros_bridge.node.destroy_node()
    except Exception:
        pass


def test_window_builds(hmi):
    window, _, _, _, _ = hmi
    assert window.isVisible()
    assert window._launcher_panel is not None
    assert window._status_panel is not None
    assert window._counters_panel is not None
    assert window._camera_panel_dashboard is not None
    assert window._camera_panel_full is not None
    assert window._log_panel is not None


def test_counters_react(hmi, qtbot):
    window, _, publisher, _, pump = hmi
    panel = window._counters_panel

    publisher.publish_box(1)
    publisher.publish_box(2)
    publisher.publish_box(1)

    qtbot.waitUntil(lambda: (pump(), panel._total >= 3)[1], timeout=3000)
    assert panel._total >= 3
    assert panel._boxes[1].value() >= 2
    assert panel._boxes[2].value() >= 1


def test_color_swatch_reacts(hmi, qtbot):
    window, _, publisher, _, pump = hmi
    swatch = window._status_panel._swatch

    publisher.publish_color("rojo")

    qtbot.waitUntil(lambda: (pump(), swatch.text() == "ROJO")[1], timeout=3000)
    assert swatch.text() == "ROJO"
    assert "#e74c3c" in swatch.styleSheet()


def test_joint_stream_live_then_stale(hmi, qtbot):
    window, _, publisher, _, pump = hmi
    status = window._status_panel

    publisher.publish_joints()
    qtbot.waitUntil(
        lambda: (pump(), status._joint_stream_label.text() == "live")[1],
        timeout=3000,
    )
    assert status._joint_stream_label.text() == "live"
    assert any(
        label.text() != "—" for label in status._joint_value_labels
    )

    deadline = time.time() + 4.0
    while time.time() < deadline:
        pump()
        qtbot.wait(50)
        if status._joint_stream_label.text().startswith("no data"):
            break
    assert status._joint_stream_label.text().startswith("no data")


def test_camera_renders(hmi, qtbot):
    window, _, publisher, _, pump = hmi
    cam = window._camera_panel_dashboard

    for _ in range(3):
        publisher.publish_image()

    def has_pixmap() -> bool:
        pump()
        pix = cam._view.pixmap()
        return pix is not None and not pix.isNull()

    qtbot.waitUntil(has_pixmap, timeout=3000)
    pix = cam._view.pixmap()
    assert pix is not None
    assert pix.width() > 0 and pix.height() > 0


def test_state_led_follows_process_state(hmi, qtbot):
    window, pm, _, _, _ = hmi
    led = window._launcher_panel._leds["driver"]

    pm._set_state("driver", GroupState.RUNNING)
    qtbot.wait(50)
    assert led._color.name().lower() == STATE_COLORS["running"].lower()

    pm._set_state("driver", GroupState.CRASHED)
    qtbot.wait(50)
    assert led._color.name().lower() == STATE_COLORS["crashed"].lower()


def test_emergency_stop_invokes_pm_and_publishes(hmi, qtbot, monkeypatch):
    window, pm, publisher, _, pump = hmi

    monkeypatch.setattr(
        "lra_hmi.ui.main_window.QMessageBox.critical",
        lambda *a, **kw: None,
    )

    qtbot.mouseClick(window._estop_btn, Qt.LeftButton)
    qtbot.waitUntil(lambda: ("emergency_stop", None) in pm.calls, timeout=1000)

    deadline = time.time() + 2.0
    while time.time() < deadline and not publisher._enable_received:
        pump()
        qtbot.wait(50)

    assert ("emergency_stop", None) in pm.calls
    assert publisher._enable_received
    assert publisher._enable_received[-1] is False
