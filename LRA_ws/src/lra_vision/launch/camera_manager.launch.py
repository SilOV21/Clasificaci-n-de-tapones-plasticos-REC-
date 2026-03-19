# =============================================================================
# LRA Vision Package - Camera Manager Launch
# Manages v4l2_camera with auto-detection and monitoring
# ROS2 Jazzy Jalisco
# =============================================================================

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


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
        default_value='640',
        description='Image width in pixels'
    )

    image_height_arg = DeclareLaunchArgument(
        'image_height',
        default_value='480',
        description='Image height in pixels'
    )

    framerate_arg = DeclareLaunchArgument(
        'framerate',
        default_value='60',
        description='Camera framerate'
    )

    pixel_format_arg = DeclareLaunchArgument(
        'pixel_format',
        default_value='YUYV',
        description='Pixel format (YUYV, MJPG, etc.)'
    )

    auto_detect_arg = DeclareLaunchArgument(
        'auto_detect',
        default_value='true',
        description='Auto-detect camera device'
    )

    image_topic_arg = DeclareLaunchArgument(
        'image_topic',
        default_value='camera/image_raw',
        description='Image topic name'
    )

    camera_info_topic_arg = DeclareLaunchArgument(
        'camera_info_topic',
        default_value='camera/camera_info',
        description='Camera info topic name'
    )

    status_rate_arg = DeclareLaunchArgument(
        'status_rate',
        default_value='5.0',
        description='Status publishing rate in Hz'
    )

    config_file_arg = DeclareLaunchArgument(
        'config_file',
        default_value=PathJoinSubstitution([
            pkg_dir, 'config', 'camera_params.yaml'
        ]),
        description='Path to camera configuration file'
    )

    # Camera manager node
    camera_manager_node = Node(
        package='lra_vision',
        executable='camera_manager_node',
        name='camera_manager',
        output='screen',
        parameters=[{
            'video_device': LaunchConfiguration('video_device'),
            'camera_name': LaunchConfiguration('camera_name'),
            'frame_id': LaunchConfiguration('frame_id'),
            'image_width': LaunchConfiguration('image_width'),
            'image_height': LaunchConfiguration('image_height'),
            'framerate': LaunchConfiguration('framerate'),
            'pixel_format': LaunchConfiguration('pixel_format'),
            'auto_detect': LaunchConfiguration('auto_detect'),
            'image_topic': LaunchConfiguration('image_topic'),
            'camera_info_topic': LaunchConfiguration('camera_info_topic'),
            'status_rate': LaunchConfiguration('status_rate'),
        }],
    )

    return LaunchDescription([
        video_device_arg,
        camera_name_arg,
        frame_id_arg,
        image_width_arg,
        image_height_arg,
        framerate_arg,
        pixel_format_arg,
        auto_detect_arg,
        image_topic_arg,
        camera_info_topic_arg,
        status_rate_arg,
        config_file_arg,
        camera_manager_node,
        LogInfo(msg=['LRA Vision: Camera manager launched']),
    ])
