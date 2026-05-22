"""Fake UR driver: publishes /joint_states with smooth sine motion."""
from __future__ import annotations

import math
import sys
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


JOINT_NAMES = [
    "shoulder_pan_joint",
    "shoulder_lift_joint",
    "elbow_joint",
    "wrist_1_joint",
    "wrist_2_joint",
    "wrist_3_joint",
]

CENTERS_DEG = [0.0, -90.0, 0.0, -90.0, 0.0, 0.0]
AMPLITUDES_DEG = [40.0, 25.0, 35.0, 30.0, 45.0, 60.0]
FREQUENCIES_HZ = [0.10, 0.12, 0.08, 0.15, 0.20, 0.07]


class FakeUrDriver(Node):

    def __init__(self):
        super().__init__("fake_ur_driver")
        self.declare_parameter("rate_hz", 50.0)
        self.declare_parameter("crash_after_s", 0.0)

        self._rate_hz = float(self.get_parameter("rate_hz").value)
        self._crash_after_s = float(self.get_parameter("crash_after_s").value)

        self._pub = self.create_publisher(JointState, "/joint_states", 20)
        self._started_at = time.time()
        period = 1.0 / max(self._rate_hz, 1.0)
        self._timer = self.create_timer(period, self._tick)
        self.get_logger().info(
            f"fake_ur_driver online: rate={self._rate_hz} Hz, "
            f"crash_after_s={self._crash_after_s}"
        )

    def _tick(self) -> None:
        now = time.time()
        elapsed = now - self._started_at

        if self._crash_after_s > 0 and elapsed >= self._crash_after_s:
            self.get_logger().error(
                f"fake_ur_driver intentionally exiting (after {elapsed:.1f}s) "
                "to simulate a crash"
            )
            rclpy.shutdown()
            sys.exit(42)

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(JOINT_NAMES)
        msg.position = [
            math.radians(c + a * math.sin(2 * math.pi * f * elapsed))
            for c, a, f in zip(CENTERS_DEG, AMPLITUDES_DEG, FREQUENCIES_HZ)
        ]
        msg.velocity = [
            math.radians(a * 2 * math.pi * f * math.cos(2 * math.pi * f * elapsed))
            for a, f in zip(AMPLITUDES_DEG, FREQUENCIES_HZ)
        ]
        self._pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = FakeUrDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
