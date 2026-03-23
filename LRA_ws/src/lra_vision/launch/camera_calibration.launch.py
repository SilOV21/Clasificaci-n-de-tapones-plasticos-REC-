# =============================================================================
# LRA Vision Package - Camera Calibration Launch
# Interactive camera calibration using chessboard pattern
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
    image_topic_arg = DeclareLaunchArgument(
        'image_topic',
        default_value='camera/image_raw',
        description='Input image topic'
    )

    board_width_arg = DeclareLaunchArgument(
        'board_width',
        default_value='8',
        description='Chessboard width (inner corners)'
    )

    board_height_arg = DeclareLaunchArgument(
        'board_height',
        default_value='5',
        description='Chessboard height (inner corners)'
    )

    square_size_arg = DeclareLaunchArgument(
        'square_size',
        default_value='0.015',
        description='Chessboard square size in meters'
    )

    min_images_arg = DeclareLaunchArgument(
        'min_images',
        default_value='30',
        description='Minimum images for calibration'
    )

    max_images_arg = DeclareLaunchArgument(
        'max_images',
        default_value='100',
        description='Maximum images for calibration'
    )

    auto_capture_arg = DeclareLaunchArgument(
        'auto_capture',
        default_value='false',
        description='Auto-capture images when pattern detected'
    )

    capture_interval_arg = DeclareLaunchArgument(
        'capture_interval',
        default_value='2.0',
        description='Interval between auto-captures in seconds'
    )

    visualize_arg = DeclareLaunchArgument(
        'visualize',
        default_value='true',
        description='Visualize detected chessboard'
    )

    camera_name_arg = DeclareLaunchArgument(
        'camera_name',
        default_value='logitech_streamcam',
        description='Camera name for calibration file'
    )

    save_path_arg = DeclareLaunchArgument(
        'save_path',
        default_value='~/.ros/camera_calibration/',
        description='Path to save calibration files'
    )

    output_file_arg = DeclareLaunchArgument(
        'output_file',
        default_value='camera_info.yaml',
        description='Output calibration filename'
    )

    # Camera calibrator node
    camera_calibrator_node = Node(
        package='lra_vision',
        executable='camera_calibrator_node',
        name='camera_calibrator',
        output='screen',
        parameters=[{
            'image_topic': LaunchConfiguration('image_topic'),
            'board_width': LaunchConfiguration('board_width'),
            'board_height': LaunchConfiguration('board_height'),
            'square_size': LaunchConfiguration('square_size'),
            'min_images': LaunchConfiguration('min_images'),
            'max_images': LaunchConfiguration('max_images'),
            'auto_capture': LaunchConfiguration('auto_capture'),
            'capture_interval': LaunchConfiguration('capture_interval'),
            'visualize': LaunchConfiguration('visualize'),
            'camera_name': LaunchConfiguration('camera_name'),
            'save_path': LaunchConfiguration('save_path'),
            'output_file': LaunchConfiguration('output_file'),
        }],
        remappings=[
            ('calibration/debug', 'camera/calibration/debug'),
            ('calibration/status', 'camera/calibration/status'),
            ('calibration/ready', 'camera/calibration/ready'),
        ],
    )

    return LaunchDescription([
        image_topic_arg,
        board_width_arg,
        board_height_arg,
        square_size_arg,
        min_images_arg,
        max_images_arg,
        auto_capture_arg,
        capture_interval_arg,
        visualize_arg,
        camera_name_arg,
        save_path_arg,
        output_file_arg,
        camera_calibrator_node,
        LogInfo(msg=['LRA Vision: Camera calibrator launched']),
        LogInfo(msg=['  Chessboard: ', LaunchConfiguration(
            'board_width'), 'x', LaunchConfiguration('board_height')]),
        LogInfo(msg=['  Square size: ',
                LaunchConfiguration('square_size'), 'm']),
    ])
