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
        'camera_height', default_value='0.05',
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

    # Robot State Publisher
    # This processes the xacro and publishes to /robot_description
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
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
        }]
    )

    # Joint State Publisher (required for RobotModel display in RViz)
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'use_sim_time': False}]
    )

    return LaunchDescription([
        camera_height_arg,
        parent_frame_arg,
        camera_name_arg,
        robot_state_publisher_node,
        joint_state_publisher_node
    ])
