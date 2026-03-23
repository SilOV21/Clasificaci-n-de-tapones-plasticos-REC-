#!/usr/bin/env python3
# =============================================================================
# LRA Vision Package - Camera Info Publisher
# Publishes camera calibration data from YAML file
# ROS2 Jazzy Jalisco
# =============================================================================

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
import yaml
import os


class CameraInfoPublisher(Node):
    """Publishes camera calibration data from YAML file."""

    def __init__(self):
        super().__init__('camera_info_publisher')

        # Parameters
        self.declare_parameter('calibration_file',
                               '~/.ros/camera_calibration/camera_info.yaml')
        self.declare_parameter('camera_info_topic', 'camera/camera_info')
        self.declare_parameter('publish_rate', 10.0)
        self.declare_parameter('frame_id', 'camera_optical_frame')

        calibration_file = self.get_parameter('calibration_file').get_parameter_value().string_value
        camera_info_topic = self.get_parameter('camera_info_topic').get_parameter_value().string_value
        publish_rate = self.get_parameter('publish_rate').get_parameter_value().double_value
        self.frame_id = self.get_parameter('frame_id').get_parameter_value().string_value

        # Expand path
        calibration_file = os.path.expanduser(calibration_file)

        # Load calibration
        self.camera_info = self.load_calibration(calibration_file)
        if self.camera_info is None:
            self.get_logger().error(f'Failed to load calibration from {calibration_file}')
            raise RuntimeError('Calibration file not found or invalid')

        self.get_logger().info(f'Loaded camera calibration from: {calibration_file}')
        self.get_logger().info(f'Camera: {self.camera_info.width}x{self.camera_info.height}')
        self.get_logger().info(f'Publishing on: {camera_info_topic} at {publish_rate} Hz')

        # Create publisher with reliable QoS for calibration data
        qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL
        )
        self.pub = self.create_publisher(CameraInfo, camera_info_topic, qos)

        # Create timer
        self.timer = self.create_timer(1.0 / publish_rate, self.publish_camera_info)

        # Publish once immediately
        self.publish_camera_info()

    def load_calibration(self, filepath):
        """Load camera calibration from YAML file."""
        try:
            with open(filepath, 'r') as f:
                calib = yaml.safe_load(f)

            info = CameraInfo()
            info.header.frame_id = self.frame_id

            # Image dimensions
            info.width = calib['image_width']
            info.height = calib['image_height']

            # Camera matrix (K)
            camera_matrix = calib['camera_matrix']['data']
            info.k = camera_matrix

            # Distortion coefficients (D)
            dist_coeffs = calib['distortion_coefficients']['data']
            info.d = dist_coeffs

            # Distortion model
            info.distortion_model = 'plumb_bob'

            # Rectification matrix (R) - identity for monocular camera
            rect_matrix = calib['rectification_matrix']['data']
            info.r = rect_matrix

            # Projection matrix (P)
            proj_matrix = calib['projection_matrix']['data']
            # P is 3x4, but CameraInfo expects 12 elements
            info.p = proj_matrix

            self.get_logger().info(f'Camera matrix K: {info.k}')
            self.get_logger().info(f'Distortion coeffs: {info.d}')

            return info

        except FileNotFoundError:
            self.get_logger().error(f'Calibration file not found: {filepath}')
            return None
        except KeyError as e:
            self.get_logger().error(f'Missing key in calibration file: {e}')
            return None
        except Exception as e:
            self.get_logger().error(f'Error loading calibration: {e}')
            return None

    def publish_camera_info(self):
        """Publish camera info message."""
        if self.camera_info is not None:
            self.camera_info.header.stamp = self.get_clock().now().to_msg()
            self.pub.publish(self.camera_info)


def main(args=None):
    rclpy.init(args=args)
    try:
        node = CameraInfoPublisher()
        rclpy.spin(node)
    except RuntimeError as e:
        print(f'Error: {e}')
        return 1
    except KeyboardInterrupt:
        pass
    finally:
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
