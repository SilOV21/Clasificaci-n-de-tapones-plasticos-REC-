#!/bin/bash
# =============================================================================
# Vision System Launcher
# Launches: camera_manager, upload_urdf, aruco_detector, detector_tapones
# =============================================================================
cleanup() {
    echo ""
    echo "Shutting down all vision nodes..."
    kill 0
}
trap cleanup SIGINT SIGTERM EXIT

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"
echo "Workspace Root: $WORKSPACE_ROOT"

if [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
fi
if [ -f "$WORKSPACE_ROOT/install/setup.bash" ]; then
    source "$WORKSPACE_ROOT/install/setup.bash"
    echo "Sourced workspace setup."
else
    echo "Warning: Workspace setup.bash not found. Please build the workspace first."
fi

echo "Starting Vision Pipeline..."

# 1. Camera Manager
echo "Launching Camera Manager..."
ros2 launch lra_vision camera_manager.launch.py &
sleep 3

# 2. URDF Launcher
echo "Launching URDF Publisher..."
ros2 launch lra_vision upload_urdf.launch.py &
sleep 1

# 3. ArUco Detector
echo "Launching ArUco Detector..."
ros2 launch lra_vision aruco_detector.launch.py &
sleep 1

# 4. Calibración color
echo "Launching Calibracion Color..."
ros2 launch rec_vision color_calibrator.launch.py &
sleep 1

# 5. Visor imagen debug (antes del detector para que esté listo)
echo "Launching Image Viewer..."
ros2 run rqt_image_view rqt_image_view /tapones/imagen_debug &
sleep 1

# 6. Detector Tapones
echo "Launching Detector Tapones..."
ros2 launch rec_vision detector_tapones.launch.py show_debug:=true &

echo "All nodes launched. Press Ctrl+C to stop."
wait
