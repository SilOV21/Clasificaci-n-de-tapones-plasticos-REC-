# =============================================================================
# LRA Vision Package - TF Broadcaster Launch
# Publishes TF transforms for camera-UR3 relationship
# ROS2 Humble Hawksbill
# =============================================================================

import os
import yaml
import math
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, OpaqueFunction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def launch_setup(context, *args, **kwargs):
    translation_x = LaunchConfiguration('translation_x').perform(context)
    translation_y = LaunchConfiguration('translation_y').perform(context)
    translation_z = LaunchConfiguration('translation_z').perform(context)
    roll = LaunchConfiguration('roll').perform(context)
    pitch = LaunchConfiguration('pitch').perform(context)
    yaw = LaunchConfiguration('yaw').perform(context)
    parent_frame = LaunchConfiguration('parent_frame').perform(context)
    camera_frame = LaunchConfiguration('camera_frame').perform(context)
    optical_frame = LaunchConfiguration('optical_frame').perform(context)
    config_file = LaunchConfiguration('config_file').perform(context)

    # Read from config if provided
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            if 'camera_mount' in config:
                mount = config['camera_mount']
                translation_x = str(mount.get('translation_x', translation_x))
                translation_y = str(mount.get('translation_y', translation_y))
                translation_z = str(mount.get('translation_z', translation_z))
                roll = str(mount.get('roll', roll))
                pitch = str(mount.get('pitch', pitch))
                yaw = str(mount.get('yaw', yaw))
                parent_frame = mount.get('parent_frame', parent_frame)
                camera_frame = mount.get('camera_frame', camera_frame)
                optical_frame = mount.get('optical_frame', optical_frame)

    # Base to Camera Transform
    camera_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='camera_mount_tf',
        output='screen',
        arguments=[
            translation_x, translation_y, translation_z,
            yaw, pitch, roll, # static_transform_publisher uses yaw pitch roll
            parent_frame, camera_frame
        ]
    )

    # Camera to Optical Transform
    # Optical frame standard in ROS is: z forward, x right, y down
    # This corresponds to roll = -pi/2, pitch = 0, yaw = -pi/2
    optical_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='camera_optical_tf',
        output='screen',
        arguments=[
            '0', '0', '0',
            str(-math.pi/2), '0', str(-math.pi/2),
            camera_frame, optical_frame
        ]
    )

    return [
        LogInfo(msg=['LRA Vision: TF broadcaster launched (Static transforms)']),
        LogInfo(msg=[f'  Transform: {parent_frame} -> {camera_frame} -> {optical_frame}']),
        LogInfo(msg=[f'  Translation: ({translation_x}, {translation_y}, {translation_z}) m']),
        camera_tf_node,
        optical_tf_node
    ]

def generate_launch_description():
    # Declare launch arguments
    translation_x_arg = DeclareLaunchArgument(
        'translation_x', default_value='0.0', description='Camera translation X from parent frame (meters)'
    )
    translation_y_arg = DeclareLaunchArgument(
        'translation_y', default_value='0.0', description='Camera translation Y from parent frame (meters)'
    )
    translation_z_arg = DeclareLaunchArgument(
        'translation_z', default_value='0.05', description='Camera translation Z from parent frame (meters) - 5cm above UR3'
    )
    roll_arg = DeclareLaunchArgument(
        'roll', default_value='0.0', description='Camera roll angle (radians)'
    )
    pitch_arg = DeclareLaunchArgument(
        'pitch', default_value='3.14159', description='Camera pitch angle (radians) - PI for downward facing'
    )
    yaw_arg = DeclareLaunchArgument(
        'yaw', default_value='0.0', description='Camera yaw angle (radians)'
    )
    parent_frame_arg = DeclareLaunchArgument(
        'parent_frame', default_value='tool0', description='Parent frame (UR3 end effector)'
    )
    camera_frame_arg = DeclareLaunchArgument(
        'camera_frame', default_value='camera_link', description='Camera link frame name'
    )
    optical_frame_arg = DeclareLaunchArgument(
        'optical_frame', default_value='camera_optical_frame', description='Camera optical frame name'
    )
    config_file_arg = DeclareLaunchArgument(
        'config_file', default_value='', description='Path to YAML config file (optional)'
    )
    
    # We ignore publish_rate and static_transform args since they aren't relevant for static_transform_publisher
    
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
        config_file_arg,
        OpaqueFunction(function=launch_setup)
    ])