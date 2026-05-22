#!/bin/bash
set -e
source /opt/ros/humble/setup.bash
rm -rf build/ log/ install/
colcon build
source install/setup.bash

# Connectivity check
echo "Checking connectivity to 192.168.1.102..."
ping -c 3 192.168.1.102 || echo "Warning: 192.168.1.102 is unreachable."

echo "Host IP set to $LOCAL_IP. Port 50002 is ready for UR3 driver."

exec bash
