from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    num_cajas_arg = DeclareLaunchArgument(
        'num_cajas', default_value='3',
        description='Numero de cajas de clasificacion (1-6)')

    frames_muestreo_arg = DeclareLaunchArgument(
        'frames_muestreo', default_value='30',
        description='Frames a acumular para el K-Means')

    show_debug_arg = DeclareLaunchArgument(
        'show_debug', default_value='true',
        description='Mostrar ventana de debug OpenCV')

    calibrator_node = Node(
        package='rec_vision',
        executable='color_calibrator_node',
        name='color_calibrator_node',
        output='screen',
        parameters=[{
            'camera_info_yaml': '/home/delia/Documents/MUAR/ProyectoREC/Clasificaci-n-de-tapones-plasticos-REC--vision-Humble/LRA_ws/calibration_data/camera_info.yaml',
            'num_cajas':        LaunchConfiguration('num_cajas'),
            'frames_muestreo':  LaunchConfiguration('frames_muestreo'),
            'show_debug':       LaunchConfiguration('show_debug'),
            'image_topic':      '/image_raw',
            'min_radius':       33,
            'max_radius':       54,
            'min_dist':         75,
            'hough_param1':     21,
            'hough_param2':     27,
        }]
    )

    return LaunchDescription([
        num_cajas_arg,
        frames_muestreo_arg,
        show_debug_arg,
        calibrator_node,
    ])
