"""rclpy Node bridge: subscribes to system topics, exposes Qt signals."""
from __future__ import annotations

import math
import time
from typing import Optional

import numpy as np
import rclpy
from cv_bridge import CvBridge
from PyQt5.QtCore import QObject, pyqtSignal
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from sensor_msgs.msg import Image, JointState
from std_msgs.msg import Bool, Int32, String


JOINT_ORDER = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]


class RosBridge(QObject):
    """Owns the rclpy Node and re-emits topic data as Qt signals."""

    total_caps_changed = pyqtSignal(int)
    box_assigned = pyqtSignal(int)
    num_boxes_changed = pyqtSignal(int)
    color_changed = pyqtSignal(str)
    joint_states_changed = pyqtSignal(list)
    joint_states_stale = pyqtSignal(bool)
    image_raw_received = pyqtSignal(object)
    image_debug_received = pyqtSignal(object)
    log_message = pyqtSignal(str, str)

    def __init__(self, node_name: str = "lra_hmi"):
        super().__init__()
        if not rclpy.ok():
            rclpy.init()
        self._node: Node = rclpy.create_node(node_name)
        self._bridge = CvBridge()
        self._last_joint_msg_time: Optional[float] = None
        self._joint_stale = True

        latched_qos = QoSProfile(
            depth=1,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
            history=QoSHistoryPolicy.KEEP_LAST,
        )
        sensor_qos = QoSProfile(
            depth=5,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
            history=QoSHistoryPolicy.KEEP_LAST,
        )

        self._subs = [
            self._node.create_subscription(
                Int32, "/tapones/cantidad", self._on_total_caps, 10),
            self._node.create_subscription(
                Int32, "/tapones/caja_asignada", self._on_box_assigned, 10),
            self._node.create_subscription(
                Int32, "/clasificador/num_cajas", self._on_num_boxes, latched_qos),
            self._node.create_subscription(
                String, "/vision_color", self._on_color, 10),
            self._node.create_subscription(
                JointState, "/joint_states", self._on_joint_state, sensor_qos),
            self._node.create_subscription(
                Image, "/camera/image_raw", self._on_image_raw, sensor_qos),
            self._node.create_subscription(
                Image, "/tapones/imagen_debug", self._on_image_debug, sensor_qos),
        ]

        self._vision_enable_pub = self._node.create_publisher(Bool, "/vision_enable", 10)

    @property
    def node(self) -> Node:
        return self._node

    def spin_once(self, timeout_sec: float = 0.0) -> None:
        try:
            rclpy.spin_once(self._node, timeout_sec=timeout_sec)
        except Exception as exc:
            self.log_message.emit("ros", f"[warn] spin_once: {exc}")
        now = time.time()
        if self._last_joint_msg_time is None:
            stale = True
        else:
            stale = (now - self._last_joint_msg_time) > 2.0
        if stale != self._joint_stale:
            self._joint_stale = stale
            self.joint_states_stale.emit(stale)

    def publish_vision_enable(self, enabled: bool) -> None:
        msg = Bool()
        msg.data = bool(enabled)
        self._vision_enable_pub.publish(msg)
        self.log_message.emit("ros", f"[info] published /vision_enable={enabled}")

    def shutdown(self) -> None:
        try:
            self._node.destroy_node()
        except Exception:
            pass
        if rclpy.ok():
            try:
                rclpy.shutdown()
            except Exception:
                pass

    def _on_total_caps(self, msg: Int32) -> None:
        self.total_caps_changed.emit(int(msg.data))

    def _on_box_assigned(self, msg: Int32) -> None:
        self.box_assigned.emit(int(msg.data))

    def _on_num_boxes(self, msg: Int32) -> None:
        self.num_boxes_changed.emit(int(msg.data))

    def _on_color(self, msg: String) -> None:
        self.color_changed.emit(str(msg.data))

    def _on_joint_state(self, msg: JointState) -> None:
        self._last_joint_msg_time = time.time()
        if self._joint_stale:
            self._joint_stale = False
            self.joint_states_stale.emit(False)
        positions = self._reorder_joints(msg)
        self.joint_states_changed.emit(positions)

    def _reorder_joints(self, msg: JointState) -> list:
        name_to_pos = {name: pos for name, pos in zip(msg.name, msg.position)}
        result = []
        for j in JOINT_ORDER:
            if j in name_to_pos:
                result.append(math.degrees(name_to_pos[j]))
            else:
                result.append(float("nan"))
        return result

    def _on_image_raw(self, msg: Image) -> None:
        img = self._to_bgr(msg)
        if img is not None:
            self.image_raw_received.emit(img)

    def _on_image_debug(self, msg: Image) -> None:
        img = self._to_bgr(msg)
        if img is not None:
            self.image_debug_received.emit(img)

    def _to_bgr(self, msg: Image) -> Optional[np.ndarray]:
        try:
            return self._bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as exc:
            self.log_message.emit("ros", f"[warn] cv_bridge: {exc}")
            return None
