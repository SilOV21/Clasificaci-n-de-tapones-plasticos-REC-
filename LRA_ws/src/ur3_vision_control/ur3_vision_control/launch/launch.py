import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_ur_moveit = get_package_share_directory('ur_moveit_config')
    pkg_lra_vision = get_package_share_directory('lra_vision')
    pkg_rec_vision = get_package_share_directory('rec_vision')

    # MoveIt
    launch_moveit = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ur_moveit, 'launch', 'ur_moveit.launch.py')
        ),
        launch_arguments={
            'ur_type': 'ur3e',
            'launch_rviz': 'false',
            'launch_servo': 'false'
        }.items()
    )

    # Cámara real
    launch_camera = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_lra_vision, 'launch', 'camera_manager.launch.py')
        )
    )

    # TF/URDF de cámara
    launch_camera_urdf = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_lra_vision, 'launch', 'upload_urdf.launch.py')
        )
    )

    # Calibrador de color
    launch_color_calibrator = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_rec_vision, 'launch', 'color_calibrator.launch.py')
        )
    )

    # Nodo principal del robot
    node_pick_sort = Node(
        package='ur3_vision_control',
        executable='ur3_pick_sort',
        name='ur3_pick_sort',
        parameters=[{
            'simulate_gripper': False
        }],
        output='screen'
    )

    # Detector real de tapones
    launch_detector = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_rec_vision, 'launch', 'detector_tapones.launch.py')
        ),
        launch_arguments={
            'show_debug': 'true'
        }.items()
    )

    return LaunchDescription([
        launch_moveit,
        launch_camera,
        launch_camera_urdf,
        launch_color_calibrator,

        # Se espera a que MoveIt esté arriba antes de iniciar pick_sort
        TimerAction(
            period=8.0,
            actions=[node_pick_sort]
        ),

        # Se espera más para que el robot llegue a HOME antes del detector
        TimerAction(
            period=25.0,
            actions=[launch_detector]
        ),
    ])
