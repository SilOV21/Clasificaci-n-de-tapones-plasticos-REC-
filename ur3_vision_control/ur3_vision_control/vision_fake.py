import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from std_msgs.msg import Bool
import random


class VisionFake(Node):

    def __init__(self):

        super().__init__('vision_fake')

        self.publisher = self.create_publisher(Point, '/vision_target', 10)

        self.subscription = self.create_subscription(
            Bool,
            '/vision_enable',
            self.enable_callback,
            10
        )

        self.vision_enabled = True

        self.timer = self.create_timer(15.0, self.send_target)

        self.Z_CONST = 0.10   # mismo Z para todo el sistema

    def enable_callback(self, msg):
        self.vision_enabled = msg.data

    def send_target(self):

        if not self.vision_enabled:
            return

        msg = Point()

        msg.x = random.uniform(0.2, 0.4)
        msg.y = random.uniform(-0.8, 0.2)
        msg.z = self.Z_CONST

        self.publisher.publish(msg)

        self.get_logger().info(
            f"Vision detected target: x={msg.x:.3f} y={msg.y:.3f} z={msg.z:.3f}"
        )


def main():

    rclpy.init()

    node = VisionFake()

    rclpy.spin(node)

    rclpy.shutdown()


if __name__ == '__main__':
    main()
