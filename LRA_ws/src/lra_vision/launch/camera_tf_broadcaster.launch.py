# =============================================================================
# LRA Vision Package - TF Broadcaster Launch
# Publishes TF transforms for camera-UR3 relationship
# ROS2 Humble Hawksbill
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
    translation_x_arg = DeclareLaunchArgument(
        'translation_x',
        default_value='0.0',
        description='Camera translation X from parent frame (meters)'
    )
    
    translation_y_arg = DeclareLaunchArgument(
        'translation_y',
        default_value='0.0',
        description='Camera translation Y from parent frame (meters)'
    )
    
    translation_z_arg = DeclareLaunchArgument(
        'translation_z',
        default_value='0.05',
        description='Camera translation Z from parent frame (meters) - 5cm above UR3'
    )
    
    roll_arg = DeclareLaunchArgument(
        'roll',
        default_value='0.0',
        description='Camera roll angle (radians)'
    )
    
    pitch_arg = DeclareLaunchArgument(
        'pitch',
        default_value='3.14159',
        description='Camera pitch angle (radians) - PI for downward facing'
    )
    
    yaw_arg = DeclareLaunchArgument(
        'yaw',
        default_value='0.0',
        description='Camera yaw angle (radians)'
    )
    
    parent_frame_arg = DeclareLaunchArgument(
        'parent_frame',
        default_value='tool0',
        description='Parent frame (UR3 end effector)'
    )
    
    camera_frame_arg = DeclareLaunchArgument(
        'camera_frame',
        default_value='camera_link',
        description='Camera link frame name'
    )
    
    optical_frame_arg = DeclareLaunchArgument(
        'optical_frame',
        default_value='camera_optical_frame',
        description='Camera optical frame name'
    )
    
    publish_rate_arg = DeclareLaunchArgument(
        'publish_rate',
        default_value='30.0',
        description='TF publish rate (Hz)'
    )
    
    static_transform_arg = DeclareLaunchArgument(
        'static_transform',
        default_value='true',
        description='Publish as static transform'
    )
    
    config_file_arg = DeclareLaunchArgument(
        'config_file',
        default_value='',
        description='Path to YAML config file (optional)'
    )
    
    # TF broadcaster node
    tf_broadcaster_node = Node(
        package='lra_vision',
        executable='camera_tf_broadcaster_node',
        name='camera_tf_broadcaster',
        output='screen',
        parameters=[{
            'translation_x': LaunchConfiguration('translation_x'),
            'translation_y': LaunchConfiguration('translation_y'),
            'translation_z': LaunchConfiguration('translation_z'),
            'roll': LaunchConfiguration('roll'),
            'pitch': LaunchConfiguration('pitch'),
            'yaw': LaunchConfiguration('yaw'),
            'parent_frame': LaunchConfiguration('parent_frame'),
            'camera_frame': LaunchConfiguration('camera_frame'),
            'optical_frame': LaunchConfiguration('optical_frame'),
            'publish_rate': LaunchConfiguration('publish_rate'),
            'static_transform': LaunchConfiguration('static_transform'),
            'config_file': LaunchConfiguration('config_file'),
        }],
    )
    
    return LaunchDescription([
        translation_x_arg,
        translation_y_arg,
        translation_z_arg,
        roll_arg,
        pitch_arg,
        yaw_arg,
        parent_frame_arg,
        camera_frame_arg,
        optical_frame_arg,
        publish_rate_arg,
        static_transform_arg,
        config_file_arg,
        tf_broadcaster_node,
        LogInfo(msg=['LRA Vision: TF broadcaster launched']),
        LogInfo(msg=['  Transform: ', LaunchConfiguration('parent_frame'), 
                     ' -> ', LaunchConfiguration('camera_frame'),
                     ' -> ', LaunchConfiguration('optical_frame')]),
        LogInfo(msg=['  Translation: (', LaunchConfiguration('translation_x'), 
                     ', ', LaunchConfiguration('translation_y'), 
                     ', ', LaunchConfiguration('translation_z'), ') m']),
    ])