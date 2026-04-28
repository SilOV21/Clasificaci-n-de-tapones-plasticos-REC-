from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    show_debug_arg = DeclareLaunchArgument(
        'show_debug', default_value='true',
        description='Mostrar ventana de debug OpenCV')

    frames_muestreo_arg = DeclareLaunchArgument(
        'frames_muestreo', default_value='30',
        description='Frames a acumular para estabilizar posicion')

    detector_node = Node(
        package='rec_vision',
        executable='detector_tapones',
        name='vision_node',
        output='screen',
        parameters=[{
            'camera_info_yaml': '/home/delia/Documents/MUAR/ProyectoREC/Clasificaci-n-de-tapones-plasticos-REC--vision-Humble/LRA_ws/calibration_data/camera_info.yaml',
            'show_debug':       LaunchConfiguration('show_debug'),
            'frames_muestreo':  LaunchConfiguration('frames_muestreo'),
            'image_topic':      '/image_raw',
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
