# Clasificacion-de-tapones-plasticos-REC
En este proyecto se utilizará un robot UR3 y se dispondrá de una webcam / opcionalmente una cámara Intel Real Sense SR305. Se podrá diseñar un sistema efector diferente del eléctrico proporcionado. El objetivo es clasificar los tapones proporcionados en un depósito de entrada en n depósitos de salida.


## Instrucciones de lanzamiento del sistema UR3 + visión

Antes de iniciar el sistema, abrir una terminal y ubicarse en el workspace:

```bash
cd ~/Downloads/Clasificaci-n-de-tapones-plasticos-REC--version-portable/LRA_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
Terminal 1 — Conexión con el UR3 real
cd ~/Downloads/Clasificaci-n-de-tapones-plasticos-REC--version-portable/LRA_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur3e robot_ip:=169.254.12.28 launch_rviz:=false

Esperar hasta que aparezca el mensaje de conexión del robot.

Terminal 2 — Transformación estática world a base_link
cd ~/Downloads/Clasificaci-n-de-tapones-plasticos-REC--version-portable/LRA_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 world base_link

Dejar esta terminal abierta.

Terminal 3 — Sistema completo de control y visión
cd ~/Downloads/Clasificaci-n-de-tapones-plasticos-REC--version-portable/LRA_ws
source /opt/ros/humble/setup.bash
source install/setup.bash

ros2 launch ur3_vision_control launch.py

=============================================

Verificación de topics

ros2 topic echo /tapones/caja_asignada

Para verificar la caja asignada por visión:

ros2 topic echo /ur3/target_point
