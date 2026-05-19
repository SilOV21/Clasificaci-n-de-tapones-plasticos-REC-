import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # Directorios de los paquetes
    pkg_ur_moveit = get_package_share_directory('ur_moveit_config')
    pkg_vision_control = get_package_share_directory('ur3_vision_control')

    # --- EQUIVALENTE A TERMINAL 2 (MoveIt) ---
    launch_moveit = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ur_moveit, 'launch', 'ur_moveit.launch.py')
        ),
        launch_arguments={
            'ur_type': 'ur3',
            'launch_rviz': 'true',
            'launch_servo': 'false'
        }.items()
    )

    # --- EQUIVALENTE A TERMINAL 3 (Vision Node) ---
    node_vision = Node(
        package='ur3_vision_control',
        executable='vision_fake_sort',
        name='vision_fake_sort',
        output='screen'
    )

    # --- EQUIVALENTE A TERMINAL 4 (Pick & Sort Node) ---
    node_pick_sort = Node(
        package='ur3_vision_control',
        executable='ur3_pick_sort',
        name='ur3_pick_sort',
        parameters=[{'simulate_gripper': False}],
        output='screen'
    )

    return LaunchDescription([
        launch_moveit,
        node_vision,
        node_pick_sort
    ])
