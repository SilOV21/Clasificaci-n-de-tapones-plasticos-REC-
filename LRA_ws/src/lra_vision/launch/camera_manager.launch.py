# =============================================================================
# LRA Vision Package - Camera Manager Launch
# Manages v4l2_camera with auto-detection and monitoring
# ROS2 Humble Hawksbill
# =============================================================================

import os
import yaml
import glob
from launch import LaunchDescription
from launch.actions import LogInfo
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def get_best_video_device(default_device, auto_detect):
    if not auto_detect:
        return default_device
        
    # Prefer these devices in order
    preferred = ['/dev/video2', '/dev/video3', '/dev/video0', '/dev/video1']
    for dev in preferred:
        if os.path.exists(dev):
            return dev
            
    # Fallback to any available video device
    available = glob.glob('/dev/video*')
    if available:
        return sorted(available)[0]
        
    return default_device

def read_camera_params():
    """Read camera parameters from YAML and flatten for ROS2."""
    config_path = os.path.join(
        get_package_share_directory('lra_vision'),
        'config',
        'camera_params.yaml'
    )

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    video_device = get_best_video_device(
        config['camera']['video_device'], 
        config['camera']['auto_detect']
    )

    # Flatten nested structure for ROS2 parameters
    params = {
        # Camera settings
        'camera.video_device': video_device,
        'camera.name': config['camera']['name'],
        'camera.resolution.width': config['camera']['resolution']['width'],
        'camera.resolution.height': config['camera']['resolution']['height'],
        'camera.resolution.framerate': config['camera']['resolution']['framerate'],
        'camera.pixel_format': config['camera']['pixel_format'],
        'camera.auto_detect': False, # handled in python

        # Topics
        'topics.image_raw': config['topics']['image_raw'],
        'topics.camera_info': config['topics']['camera_info'],

        # Frames
        'frames.optical_frame': config['frames']['optical_frame']
    }

    return params


def generate_launch_description():
    # Read parameters from YAML
    params = read_camera_params()

    # v4l2_camera node
    v4l2_camera_node = Node(
        package='v4l2_camera',
        executable='v4l2_camera_node',
        name='v4l2_camera',
        output='screen',
        parameters=[{
            'video_device': params['camera.video_device'],
            'image_size': [params['camera.resolution.width'], params['camera.resolution.height']],
            'time_per_frame': [1, params['camera.resolution.framerate']],
            'pixel_format': params['camera.pixel_format'],
            'camera_frame_id': params['frames.optical_frame']
        }],
        remappings=[
            ('image_raw', params['topics.image_raw']),
            ('camera_info', params['topics.camera_info']),
        ]
    )

    return LaunchDescription([
        LogInfo(msg=[f"LRA Vision: Launching v4l2_camera on device {params['camera.video_device']}"]),
        v4l2_camera_node,
    ])
