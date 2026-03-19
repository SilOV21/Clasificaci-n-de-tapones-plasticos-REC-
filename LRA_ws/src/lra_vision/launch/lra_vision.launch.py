# =============================================================================
# LRA Vision Package - Complete Vision System Launch
# Launches all vision nodes for the REC Project
# ROS2 Jazzy Jalisco
# =============================================================================

import os
import yaml
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration
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
    # Read camera parameters from YAML
    camera_params = read_camera_params()

    # Declare launch arguments
    translation_z_arg = DeclareLaunchArgument(
        'translation_z',
        default_value='0.08',
        description='Camera height above UR3 (meters)'
    )

    calibration_file_arg = DeclareLaunchArgument(
        'calibration_file',
        default_value='',
        description='Path to camera calibration file'
    )

    # Camera manager node
    camera_manager_node = Node(
        package='lra_vision',
        executable='camera_manager_node',
        name='camera_manager',
        output='screen',
        parameters=[camera_params],
    )

    # TF broadcaster node
    tf_broadcaster_node = Node(
        package='lra_vision',
        executable='camera_tf_broadcaster_node',
        name='camera_tf_broadcaster',
        output='screen',
        parameters=[{
            'translation_x': 0.0,
            'translation_y': 0.0,
            'translation_z': LaunchConfiguration('translation_z'),
            'roll': 3.14159,
            'pitch': 0.0,
            'yaw': 0.0,
            'parent_frame': 'tool0',
            'camera_frame': 'camera_link',
            'optical_frame': 'camera_optical_frame',
            'publish_rate': 30.0,
            'static_transform': True,
        }],
    )

    # ArUco detector node
    aruco_detector_node = Node(
        package='lra_vision',
        executable='aruco_detector_node',
        name='aruco_detector',
        output='screen',
        parameters=[{
            'image_topic': 'camera/image_raw',
            'camera_info_topic': 'camera/camera_info',
            'dictionary': 'DICT_4X4_50',
            'marker_size': 0.05,
            'publish_markers': True,
            'publish_poses': True,
            'publish_image': True,
            'calibration_file': LaunchConfiguration('calibration_file'),
        }],
    )

    return LaunchDescription([
        translation_z_arg,
        calibration_file_arg,
        LogInfo(msg=''),
        LogInfo(msg='========================================'),
        LogInfo(msg='LRA Vision System - REC Project'),
        LogInfo(msg='========================================'),
        LogInfo(msg=''),
        LogInfo(msg='Loading config from: camera_params.yaml'),
        LogInfo(msg=''),
        camera_manager_node,
        tf_broadcaster_node,
        aruco_detector_node,
        LogInfo(msg=''),
        LogInfo(msg='LRA Vision: All nodes launched successfully'),
        LogInfo(msg=''),
        LogInfo(msg='Topics:'),
        LogInfo(msg='  - /camera/image_raw'),
        LogInfo(msg='  - /camera/camera_info'),
        LogInfo(msg='  - /camera/status'),
        LogInfo(msg='  - /aruco/markers'),
        LogInfo(msg='  - /aruco/poses'),
        LogInfo(msg=''),
        LogInfo(msg='TF Frames:'),
        LogInfo(msg='  - tool0 -> camera_link -> camera_optical_frame'),
        LogInfo(msg=''),
        LogInfo(msg='Services:'),
        LogInfo(msg='  - /camera/reconnect'),
        LogInfo(msg=''),
        LogInfo(msg='========================================'),
    ])
