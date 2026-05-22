import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, FindExecutable
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # Paths
    pkg_share = get_package_share_directory('lra_vision')
    xacro_file = os.path.join(pkg_share, 'urdf', 'camera.xacro')

    # Arguments
    camera_height_arg = DeclareLaunchArgument(
        'camera_height', default_value='0.045',
        description='Height of the camera above parent frame'
    )
    parent_frame_arg = DeclareLaunchArgument(
        'parent_frame', default_value='tool0',
        description='Parent frame to attach camera to'
    )
    camera_name_arg = DeclareLaunchArgument(
        'camera_name', default_value='camera',
        description='Name prefix for camera links'
    )

    # Camera State Publisher
    # We rename the node and remap the topic to avoid conflicts with the UR3 driver
    camera_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='camera_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': ParameterValue(
                Command([
                    FindExecutable(name='xacro'), ' ', xacro_file,
                    ' parent_link:=', LaunchConfiguration('parent_frame'),
                    ' camera_name:=', LaunchConfiguration('camera_name'),
                    ' translation_z:=', LaunchConfiguration('camera_height')
                ]),
                value_type=str
            )
        }],
        remappings=[
            ('robot_description', 'camera_description')
        ]
    )

    return LaunchDescription([
        camera_height_arg,
        parent_frame_arg,
        camera_name_arg,
        camera_state_publisher_node,
    ])
