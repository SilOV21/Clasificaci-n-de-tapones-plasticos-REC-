# Clasificacion-de-tapones-plasticos-REC
En este proyecto se utilizará un robot UR3 y se dispondrá de una webcam / opcionalmente una cámara Intel Real Sense SR305. Se podrá diseñar un sistema efector diferente del eléctrico proporcionado. El objetivo es clasificar los tapones proporcionados en un depósito de entrada en n depósitos de salida.


Se necesita descargar los drivers del UR3 para ejecutarlos y escoger el tipo de ros.

Para abrir y cerrar la pinza ficamente es con estos comandos

ros2 service call /io_and_status_controller/set_io ur_msgs/srv/SetIO "{fun: 1, pin: 17, state: 0}"
ros2 service call /io_and_status_controller/set_io ur_msgs/srv/SetIO "{fun: 1, pin: 16, state: 1}"


ros2 service call /io_and_status_controller/set_io ur_msgs/srv/SetIO "{fun: 1, pin: 16, state: 0}"
ros2 service call /io_and_status_controller/set_io ur_msgs/srv/SetIO "{fun: 1, pin: 17, state: 1}"


Para lanzar este repositorio es con estos comandos


cd ~/ros2_ws
colcon build --packages-select ur3_vision_control


Terminal 1
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur3 robot_ip:=192.168.0.1 use_fake_hardware:=true launch_dashboard_client:=false headless_mode:=true launch_rviz:=false
Terminal 2
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur3 launch_rviz:=true launch_servo:=false
Terminal 3
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run ur3_vision_control vision_fake_sort
Terminal 4
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run ur3_vision_control ur3_pick_sort --ros-args -p simulate_gripper:=true
