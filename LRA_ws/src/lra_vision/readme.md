# LRA Vision Package - Complete Documentation

## Overview

This package provides complete vision capabilities for the LRA (Laboratorio de Automática y Robótica) REC Project - Plastic Cap Classification using UR3 Robotic Arm and Logitech StreamCam.

**Universidad Politécnica de Madrid - MUAR 2025-2026**

## Table of Contents

1. [Package Structure](#package-structure)
2. [Nodes](#nodes)
3. [Launch Files](#launch-files)
4. [Messages and Services](#messages-and-services)
5. [Configuration Files](#configuration-files)
6. [TF Transformations](#tf-transformations)
7. [User Manual](#user-manual)
8. [Installation and Building](#installation-and-building)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

## Package Structure

```
lra_vision/
├── CMakeLists.txt           # Build configuration
├── package.xml             # Package metadata
├── README.md               # Main documentation
├── QUICKREF.md             # Quick reference guide
├── config/                 # Configuration files
│   ├── camera_params.yaml   # Camera parameters
│   ├── calibration.yaml    # Calibration settings
│   ├── camera_mount.yaml    # TF configuration
│   ├── aruco_params.yaml   # ArUco settings
│   └── image_processing.yaml # Image processing params
├── include/lra_vision/    # Header files
│   ├── camera_detector.hpp
│   ├── camera_calibration.hpp
│   ├── image_processor.hpp
│   ├── camera_tf_broadcaster.hpp
│   └── aruco_detector.hpp
├── launch/                 # Launch files
│   ├── camera_publisher.launch.py
│   ├── camera_calibration.launch.py
│   ├── camera_tf_broadcaster.launch.py
│   ├── aruco_detector.launch.py
│   └── lra_vision.launch.py
├── msg/                    # Custom messages
│   ├── CameraInfo.msg
│   └── CalibrationStatus.msg
├── rviz/                   # RViz configurations
│   ├── camera_view.rviz
│   └── detection_view.rviz
├── src/                    # Source files
│   ├── nodes/             # ROS2 nodes
│   │   ├── camera_publisher_node.cpp
│   │   ├── camera_calibrator_node.cpp
│   │   ├── camera_tf_broadcaster_node.cpp
│   │   └── aruco_detector_node.cpp
│   ├── utils/             # Utility libraries
│   │   ├── camera_detector.cpp
│   │   ├── camera_calibration.cpp
│   │   ├── image_processor.cpp
│   │   └── aruco_detector.cpp
│   └── tf/                # TF utilities
│       ├── camera_tf_broadcaster.cpp
│       └── ur3_camera_transform.cpp
├── srv/                    # Custom services
│   ├── GetCameraDevice.srv
│   └── CalibrateCamera.srv
├── test/                   # Unit tests
│   ├── test_camera_detector.cpp
│   ├── test_camera_calibration.cpp
│   ├── test_tf_broadcaster.cpp
│   ├── test_image_processor.cpp
│   └── test_aruco_detector.cpp
└── urdf/                   # Robot description
    ├── camera.urdf
    └── camera.xacro
```

## Nodes

### 1. Camera Publisher Node (`camera_publisher_node`)

Publishes camera images from the Logitech StreamCam device.

**Parameters:**
- `video_device`: Video device path (default: "/dev/video2")
- `camera_name`: Camera name (default: "logitech_streamcam")
- `frame_id`: Frame ID for camera (default: "camera_optical_frame")
- `image_width`: Image width (default: 1920)
- `image_height`: Image height (default: 1080)
- `framerate`: Frame rate (default: 30)
- `auto_detect`: Auto-detect camera (default: true)
- `publish_rate`: Publishing rate (default: 30.0)

**Published Topics:**
- `/camera/image_raw` (sensor_msgs/Image): Raw camera images
- `/camera/camera_info` (sensor_msgs/CameraInfo): Camera calibration information
- `/camera/status` (std_msgs/String): Camera status information

**Services:**
- `/reconnect` (std_srvs/Trigger): Reconnect to camera

### 2. Camera Calibrator Node (`camera_calibrator_node`)

Performs interactive camera calibration using chessboard pattern detection.

**Parameters:**
- `board_width`: Chessboard width (inner corners, default: 9)
- `board_height`: Chessboard height (inner corners, default: 6)
- `square_size`: Square size in meters (default: 0.025)
- `min_images`: Minimum images for calibration (default: 30)

**Published Topics:**
- `/calibration/status` (std_msgs/String): Calibration status
- `/calibration/ready` (std_msgs/Bool): Calibration readiness
- `/calibration/debug` (sensor_msgs/Image): Debug visualization

**Services:**
- `/capture` (std_srvs/Trigger): Capture current image
- `/calibrate` (std_srvs/Trigger): Perform calibration
- `/save` (std_srvs/Trigger): Save calibration results
- `/reset` (std_srvs/Trigger): Clear collected data

### 3. Camera TF Broadcaster Node (`camera_tf_broadcaster_node`)

Publishes TF transforms for the camera-UR3 relationship.

**Parameters:**
- `translation_x`: X translation (default: 0.0)
- `translation_y`: Y translation (default: 0.0)
- `translation_z`: Z translation (height above UR3, default: 0.05)
- `roll`: Roll rotation (default: 0.0)
- `pitch`: Pitch rotation (default: 3.14159 - 180 degrees)
- `yaw`: Yaw rotation (default: 0.0)
- `parent_frame`: Parent frame (default: "tool0")
- `camera_frame`: Camera frame (default: "camera_link")
- `optical_frame`: Optical frame (default: "camera_optical_frame")
- `publish_rate`: Publishing rate (default: 30.0)
- `static_transform`: Static transform (default: true)

**Published TF Frames:**
- `tool0` → `camera_link` → `camera_optical_frame`

### 4. ArUco Detector Node (`aruco_detector_node`)

Detects ArUco markers for hand-eye calibration.

**Parameters:**
- `image_topic`: Input image topic (default: "camera/image_raw")
- `camera_info_topic`: Camera info topic (default: "camera/camera_info")
- `dictionary`: ArUco dictionary (default: "DICT_4X4_50")
- `marker_size`: Marker size in meters (default: 0.05)
- `publish_markers`: Publish markers (default: true)
- `publish_poses`: Publish poses (default: true)
- `publish_image`: Publish detected image (default: true)
- `calibration_file`: Calibration file path (default: "")

**Published Topics:**
- `/aruco/markers` (visualization_msgs/MarkerArray): Detected markers
- `/aruco/poses` (geometry_msgs/PoseArray): Marker poses
- `/aruco/marker_ids` (std_msgs/Int32MultiArray): Detected marker IDs
- `/aruco/detected_image` (sensor_msgs/Image): Visualization image

## Launch Files

### 1. Main Launch File (`lra_vision.launch.py`)

Launches all vision nodes for the complete system.

**Launch Arguments:**
- `video_device`: Video device path (default: "/dev/video2")
- `camera_name`: Camera name (default: "logitech_streamcam")
- `calibration_file`: Path to camera calibration file (default: "")
- `board_width`: Chessboard width (default: "9")
- `board_height`: Chessboard height (default: "6")
- `translation_z`: Camera height above UR3 (default: "0.05")
- `use_namespace`: Use namespace for nodes (default: "false")
- `namespace`: Namespace for nodes (default: "lra_vision")

**Launched Nodes:**
- Camera publisher node
- Camera TF broadcaster node
- ArUco detector node

### 2. Camera Publisher Launch (`camera_publisher.launch.py`)

Launches only the camera publisher node.

### 3. Camera Calibration Launch (`camera_calibration.launch.py`)

Launches only the camera calibrator node.

### 4. Camera TF Broadcaster Launch (`camera_tf_broadcaster.launch.py`)

Launches only the camera TF broadcaster node.

### 5. ArUco Detector Launch (`aruco_detector.launch.py`)

Launches only the ArUco detector node.

## Messages and Services

### Messages

#### CameraInfo.msg
Contains camera-specific information.

#### CalibrationStatus.msg
Contains calibration status information.

### Services

#### GetCameraDevice.srv
Service to get camera device information.

Request:
- None

Response:
- string device_path: Camera device path
- bool success: Success status

#### CalibrateCamera.srv
Service to calibrate the camera.

Request:
- None

Response:
- bool success: Success status
- string message: Result message

## Configuration Files

### Camera Parameters (`config/camera_params.yaml`)

```yaml
camera:
  name: "logitech_streamcam"
  manufacturer: "Logitech"
  model: "StreamCam"
  video_device: "/dev/video2"
  auto_detect: true
  fallback_devices:
    - "/dev/video2"
    - "/dev/video3"
    - "/dev/video0"
    - "/dev/video1"
  resolution:
    width: 1920
    height: 1080
    framerate: 30
  pixel_format: "YUYV"
  publish_rate: 30.0
  buffer_size: 1

topics:
  image_raw: "camera/image_raw"
  camera_info: "camera/camera_info"
  status: "camera/status"

frames:
  camera_link: "camera_link"
  optical_frame: "camera_optical_frame"

auto_exposure:
  enabled: true
  priority: "quality"
  exposure_time: 0
  gain: 0
  white_balance: true
```

### Calibration Parameters (`config/calibration.yaml`)

```yaml
calibration:
  board_width: 9
  board_height: 6
  square_size: 0.025
  min_images: 30
```

### Camera Mount Parameters (`config/camera_mount.yaml`)

```yaml
camera_mount:
  translation:
    x: 0.0
    y: 0.0
    z: 0.05
  rotation:
    roll: 0.0
    pitch: 3.14159
    yaw: 0.0
  parent_frame: "tool0"
  camera_frame: "camera_link"
  optical_frame: "camera_optical_frame"
  static_transform: true
```

### ArUco Parameters (`config/aruco_params.yaml`)

```yaml
aruco:
  dictionary: "DICT_4X4_50"
  marker_size: 0.05
  publish_markers: true
  publish_poses: true
  publish_image: true
```

### Image Processing Parameters (`config/image_processing.yaml`)

```yaml
image_processing:
  # Color detection thresholds
  colors:
    red:
      lower_hsv: [0, 100, 100]
      upper_hsv: [10, 255, 255]
    blue:
      lower_hsv: [100, 100, 100]
      upper_hsv: [130, 255, 255]
    green:
      lower_hsv: [40, 100, 100]
      upper_hsv: [80, 255, 255]

  # Object detection parameters
  object_detection:
    min_area: 100
    max_area: 5000
    circularity_threshold: 0.7

  # Morphological operations
  morph:
    kernel_size: 5
    iterations: 2
```

## TF Transformations

The camera is mounted 5cm above the UR3 end effector (tool0), pointing downward:

```
TF Tree:
world → base_link → ... → tool0 → camera_link → camera_optical_frame

Transform (tool0 to camera_link):
  translation: [0, 0, 0.05]  # 5cm above tool0
  rotation: [0, π, 0]        # 180° pitch (pointing down)
```

## User Manual

### Installation

#### Prerequisites
- ROS2 Jazzy Jalisco
- OpenCV 4.x
- yaml-cpp
- GTest (for testing)

#### Dependencies Installation
```bash
sudo apt install ros-jazzy-v4l2-camera ros-jazzy-image-transport ros-jazzy-cv-bridge \
                 ros-jazzy-tf2-ros ros-jazzy-camera-info-manager libopencv-dev \
                 libyaml-cpp-dev
```

#### Building the Package
```bash
cd ~/Desktop/LRA_ws
colcon build --packages-select lra_vision
source install/setup.bash
```

### Running the System

### Quick Start
1. Connect Logitech StreamCam to USB port
2. Launch the complete system:
```bash
./scripts/launch_vision_system.sh
```
Or with tmux:
```bash
./scripts/launch_vision_system.sh tmux
```

#### 1. Starting Individual Components

##### Camera Publisher
```bash
# Using rosrun
ros2 run lra_vision camera_publisher_node --ros-args \
  -p video_device:=/dev/video2 \
  -p auto_detect:=true

# Using launch file
ros2 launch lra_vision camera_publisher.launch.py \
  video_device:=/dev/video2 \
  auto_detect:=true
```

##### Camera Calibration
```bash
# Start calibration node
ros2 launch lra_vision camera_calibration.launch.py

# Capture images
ros2 service call /capture std_srvs/srv/Trigger

# Perform calibration
ros2 service call /calibrate std_srvs/srv/Trigger

# Save calibration
ros2 service call /save std_srvs/srv/Trigger

# Reset calibration data
ros2 service call /reset std_srvs/srv/Trigger
```

##### TF Broadcaster
```bash
# Using launch file
ros2 launch lra_vision camera_tf_broadcaster.launch.py \
  translation_z:=0.05 \
  pitch:=3.14159
```

##### ArUco Detector
```bash
# Using launch file
ros2 launch lra_vision aruco_detector.launch.py \
  dictionary:=DICT_4X4_50 \
  marker_size:=0.05
```

#### 2. Starting Complete System
```bash
# Launch all nodes
ros2 launch lra_vision lra_vision.launch.py

# With custom parameters
ros2 launch lra_vision lra_vision.launch.py \
  video_device:=/dev/video3 \
  translation_z:=0.06
```

### Monitoring and Visualization

#### Viewing Camera Images
```bash
# View raw camera images
ros2 run image_view image_view --ros-args -r image:=/camera/image_raw

# View processed images
ros2 run image_view image_view --ros-args -r image:=/aruco/detected_image
```

#### Viewing TF Transforms
```bash
# View TF tree
ros2 run tf2_tools view_frames

# Echo specific transform
ros2 run tf2_ros tf2_echo tool0 camera_link
```

#### Using RViz
```bash
# Launch RViz with camera view configuration
ros2 run rviz2 rviz2 -d src/lra_vision/rviz/camera_view.rviz
```

### Testing

#### Running All Tests
```bash
colcon test --packages-select lra_vision
colcon test-result --verbose
```

#### Running Specific Tests
```bash
# Run camera detector tests
colcon test --packages-select lra_vision --ctest-args -R test_camera_detector

# Run calibration tests
colcon test --packages-select lra_vision --ctest-args -R test_camera_calibration

# Run TF broadcaster tests
colcon test --packages-select lra_vision --ctest-args -R test_tf_broadcaster

# Run image processor tests
colcon test --packages-select lra_vision --ctest-args -R test_image_processor

# Run ArUco detector tests
colcon test --packages-select lra_vision --ctest-args -R test_aruco_detector
```

### API Usage Examples

#### Camera Detection (C++)
```cpp
#include "lra_vision/camera_detector.hpp"

// Detect all available cameras
auto cameras = CameraDetector::detect_all_cameras();

// Find Logitech StreamCam specifically
auto streamcam = CameraDetector::find_streamcam();

// Validate camera device
bool valid = CameraDetector::is_valid_camera_device("/dev/video2");
```

#### Camera Calibration (C++)
```cpp
#include "lra_vision/camera_calibration.hpp"

// Configure calibration
CalibrationConfig config;
config.board_width = 9;
config.board_height = 6;
config.square_size = 0.025;

// Initialize calibrator
CameraCalibrator calibrator(config);

// Add calibration images
calibrator.add_image(image);

// Perform calibration
auto result = calibrator.calibrate();

// Save calibration results
calibrator.save_calibration("camera_info.yaml");
```

#### Image Processing (C++)
```cpp
#include "lra_vision/image_processor.hpp"

// Configure processing parameters
ProcessingParams params = ProcessingParams::default_for_caps();

// Initialize processor
ImageProcessor processor(params);

// Detect objects in image
auto objects = processor.detect_objects(image);

// Detect objects by color
auto red_objects = processor.detect_objects_by_color(image, "red");
```

#### TF Broadcasting (C++)
```cpp
#include "lra_vision/camera_tf_broadcaster.hpp"

// Configure camera mount
CameraMountConfig config = CameraMountConfig::overhead(0.05);

// Initialize broadcaster
CameraTfBroadcaster broadcaster(node, config);

// Initialize and update
broadcaster.initialize();
broadcaster.update();  // Publish transforms
```

## Troubleshooting

### Camera Not Found
```bash
# List video devices
ls -la /dev/video*

# Check permissions
sudo usermod -a -G video $USER

# Test camera
v4l2-ctl --list-devices
```

### Calibration Issues
1. Ensure good lighting
2. Use a proper chessboard (printed accurately)
3. Capture images from different angles
4. Minimum 30 images recommended

### TF Issues
```bash
# View TF tree
ros2 run tf2_tools view_frames

# Echo transforms
ros2 run tf2_ros tf2_echo tool0 camera_link
```

## License



## Authors



