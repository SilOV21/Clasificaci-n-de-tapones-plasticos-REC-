"""Convenience launch: brings up every fake node in one command.

Useful for testing the simulation without going through the HMI launcher.
Run with: ros2 launch lra_hmi_sim all_sim.launch.py
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    num_boxes = LaunchConfiguration("num_boxes")
    driver_crash_after = LaunchConfiguration("driver_crash_after_s")

    return LaunchDescription([
        DeclareLaunchArgument("num_boxes", default_value="4"),
        DeclareLaunchArgument("driver_crash_after_s", default_value="0.0"),

        Node(
            package="lra_hmi_sim",
            executable="fake_ur_driver",
            name="fake_ur_driver",
            output="screen",
            emulate_tty=True,
            parameters=[{"crash_after_s": driver_crash_after}],
        ),
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="world_to_base_link",
            output="screen",
            arguments=["0", "0", "0", "0", "0", "0", "world", "base_link"],
        ),
        Node(
            package="lra_hmi_sim",
            executable="fake_vision",
            name="fake_vision",
            output="screen",
            emulate_tty=True,
            parameters=[{"num_boxes": num_boxes}],
        ),
        Node(
            package="lra_hmi_sim",
            executable="vision_enable_logger",
            name="vision_enable_logger",
            output="screen",
            emulate_tty=True,
        ),
    ])
