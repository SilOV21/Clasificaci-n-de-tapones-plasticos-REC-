"""Subscribes to /vision_enable and prints every received message.

Used in simulation to verify the HMI publishes correctly on Vision toggle
and Emergency Stop.
"""
from __future__ import annotations

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool


class VisionEnableLogger(Node):

    def __init__(self):
        super().__init__("vision_enable_logger")
        self._sub = self.create_subscription(
            Bool, "/vision_enable", self._on_msg, 10
        )
        self.get_logger().info("vision_enable_logger online: subscribed to /vision_enable")

    def _on_msg(self, msg: Bool) -> None:
        self.get_logger().info(
            f">>> /vision_enable received: data={msg.data}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = VisionEnableLogger()
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
