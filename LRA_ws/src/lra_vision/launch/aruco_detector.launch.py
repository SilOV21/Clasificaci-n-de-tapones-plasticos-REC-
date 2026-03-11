# =============================================================================
# LRA Vision Package - ArUco Detector Launch
# ArUco marker detection for hand-eye calibration
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
    
    camera_info_topic_arg = DeclareLaunchArgument(
        'camera_info_topic',
        default_value='camera/camera_info',
        description='Camera info topic'
    )
    
    dictionary_arg = DeclareLaunchArgument(
        'dictionary',
        default_value='DICT_4X4_50',
        description='ArUco dictionary (DICT_4X4_50, DICT_5X5_50, DICT_6X6_50, etc.)'
    )
    
    marker_size_arg = DeclareLaunchArgument(
        'marker_size',
        default_value='0.05',
        description='Marker size in meters'
    )
    
    publish_markers_arg = DeclareLaunchArgument(
        'publish_markers',
        default_value='true',
        description='Publish visualization markers'
    )
    
    publish_poses_arg = DeclareLaunchArgument(
        'publish_poses',
        default_value='true',
        description='Publish marker poses'
    )
    
    publish_image_arg = DeclareLaunchArgument(
        'publish_image',
        default_value='true',
        description='Publish detected image'
    )
    
    calibration_file_arg = DeclareLaunchArgument(
        'calibration_file',
        default_value='',
        description='Path to camera calibration file (optional)'
    )
    
    # ArUco detector node
    aruco_detector_node = Node(
        package='lra_vision',
        executable='aruco_detector_node',
        name='aruco_detector',
        output='screen',
        parameters=[{
            'image_topic': LaunchConfiguration('image_topic'),
            'camera_info_topic': LaunchConfiguration('camera_info_topic'),
            'dictionary': LaunchConfiguration('dictionary'),
            'marker_size': LaunchConfiguration('marker_size'),
            'publish_markers': LaunchConfiguration('publish_markers'),
            'publish_poses': LaunchConfiguration('publish_poses'),
            'publish_image': LaunchConfiguration('publish_image'),
            'calibration_file': LaunchConfiguration('calibration_file'),
        }],
        remappings=[
            ('aruco/detected_image', 'camera/aruco/detected_image'),
            ('aruco/markers', 'camera/aruco/markers'),
            ('aruco/poses', 'camera/aruco/poses'),
            ('aruco/marker_ids', 'camera/aruco/marker_ids'),
        ],
    )
    
    return LaunchDescription([
        image_topic_arg,
        camera_info_topic_arg,
        dictionary_arg,
        marker_size_arg,
        publish_markers_arg,
        publish_poses_arg,
        publish_image_arg,
        calibration_file_arg,
        aruco_detector_node,
        LogInfo(msg=['LRA Vision: ArUco detector launched']),
        LogInfo(msg=['  Dictionary: ', LaunchConfiguration('dictionary')]),
        LogInfo(msg=['  Marker size: ', LaunchConfiguration('marker_size'), 'm']),
    ])