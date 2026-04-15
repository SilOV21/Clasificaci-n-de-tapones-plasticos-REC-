# Clasificacion-de-tapones-plasticos-REC
En este proyecto se utilizará un robot UR3 y se dispondrá de una webcam / opcionalmente una cámara Intel Real Sense SR305. Se podrá diseñar un sistema efector diferente del eléctrico proporcionado. El objetivo es clasificar los tapones proporcionados en un depósito de entrada en n depósitos de salida.


Se necesita descargar los drivers del UR3 para ejecutarlos y escoger el tipo de ros.

Para abrir y cerrar la pinza ficamente es con estos comandos

ros2 service call /io_and_status_controller/set_io ur_msgs/srv/SetIO "{fun: 1, pin: 17, state: 0}"
ros2 service call /io_and_status_controller/set_io ur_msgs/srv/SetIO "{fun: 1, pin: 16, state: 1}"


ros2 service call /io_and_status_controller/set_io ur_msgs/srv/SetIO "{fun: 1, pin: 16, state: 0}"
ros2 service call /io_and_status_controller/set_io ur_msgs/srv/SetIO "{fun: 1, pin: 17, state: 1}"


RUTH ALEJANDRA BASTIDAS ALVA <rbastidasalva@gmail.com>
mié, 8 abr, 14:29 (hace 7 días)
para mí

ip -4 addr show eno1   ------  debo ver inet 169.254.12.10/24

sudo ip addr flush dev eno1
sudo ip addr add 169.254.12.10/24 dev eno1
sudo ip link set eno1 up
ip -4 addr show eno1

---
ping -c 4 169.254.12.20


source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur3 robot_ip:=169.254.12.28 launch_rviz:=false

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
ros2 run ur3_vision_control ur3_pick_sort --ros-args -p simulate_gripper:=false
