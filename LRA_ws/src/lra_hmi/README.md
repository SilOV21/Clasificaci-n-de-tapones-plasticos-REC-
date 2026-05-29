# LRA HMI: A Graphical Interface and Centralized Subprocess Launcher for the UR3e Bottle-Cap Sorting Pipeline

## Technical Documentation

**Version:** 1.0.0  
**Date:** 29 May 2026  
**ROS2 Distribution:** Humble Hawksbill (Docker Container Integration)  

---

## Authors and Affiliation

| Author | Affiliation |
|--------|-------------|
| LRA Team | Universidad Politécnica de Madrid (UPM) |

**Correspondence:** `asil.arnous@opendeusto.es`  

**Institution:**  
Universidad Politécnica de Madrid  
Laboratorio de Automática y Robótica (LRA)  
REC Project: Plastic Cap Classification using UR3/UR3e Robotic Arm  

---

## Abstract

This document presents the **LRA HMI** package, a centralized PyQt5-based graphical human-machine interface and launcher developed for the REC project. Traditionally, operating a complex ROS2-based robotic pipeline (comprising robot drivers, MoveIt motion planners, video hardware interfaces, vision detectors, color calibrators, and custom trajectory control nodes) requires spawning and managing multiple terminal shells simultaneously. This HMI replaces this manual flow with a single graphical dashboard. It handles multi-process launching with process-group process isolation, monitors robot accessibility via background ping requests, pipes logs into a tabbed console, provides a live visual viewport of raw/debug camera topics, aggregates real-time sorting counters, and implements a hardwired software Emergency Stop (E-Stop) to shut down the manipulator and vision pipeline instantly.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Methodology](#3-methodology)
4. [Implementation Details](#4-implementation-details)
5. [Configuration and Design System](#5-configuration-and-design-system)
6. [Usage Instructions](#6-usage-instructions)

---

## 1. Introduction

### 1.1 Problem Statement
Operating the UR3e sorting pipeline involves running several ROS2 packages in a specific sequence:
1. Universal Robots driver (`ur_robot_driver`)
2. Static coordinate transform publishers (`tf2_ros`)
3. MoveIt path planner and motion controller (`ur_moveit_config`)
4. USB camera node (`v4l2_camera`)
5. Camera URDF/TF broadcaster (`lra_vision` upload)
6. Color calibration suite (`rec_vision` calibrator)
7. HSV-based cap detector (`rec_vision` detector)
8. Pick-and-sort trajectory sequencer (`ur3_vision_control` manipulator node)

Spawning these components across multiple bash terminals is error-prone, makes logging hard to trace, and lacks a centralized safety mechanism to stop execution if an error occurs.

### 1.2 Objectives
*   **O1: Centralized Launch Control:** Initialize the entire stack in the correct sequence using a single button.
*   **O2: Per-Subsystem Lifecycle Management:** Provide isolated start, stop, and restart operations for specific nodes.
*   **O3: Visual Telemetry & Logging:** Render live image streams and aggregate system output logs.
*   **O4: Real-time Analytics:** Display sorting statistics (caps sorted per box and per minute) with JSON report export features.
*   **O5: Emergency Stop Integration:** Provide a prominent emergency button to force-kill all subprocesses and disable the vision pipeline.

---

## 2. System Architecture

The HMI integrates a PyQt5 GUI loop with the ROS2 `rclpy` runtime using a single-threaded spinning design:

```
+--------------------------------------------------------+
|                      PyQt5 HMI                         |
|  +--------------------+        +--------------------+  |
|  |     MainWindow     |        |   ProcessManager   |  |
|  +---------+----------+        +---------+----------+  |
|            |                             |             |
|    (Qt Signals/Slots)            (Subprocess Pipes)    |
|            |                             |             |
|  +---------v----------+                  |             |
|  |     RosBridge      |                  v             |
|  |  (rclpy.spin_once) | <----+     [ROS2 Nodes]        |
|  +---------+----------+      |    (Driver, MoveIt,     |
|            |                 |     Vision, Pick/Sort)  |
|     (ROS2 Topics)            |                         |
|            |                 |                         |
|            +-----------------+                         |
+--------------------------------------------------------+
```

*   **GUI & ROS Coexistence:** To avoid threading issues between Qt and ROS2, the HMI uses a `QTimer` configured to fire every 50 ms. This timer executes `rclpy.spin_once(node, timeout_sec=0.0)`. This allows the GUI thread to handle incoming ROS callbacks without locking up.
*   **Background Monitoring:** A dedicated thread ([ConnectionMonitor](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/connection_monitor.py#L9)) checks the physical connection to the robot using ICMP pings. This keeps the network diagnostics isolated from the user interface.

---

## 3. Methodology

### 3.1 Multi-Process Management & Lifecycle Control
Subprocesses are spawned using `subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid)`. By setting the process group ID (`os.setsid`), the HMI groups the spawned node and all its child shells together. 

When a "Stop" command is triggered:
1. The HMI sends a `SIGTERM` to the process group via `os.killpg(pgid, signal.SIGTERM)`.
2. It waits up to 5 seconds for a clean shutdown.
3. If the process remains active, it escalates to `SIGKILL` (`os.killpg(pgid, signal.SIGKILL)`) to force-release resources.

### 3.2 Emergency Stop Behavior
When the **EMERGENCY STOP** button is pressed:
1. A hard shutdown command is issued directly to all running process groups using `SIGKILL` without waiting.
2. A `Bool(False)` message is published to `/vision_enable`. This informs the pick-and-sort node to halt operations, acting as a software interlock.
3. The system remains locked until the user clicks **REHABILITAR** on the dashboard, which republishes `Bool(True)` to `/vision_enable`.

### 3.3 Connection Diagnostics
The [ConnectionMonitor](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/connection_monitor.py#L9) thread runs a ping loop at 2-second intervals. It measures the round-trip time (RTT) to the robot's IP. If a packet is lost, the HMI updates its UI elements to warn the operator that the robot is offline.

---

## 4. Implementation Details

The source files are organized inside the `lra_hmi` Python module:

### 4.1 UI Components (Inside [ui/](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/))

*   **[MainWindow](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/main_window.py#L34):** The central window wrapper. It integrates the sub-panels into tabs, displays a top bar containing connection status LEDs and the E-Stop controls, and manages global exit events.
*   **[LauncherPanel](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/launcher_panel.py):** Implements controls for the launch groups. Group status is shown using custom colored LEDs matching their run state:
    *   `STOPPED`: Grey
    *   `STARTING`: Orange
    *   `RUNNING`: Green
    *   `CRASHED`: Red (exited with non-zero code)
    *   `STOPPING`: Yellow
*   **[CountersPanel](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/counters_panel.py#L47):** Displays counts of processed caps. It updates dynamically using data from `/tapones/caja_asignada`. The panel calculates the sorting rate in real time and can export session data to a JSON report containing timestamps and cap distributions.
*   **[StatusPanel](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/status_panel.py#L30):** Displays the current angles of the robot's six joints. If joint data is not received for more than 2 seconds, it flags the stream as stale. It also includes the vision toggle checkbox and a color indicator swatch.
*   **[CameraPanel](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/camera_panel.py):** Contains a selection list to choose between raw camera images (`/camera/image_raw`) and debug overlays (`/tapones/imagen_debug`). It converts ROS image messages to QImages for display.
*   **[LogPanel](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/log_panel.py):** Pipes logs from stdout and stderr of each running process group into separate tabbed terminal views.

### 4.2 ROS Node & Spawning Configuration (Inside [lra_hmi/](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/))

*   **[ros_bridge.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ros_bridge.py):** Extends `QObject`. It manages the subscriptions and publishers shown below:
    
    *   **Subscribed Topics:**
        *   `/tapones/cantidad` (`std_msgs/Int32`): Total number of detected caps.
        *   `/tapones/caja_asignada` (`std_msgs/Int32`): The bin ID where the last cap was sorted.
        *   `/clasificador/num_cajas` (`std_msgs/Int32`, Transient Local QoS): The active box configuration.
        *   `/vision_color` (`std_msgs/String`): The color name of the last sorted cap.
        *   `/joint_states` (`sensor_msgs/JointState`, Best Effort QoS): Joint position tracking.
        *   `/camera/image_raw` (`sensor_msgs/Image`, Best Effort QoS): Live camera feed.
        *   `/tapones/imagen_debug` (`sensor_msgs/Image`, Best Effort QoS): Debug images with classification overlays.
        
    *   **Published Topics:**
        *   `/vision_enable` (`std_msgs/Bool`): Enables or disables the vision pipeline.

*   **[process_manager.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/process_manager.py):** Maps each run key to a list of terminal command arguments:
    *   `driver`: Launches `ur_control.launch.py` from `ur_robot_driver`.
    *   `tf`: Launches `static_transform_publisher` to set static frames from `world` to `base_link`.
    *   `moveit`: Launches `ur_moveit.launch.py` to start planning services.
    *   `camera`: Runs `v4l2_camera_node` with the configured video device, resolution, and format.
    *   `camera_urdf`: Runs `upload_urdf.launch.py` in `lra_vision` to broadcast camera TF frames.
    *   `calibrator`: Runs `color_calibrator_node` in `rec_vision` with calibration settings.
    *   `detector`: Runs `detector_tapones` in `rec_vision` to detect caps.
    *   `pick_sort`: Runs `ur3_pick_sort` in `ur3_vision_control` with gripper parameters.

---

## 5. Configuration and Design System

### 5.1 YAML Parameter Hierarchy
HMI configurations are defined in [default_config.yaml](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/config/default_config.yaml). Settings modified via the GUI settings panel are persisted to `~/.lra_hmi.yaml` on exit.

```yaml
robot_ip: 169.254.12.28
ur_type: ur3e
num_boxes: 4

camera:
  video_device: /dev/video2
  width: 640
  height: 480
  framerate: 30
  pixel_format: YUYV
  frame_id: camera_optical_frame

camera_urdf:
  height: 0.045
  parent_frame: tool0
  camera_name: camera

calibrator:
  frames_muestreo: 30
  show_debug: false
  hough:
    min_radius: 33
    max_radius: 54
    min_dist: 75
    hough_param1: 21
    hough_param2: 27

detector:
  frames_muestreo: 30
  show_debug: true
  target_frame: base_link
  camera_frame: camera_optical_frame
  hough:
    min_radius: 33
    max_radius: 54
    min_dist: 75
    hough_param1: 21
    hough_param2: 27

pick_sort:
  simulate_gripper: false
  offset_x: 0.0
  offset_y: 0.0
```

### 5.2 Style and Aesthetic Tokens
The dashboard styles are detailed in the [ui/README.md](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/ui/README.md) file. The interface uses a dark SCADA color scheme:
*   **Palette:** Backgrounds use `#15171c` (base) and `#1b1d22` (panels). Accents use `#00b4ff` (light blue) and `#ffb000` (amber highlights).
*   **Typography:** Labels use `Inter` for readability, while numeric readouts and console outputs use `JetBrains Mono`.

---

## 6. Usage Instructions

### 6.1 Compiling the Package
The HMI is built using `colcon` inside the ROS2 Humble Docker container:
```bash
# Navigate to the workspace root
cd /home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws

# Build the HMI package
colcon build --packages-select lra_hmi

# Source the overlay
source install/setup.bash
```

### 6.2 Running the HMI

#### Option A: Running with a Physical UR3e Robot
Make sure your network configuration matches the IP address in [default_config.yaml](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/config/default_config.yaml).
```bash
ros2 launch lra_hmi hmi.launch.py
```

#### Option B: Running in Simulation Mode (Offline Testing)
To test the HMI without connecting to physical camera or robot hardware, run it with the `LRA_HMI_SIM` environment variable set:
```bash
export LRA_HMI_SIM=1
ros2 launch lra_hmi hmi.launch.py
```
*In simulation mode, the interface maps connection checks to `127.0.0.1` and uses mock launch parameters.*

### 6.3 X11 Display Forwarding
Because the HMI runs inside a Docker container, it requires access to the host's X11 server to display its window. 

1. On your host system, allow local Docker containers to connect to the X11 server:
   ```bash
   xhost +local:docker
   ```
2. Launch the container using `docker compose up`. The compose file will forward the `DISPLAY` environment variable and mount `/tmp/.X11-unix`.
3. If the window fails to open, verify that the `DISPLAY` variable is set correctly inside the container:
   ```bash
   echo $DISPLAY
   ```
