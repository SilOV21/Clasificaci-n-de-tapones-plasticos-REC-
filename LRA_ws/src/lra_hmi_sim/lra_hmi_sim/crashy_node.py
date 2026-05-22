"""Node that intentionally exits non-zero after `lifetime_s` to test crash detection."""
from __future__ import annotations

import sys

import rclpy
from rclpy.node import Node


class CrashyNode(Node):

    def __init__(self):
        super().__init__("crashy_node")
        self.declare_parameter("lifetime_s", 8.0)
        self._lifetime_s = float(self.get_parameter("lifetime_s").value)
        self.get_logger().info(
            f"crashy_node online: will exit non-zero in {self._lifetime_s}s"
        )
        self._tick_count = 0
        self.create_timer(1.0, self._tick)
        self.create_timer(self._lifetime_s, self._die)

    def _tick(self) -> None:
        self._tick_count += 1
        remaining = self._lifetime_s - self._tick_count
        if remaining > 0:
            self.get_logger().info(f"tick {self._tick_count}, crashing in {remaining:.0f}s")

    def _die(self) -> None:
        self.get_logger().error("crashy_node exiting with code 42 — this is intentional")
        rclpy.shutdown()
        sys.exit(42)


def main(args=None):
    rclpy.init(args=args)
    node = CrashyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except SystemExit:
        raise
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == "__main__":
    main()
