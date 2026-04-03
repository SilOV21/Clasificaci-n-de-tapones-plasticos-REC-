import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
from std_msgs.msg import Bool, String
import random


class VisionFakeSort(Node):

    def __init__(self):
        super().__init__('vision_fake_sort')

        self.target_pub = self.create_publisher(Point, '/vision_target', 10)
        self.color_pub = self.create_publisher(String, '/vision_color', 10)

        self.subscription = self.create_subscription(
            Bool,
            '/vision_enable',
            self.enable_callback,
            10
        )

        self.vision_enabled = False
        self.timer = self.create_timer(2.0, self.send_target)
        self.last_xyz = None

        self.colors = ['rojo', 'azul', 'verde', 'amarillo']

        self.pick_points = [
            (-0.38, 0.20, 0.05),
            (-0.30, 0.15, 0.05),
            (-0.32, 0.22, 0.05), 
            (-0.25, 0.20, 0.05),
            (-0.34, 0.15, 0.05),
            (-0.33, 0.20, 0.05),
            (-0.25, 0.28, 0.05),
            (-0.31, 0.24, 0.05),
        ]

        self.get_logger().info('Vision iniciada APAGADA')

    def enable_callback(self, msg):
        self.vision_enabled = msg.data
        self.get_logger().info(f'Vision enabled = {self.vision_enabled}')

    def send_target(self):
        if not self.vision_enabled:
            return

        if len(self.pick_points) == 1:
            xyz = self.pick_points[0]
        else:
            xyz = random.choice(self.pick_points)
            max_tries = 20
            tries = 0

            while self.last_xyz is not None and xyz == self.last_xyz and tries < max_tries:
                xyz = random.choice(self.pick_points)
                tries += 1

        self.last_xyz = xyz

        point_msg = Point()
        point_msg.x = xyz[0]
        point_msg.y = xyz[1]
        point_msg.z = xyz[2]

        color_msg = String()
        color_msg.data = random.choice(self.colors)

        self.target_pub.publish(point_msg)
        self.color_pub.publish(color_msg)

        self.get_logger().info(
            f'Target detected -> x={point_msg.x:.3f}, '
            f'y={point_msg.y:.3f}, z={point_msg.z:.3f}, '
            f'color={color_msg.data}'
        )

        self.vision_enabled = False
        self.get_logger().info('Vision se auto-desactiva tras enviar objetivo')


def main(args=None):
    rclpy.init(args=args)
    node = VisionFakeSort()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
