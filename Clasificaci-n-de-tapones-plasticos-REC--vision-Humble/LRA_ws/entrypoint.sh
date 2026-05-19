#!/bin/bash
set -e
source /opt/ros/humble/setup.bash
rm -rf build/ log/ install/
colcon build
source install/setup.bash
exec bash
