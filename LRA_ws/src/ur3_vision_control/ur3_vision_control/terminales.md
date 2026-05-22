Terminal 1

cd ~/ros2_ws && source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur3e robot_ip:=192.168.0.1 use_fake_hardware:=true launch_dashboard_client:=false headless_mode:=true launch_rviz:=false


Terminal 2

cd ~/ros2_ws && source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 launch ur_moveit_config ur_moveit.launch.py ur_type:=ur3e launch_rviz:=true launch_servo:=false


Terminal 3

cd ~/ros2_ws && source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 run ur3_vision_control vision_fake_sort


Terminal 4

cd ~/ros2_ws && source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 run ur3_vision_control ur3_pick_sort --ros-args -p simulate_gripper:=true
