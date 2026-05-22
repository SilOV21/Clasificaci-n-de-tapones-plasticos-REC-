"""Simulation stack used as a stand-in for ur3_vision_control.

This is what the HMI launches as the "Vision & MoveIt" group when
LRA_HMI_SIM=1 is set.
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    num_boxes = LaunchConfiguration("num_boxes")

    return LaunchDescription([
        DeclareLaunchArgument("num_boxes", default_value="4"),

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
