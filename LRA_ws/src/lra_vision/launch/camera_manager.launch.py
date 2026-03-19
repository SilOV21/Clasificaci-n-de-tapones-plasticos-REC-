# =============================================================================
# LRA Vision Package - Camera Manager Launch
# Manages v4l2_camera with auto-detection and monitoring
# ROS2 Jazzy Jalisco
# =============================================================================

import os
import yaml
from launch import LaunchDescription
from launch.actions import LogInfo
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def read_camera_params():
    """Read camera parameters from YAML and flatten for ROS2."""
    config_path = os.path.join(
        get_package_share_directory('lra_vision'),
        'config',
        'camera_params.yaml'
    )

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Flatten nested structure for ROS2 parameters
    params = {
        # Camera settings
        'camera.video_device': config['camera']['video_device'],
        'camera.name': config['camera']['name'],
        'camera.resolution.width': config['camera']['resolution']['width'],
        'camera.resolution.height': config['camera']['resolution']['height'],
        'camera.resolution.framerate': config['camera']['resolution']['framerate'],
        'camera.pixel_format': config['camera']['pixel_format'],
        'camera.auto_detect': config['camera']['auto_detect'],

        # Topics
        'topics.image_raw': config['topics']['image_raw'],
        'topics.camera_info': config['topics']['camera_info'],

        # Frames
        'frames.optical_frame': config['frames']['optical_frame'],

        # Camera manager specific
        'camera_manager.status_rate': config.get('camera_manager', {}).get('status_rate', 5.0),
    }

    return params


def generate_launch_description():
    # Read parameters from YAML
    params = read_camera_params()

    # Camera manager node
    camera_manager_node = Node(
        package='lra_vision',
        executable='camera_manager_node',
        name='camera_manager',
        output='screen',
        parameters=[params],
    )

    return LaunchDescription([
        camera_manager_node,
        LogInfo(msg=['LRA Vision: Camera manager launched']),
    ])
