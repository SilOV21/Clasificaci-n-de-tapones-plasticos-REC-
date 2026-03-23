#!/bin/bash
# Test script for ArUco detector

source /home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/install/setup.bash

echo "=== Starting ArUco Test ==="
echo ""

# Run camera info publisher in background
echo "Starting camera info publisher..."
ros2 run lra_vision camera_info_publisher.py &
CAMERA_PID=$!

# Wait for it to start
sleep 2

# Check if camera info is publishing
echo ""
echo "=== Checking camera_info topic ==="
timeout 2 ros2 topic echo /camera/camera_info --once 2>/dev/null || echo "Camera info not publishing"

# Run test image publisher in background
echo ""
echo "Starting test image publisher..."
ros2 run lra_vision aruco_test_publisher.py &
IMAGE_PID=$!

# Wait for it
sleep 2

# Run ArUco detector in background
echo ""
echo "Starting ArUco detector..."
ros2 launch lra_vision aruco_detector.launch.py calibration_file:=/home/asil/.ros/camera_calibration/camera_info.yaml 2>&1 &
ARUCO_PID=$!

# Wait for detector to initialize
sleep 3

echo ""
echo "=== Testing marker detection ==="
echo "Checking /camera/aruco/marker_ids for 10 seconds..."
timeout 10 ros2 topic echo /camera/aruco/marker_ids

echo ""
echo "Checking /camera/aruco/poses..."
timeout 3 ros2 topic echo /camera/aruco/poses --once 2>/dev/null || echo "No poses published"

echo ""
echo "=== Test complete ==="

# Cleanup
kill $CAMERA_PID $IMAGE_PID $ARUCO_PID 2>/dev/null
