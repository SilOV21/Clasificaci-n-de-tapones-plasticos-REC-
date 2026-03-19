#!/bin/bash

# LRA Vision System Launcher
# Launches all necessary components for the vision package

set -e  # Exit on any error

echo "=== LRA Vision System Launcher ==="
echo "Starting vision system components..."

# Source the ROS2 environment
source /opt/ros/jazzy/setup.bash
if [ -f "install/setup.bash" ]; then
    source install/setup.bash
fi

# Function to check if a process is running
is_running() {
    pgrep -f "$1" > /dev/null
    return $?
}

# Function to launch a component
launch_component() {
    local name=$1
    local command=$2
    local check_process=$3

    echo "Launching $name..."

    # Check if already running
    if is_running "$check_process"; then
        echo "$name is already running"
        return
    fi

    # Launch in background
    eval "$command" &
    sleep 2

    # Check if it started successfully
    if is_running "$check_process"; then
        echo "$name started successfully"
    else
        echo "Failed to start $name"
        return 1
    fi
}

# Option 1: Launch everything in separate terminals using tmux
if [ "$1" == "tmux" ]; then
    echo "Launching in tmux session..."

    # Kill existing session if it exists
    tmux kill-session -t lra_vision 2>/dev/null || true

    # Create new session
    tmux new-session -d -s lra_vision

    # Create windows for each component
    tmux new-window -t lra_vision -n camera_manager
    tmux new-window -t lra_vision -n camera_calibrator
    tmux new-window -t lra_vision -n tf_broadcaster
    tmux new-window -t lra_vision -n aruco_detector
    tmux new-window -t lra_vision -n monitor

    # Send commands to each window
    tmux send-keys -t lra_vision:camera_manager "source /opt/ros/jazzy/setup.bash && source install/setup.bash && ros2 launch lra_vision camera_manager.launch.py" Enter
    tmux send-keys -t lra_vision:camera_calibrator "source /opt/ros/jazzy/setup.bash && source install/setup.bash && ros2 launch lra_vision camera_calibration.launch.py" Enter
    tmux send-keys -t lra_vision:tf_broadcaster "source /opt/ros/jazzy/setup.bash && source install/setup.bash && ros2 launch lra_vision camera_tf_broadcaster.launch.py" Enter
    tmux send-keys -t lra_vision:aruco_detector "source /opt/ros/jazzy/setup.bash && source install/setup.bash && ros2 launch lra_vision aruco_detector.launch.py" Enter
    tmux send-keys -t lra_vision:monitor "source /opt/ros/jazzy/setup.bash && source install/setup.bash && echo 'Vision System Monitor' && echo 'Useful commands:' && echo 'ros2 topic list' && echo 'ros2 node list' && echo 'ros2 service list' && bash" Enter

    # Attach to session
    echo "Connecting to tmux session. Use Ctrl+B, D to detach."
    tmux attach-session -t lra_vision

    exit 0
fi

# Option 2: Launch all in background processes
echo "Launching all components in background..."

# Launch camera manager
launch_component "Camera Manager" \
    "ros2 launch lra_vision camera_manager.launch.py" \
    "camera_manager_node"

# Launch camera calibrator
launch_component "Camera Calibrator" \
    "ros2 launch lra_vision camera_calibration.launch.py" \
    "camera_calibrator_node"

# Launch TF broadcaster
launch_component "TF Broadcaster" \
    "ros2 launch lra_vision camera_tf_broadcaster.launch.py" \
    "camera_tf_broadcaster_node"

# Launch ArUco detector
launch_component "ArUco Detector" \
    "ros2 launch lra_vision aruco_detector.launch.py" \
    "aruco_detector_node"

echo ""
echo "=== Vision System Launched ==="
echo "Components running:"
echo "1. Camera Manager Node (with v4l2_camera)"
echo "2. Camera Calibrator Node"
echo "3. TF Broadcaster Node"
echo "4. ArUco Detector Node"
echo ""
echo "Monitor with: ros2 node list"
echo "View topics: ros2 topic list"
echo ""
echo "To stop all components, run: pkill -f lra_vision"