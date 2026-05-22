"""Launch shortcut: `ros2 launch lra_hmi hmi.launch.py`."""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="lra_hmi",
            executable="main",
            name="lra_hmi",
            output="screen",
            emulate_tty=True,
        ),
    ])
