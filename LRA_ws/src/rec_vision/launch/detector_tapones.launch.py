from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():

    show_debug_arg = DeclareLaunchArgument(
        'show_debug', default_value='true',
        description='Mostrar ventana de debug OpenCV')

    frames_muestreo_arg = DeclareLaunchArgument(
        'frames_muestreo', default_value='30',
        description='Frames a acumular para estabilizar posicion')

    camera_info_path = PathJoinSubstitution([
        FindPackageShare('lra_vision'),
        'calibration_data',
        'camera_info.yaml'
    ])

    detector_node = Node(
        package='rec_vision',
        executable='detector_tapones',
        name='vision_node',
        output='screen',
        parameters=[{
            'camera_info_yaml': camera_info_path,  
            'frames_muestreo':  LaunchConfiguration('frames_muestreo'),
            'image_topic':      'camera/image_raw',
            'show_debug':       LaunchConfiguration('show_debug'),
            'target_frame':     'base_link',
            'camera_frame':     'camera_optical_frame',
            'min_radius':       33,
            'max_radius':       54,
            'min_dist':         75,
            'hough_param1':     21,
            'hough_param2':     27,
        }]
    )

    return LaunchDescription([
        show_debug_arg,
        frames_muestreo_arg,
        detector_node,
    ])
