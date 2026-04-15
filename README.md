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
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select eurobot_sim
source ~/ros2_ws/install/setup.bash




# Terminal 1: levantar la simulación


cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch eurobot_sim simulation.launch.py


# Terminal 2: ver si la cámara simulada publica


cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 topic list | grep -E "image|camera"



# Terminal 3: ver la imagen de la cámara

cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run rqt_image_view rqt_image_view

Y dentro de la ventana selecciona:

/eurobot_camera/image_raw


# Terminal 4: correr tu nodo ArUco en simulación


cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 run aruco_tracker objects_state --ros-args -p use_sim_camera:=true -p image_topic:=/eurobot_camera/image_raw




# Terminal 5: ver si publica resultados

cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 topic echo /objects_state
