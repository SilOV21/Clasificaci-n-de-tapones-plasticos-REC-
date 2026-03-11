# =============================================================================
# LRA Vision Package - Camera Publisher Launch
# Publishes camera images from Logitech StreamCam
# ROS2 Jazzy Jalisco
# =============================================================================

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python import get_package_share_directory
import os


def generate_launch_description():
    # Get package directory
    pkg_dir = FindPackageShare('lra_vision')
    
    # Declare launch arguments
    video_device_arg = DeclareLaunchArgument(
        'video_device',
        default_value='/dev/video2',
        description='Video device path (e.g., /dev/video2 or /dev/video3)'
    )
    
    camera_name_arg = DeclareLaunchArgument(
        'camera_name',
        default_value='logitech_streamcam',
        description='Camera name for namespacing'
    )
    
    frame_id_arg = DeclareLaunchArgument(
        'frame_id',
        default_value='camera_optical_frame',
        description='Frame ID for camera images'
    )
    
    image_width_arg = DeclareLaunchArgument(
        'image_width',
        default_value='1920',
        description='Image width in pixels'
    )
    
    image_height_arg = DeclareLaunchArgument(
        'image_height',
        default_value='1080',
        description='Image height in pixels'
    )
    
    framerate_arg = DeclareLaunchArgument(
        'framerate',
        default_value='30',
        description='Camera framerate'
    )
    
    auto_detect_arg = DeclareLaunchArgument(
        'auto_detect',
        default_value='true',
        description='Auto-detect camera device'
    )
    
    publish_rate_arg = DeclareLaunchArgument(
        'publish_rate',
        default_value='30.0',
        description='Image publishing rate'
    )
    
    config_file_arg = DeclareLaunchArgument(
        'config_file',
        default_value=PathJoinSubstitution([
            pkg_dir, 'config', 'camera_params.yaml'
        ]),
        description='Path to camera configuration file'
    )
    
    # Camera publisher node
    camera_publisher_node = Node(
        package='lra_vision',
        executable='camera_publisher_node',
        name='camera_publisher',
        output='screen',
        parameters=[{
            'video_device': LaunchConfiguration('video_device'),
            'camera_name': LaunchConfiguration('camera_name'),
            'frame_id': LaunchConfiguration('frame_id'),
            'image_width': LaunchConfiguration('image_width'),
            'image_height': LaunchConfiguration('image_height'),
            'framerate': LaunchConfiguration('framerate'),
            'auto_detect': LaunchConfiguration('auto_detect'),
            'publish_rate': LaunchConfiguration('publish_rate'),
        }],
        remappings=[
            ('image_raw', 'camera/image_raw'),
            ('camera_info', 'camera/camera_info'),
        ],
    )
    
    return LaunchDescription([
        video_device_arg,
        camera_name_arg,
        frame_id_arg,
        image_width_arg,
        image_height_arg,
        framerate_arg,
        auto_detect_arg,
        publish_rate_arg,
        config_file_arg,
        camera_publisher_node,
        LogInfo(msg=['LRA Vision: Camera publisher launched on ', LaunchConfiguration('video_device')]),
    ])