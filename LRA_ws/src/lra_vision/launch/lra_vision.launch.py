# =============================================================================
# LRA Vision Package - Complete Vision System Launch
# Launches all vision nodes for the REC Project
# ROS2 Jazzy Jalisco
# =============================================================================

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, GroupAction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Get package directory
    pkg_dir = FindPackageShare('lra_vision')
    
    # Declare launch arguments
    video_device_arg = DeclareLaunchArgument(
        'video_device',
        default_value='/dev/video2',
        description='Video device path'
    )
    
    camera_name_arg = DeclareLaunchArgument(
        'camera_name',
        default_value='logitech_streamcam',
        description='Camera name'
    )
    
    calibration_file_arg = DeclareLaunchArgument(
        'calibration_file',
        default_value='',
        description='Path to camera calibration file'
    )
    
    board_width_arg = DeclareLaunchArgument(
        'board_width',
        default_value='9',
        description='Chessboard width'
    )
    
    board_height_arg = DeclareLaunchArgument(
        'board_height',
        default_value='6',
        description='Chessboard height'
    )
    
    translation_z_arg = DeclareLaunchArgument(
        'translation_z',
        default_value='0.05',
        description='Camera height above UR3 (meters)'
    )
    
    use_namespace_arg = DeclareLaunchArgument(
        'use_namespace',
        default_value='false',
        description='Use namespace for nodes'
    )
    
    namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='lra_vision',
        description='Namespace for nodes'
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
            'frame_id': 'camera_optical_frame',
            'image_width': 1920,
            'image_height': 1080,
            'framerate': 30,
            'auto_detect': True,
            'publish_rate': 30.0,
        }],
        remappings=[
            ('image_raw', 'camera/image_raw'),
            ('camera_info', 'camera/camera_info'),
        ],
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
            'roll': 0.0,
            'pitch': 3.14159,  # 180 degrees (pointing down)
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
    
    # Calibrator node (optional - can be started separately)
    # calibrator_node = Node(...)
    
    return LaunchDescription([
        video_device_arg,
        camera_name_arg,
        calibration_file_arg,
        board_width_arg,
        board_height_arg,
        translation_z_arg,
        use_namespace_arg,
        namespace_arg,
        LogInfo(msg=''),
        LogInfo(msg='========================================'),
        LogInfo(msg='LRA Vision System - REC Project'),
        LogInfo(msg='========================================'),
        LogInfo(msg=''),
        LogInfo(msg=['Camera: ', LaunchConfiguration('camera_name')]),
        LogInfo(msg=['Device: ', LaunchConfiguration('video_device')]),
        LogInfo(msg=['Height above UR3: ', LaunchConfiguration('translation_z'), 'm']),
        LogInfo(msg=''),
        camera_publisher_node,
        tf_broadcaster_node,
        aruco_detector_node,
        LogInfo(msg=''),
        LogInfo(msg='LRA Vision: All nodes launched successfully'),
        LogInfo(msg=''),
        LogInfo(msg='Topics:'),
        LogInfo(msg='  - /camera/image_raw'),
        LogInfo(msg='  - /camera/camera_info'),
        LogInfo(msg='  - /camera/aruco/markers'),
        LogInfo(msg='  - /camera/aruco/poses'),
        LogInfo(msg=''),
        LogInfo(msg='TF Frames:'),
        LogInfo(msg='  - tool0 -> camera_link -> camera_optical_frame'),
        LogInfo(msg=''),
        LogInfo(msg='========================================'),
    ])