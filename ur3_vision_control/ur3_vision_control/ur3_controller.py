import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from geometry_msgs.msg import Point
from std_msgs.msg import Bool


class UR3VisionControl(Node):

    def __init__(self):

        super().__init__('ur3_vision_control')

        self.publisher = self.create_publisher(
            JointTrajectory,
            '/scaled_joint_trajectory_controller/joint_trajectory',
            10
        )

        self.vision_control_pub = self.create_publisher(
            Bool,
            '/vision_enable',
            10
        )

        self.subscription = self.create_subscription(
            Point,
            '/vision_target',
            self.vision_callback,
            10
        )

        self.home_position = [0.0, -1.2, 1.2, -1.5, -1.5, 0.0]

        self.Z_CONST = 0.10

    def vision_callback(self, msg):

        # apagar visión
        disable_msg = Bool()
        disable_msg.data = False
        self.vision_control_pub.publish(disable_msg)

        x = msg.x
        y = msg.y
        z = msg.z

        self.get_logger().info(
            f"Target received: x={x:.3f} y={y:.3f} z={z:.3f}"
        )

        traj = JointTrajectory()

        traj.joint_names = [
            "shoulder_pan_joint",
            "shoulder_lift_joint",
            "elbow_joint",
            "wrist_1_joint",
            "wrist_2_joint",
            "wrist_3_joint"
        ]

        target = JointTrajectoryPoint()
        pan = x * 2.0
        elbow = 1.1 + y
        
        target.positions = [ pan, -1.0, elbow, -1.5, -1.5, 0.2]
        
        target.time_from_start.sec = 2

        home = JointTrajectoryPoint()
        home.positions = self.home_position
        home.time_from_start.sec = 5

        traj.points.append(target)
        traj.points.append(home)

        self.publisher.publish(traj)

        self.get_logger().info("Robot moving")

        # esperar a que termine el movimiento
        self.create_timer(6.0, self.enable_vision)

    def enable_vision(self):

        enable_msg = Bool()
        enable_msg.data = True

        self.vision_control_pub.publish(enable_msg)

        self.get_logger().info("Vision enabled again")


def main():

    rclpy.init()

    node = UR3VisionControl()

    rclpy.spin(node)

    rclpy.shutdown()


if __name__ == '__main__':
    main()
