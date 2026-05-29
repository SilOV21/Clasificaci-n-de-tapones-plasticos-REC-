# REC Vision: A ROS2-Based HSV Clustering and Plastic Cap Classifier

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

This document presents the **REC Vision** package, a computer vision subsystem designed for the REC project. The system classifies plastic bottle caps by color without requiring hardcoded color threshold values. It splits the process into a calibration phase and a classification phase:
1. **Calibration:** Uses OpenCV K-Means clustering on HSV data to dynamically identify color categories.
2. **Classification:** Computes Euclidean distances to these color centroids in real time, projecting cap positions into 3D robot base coordinates (`/ur3/target_point`) and publishing bin assignments (`/tapones/caja_asignada`).

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Methodology](#3-methodology)
4. [Implementation Details](#4-implementation-details)
5. [Configuration & Parameters](#5-configuration--parameters)
6. [Usage Instructions](#6-usage-instructions)

---

## 1. Introduction

### 1.1 Problem Statement
Sorting objects by color using standard methods like HSV threshold segmentation is difficult when lighting conditions change. Setting hardcoded color limits often fails if the environment shifts.

### 1.2 Objectives
*   **O1: Dynamic Color Calibration:** Implement an HSV clustering algorithm using OpenCV's K-Means to automatically group cap colors.
*   **O2: Cap Extraction:** Detect circular plastic caps in the camera feed using Hough Circle Transforms.
*   **O3: Spatial Projection:** Convert 2D pixel coordinates of detected caps into 3D robot coordinate space (`base_link`) using intrinsic calibration parameters.
*   **O4: Centralized Telemetry:** Publish color assignments, cap counts, and annotated debug images.

---

## 2. System Architecture

The package contains two primary ROS2 Python nodes:

```
                  +--------------------------+
                  |    v4l2_camera_node      |
                  +------------+-------------+
                               |
                   (/camera/image_raw, Image)
                               |
                               v
+--------------------------------------------------------+
|                      REC Vision                        |
|                                                        |
|  +--------------------------------------------------+  |
|  |             ColorCalibratorNode                  |  |
|  |  * Receives image frames                         |  |
|  |  * Extracts cap HSV values                       |  |
|  |  * Applies K-Means clustering                    |  |
|  |  * Publishes HSV centroids (Latched QoS)         |  |
|  +-----------------------+--------------------------+  |
|                          |                             |
|          (/clasificador/centros_hsv)                   |
|                          |                             |
|  +-----------------------v--------------------------+  |
|  |               DetectorTapones                    |  |
|  |  * Listens to latched HSV centroids              |  |
|  |  * Matches new caps via Euclidean distance       |  |
|  |  * Computes 3D coordinates using camera matrix   |  |
|  |  * Publishes target coordinates & bin indexes    |  |
|  +--------------------------------------------------+  |
+--------------------------------------------------------+
```

*   **ColorCalibratorNode:** Runs once at startup. It collects HSV samples from circular regions of detected caps, clusters them into $K$ distinct color groups, and publishes these centroids using a **Transient Local (Latched) QoS profile**.
*   **DetectorTapones:** Runs during active operation. It listens to the latched centroids, maps detected cap colors to the nearest cluster, and projects their coordinates into the robot's coordinate frame using TF transformation parameters.

---

## 3. Methodology

### 3.1 Cap Detection via Hough Circles
Both nodes use Hough Circle Transforms to locate caps in the image. Key extraction steps include:
1. Converting BGR input frames to grayscale and applying a Gaussian blur to reduce high-frequency noise.
2. Running `cv2.HoughCircles` to extract circles defined by center $(x_c, y_c)$ and radius $r$.
3. Masking the circular region to filter out background pixels.
4. Converting the masked region to the HSV color space and computing the average H, S, and V channel values.

### 3.2 Dynamic Color Classification (K-Means)
To ensure consistent cluster assignment across runs:
1. The calibrator initializes the random number generator seed using `cv2.setRNGSeed(0)`.
2. It collects HSV feature vectors:
   $$X = \{[h_i, s_i, v_i]^T \}_{i=1}^N$$
3. The K-Means algorithm runs to minimize the sum of squared distances to the cluster centroids:
   $$J = \sum_{j=1}^{K} \sum_{x \in S_j} \|x - \mu_j\|^2$$
   where $\mu_j$ represents the HSV centroid of the $j$-th color group.
4. These centroids are published as a flat 1D array (`[H0, S0, V0, H1, S1, V1, ...]`) and saved by the detector node.
5. In the detection phase, the color of a new cap $x_{new}$ is classified by finding the closest centroid:
   $$\text{box\_id} = \arg\min_{j \in \{1,\dots,K\}} \|x_{new} - \mu_j\|$$

### 3.3 3D Position Reconstruction
The detector projects the cap center from 2D pixel coordinates $(u, v)$ to a 3D coordinate point $P_{\text{cam}} = [X_c, Y_c, Z_c]^T$ in the camera frame:
1. It queries the camera matrix $K$ loaded from [camera_info.yaml](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/lra_hmi/lra_hmi/config/default_config.yaml):
   $$K = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}$$
2. Pixel coordinates are normalized:
   $$x_n = \frac{u - c_x}{f_x}, \quad y_n = \frac{v - c_y}{f_y}$$
3. The Z-coordinate is set to a constant physical distance $Z_c$ (distance from camera to table surface).
4. The 3D coordinates in the camera frame are computed as:
   $$X_c = x_n \cdot Z_c, \quad Y_c = y_n \cdot Z_c$$
5. Using a TF transform listener, the point is transformed into the robot's frame:
   $$P_{\text{base}} = T_{\text{base}}^{\text{camera}} \cdot P_{\text{cam}}$$

---

## 4. Implementation Details

### 4.1 Node Specifications

#### 4.1.1 `color_calibrator_node`
*   **Source:** [color_calibrator_node.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/rec_vision/rec_vision/color_calibrator_node.py)
*   **Subscribed Topics:**
    *   `/camera/camera_info` (`sensor_msgs/CameraInfo`)
    *   `/camera/image_raw` (`sensor_msgs/Image`)
*   **Published Topics:**
    *   `/clasificador/centros_hsv` (`std_msgs/Float32MultiArray`, Latched)
    *   `/clasificador/num_cajas` (`std_msgs/Int32`, Latched)
    *   `/clasificador/imagen_debug` (`sensor_msgs/Image`)
*   **Parameters:**
    *   `num_cajas` (default: `3`): Number of target sorting bins (1 to 6).
    *   `frames_muestreo` (default: `30`): Calibration frames to accumulate before running K-Means.
    *   `camera_info_yaml` (string, required): Path to the camera intrinsic parameters YAML.
    *   `show_debug` (default: `True`): Toggles local OpenCV window visualization.

#### 4.1.2 `detector_tapones`
*   **Source:** [detector_tapones.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/rec_vision/rec_vision/detector_tapones.py)
*   **Subscribed Topics:**
    *   `/camera/camera_info` (`sensor_msgs/CameraInfo`)
    *   `/camera/image_raw` (`sensor_msgs/Image`)
    *   `/clasificador/centros_hsv` (`std_msgs/Float32MultiArray`, Latched)
    *   `/clasificador/num_cajas` (`std_msgs/Int32`, Latched)
    *   `/vision_enable` (`std_msgs/Bool`)
*   **Published Topics:**
    *   `/tapones/caja_asignada` (`std_msgs/Int32`): The matched box number (1 to N).
    *   `/ur3/target_point` (`geometry_msgs/Point`): projected 3D coordinates in `base_link`.
    *   `/tapones/cantidad` (`std_msgs/Int32`): Count of visible caps.
    *   `/tapones/imagen_debug` (`sensor_msgs/Image`): annotated camera feed.
    *   `/vision_color` (`std_msgs/String`): text string representing the closest color.

---

## 5. Configuration & Parameters

Parameters are shared and mapped to launch configurations. Intrinsic calibrations are loaded using the OpenCV camera calibration format:
```yaml
# camera_info.yaml snippet
image_width: 640
image_height: 480
camera_name: camera
camera_matrix:
  rows: 3
  cols: 3
  data: [f_x, 0.0, c_x, 0.0, f_y, c_y, 0.0, 0.0, 1.0]
distortion_model: plumb_bob
distortion_coefficients:
  rows: 1
  cols: 5
  data: [k1, k2, p1, p2, k3]
```

---

## 6. Usage Instructions

### 6.1 Compiling the Package
Compile using `colcon` in the root of the workspace:
```bash
cd /home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws
colcon build --packages-select rec_vision
source install/setup.bash
```

### 6.2 Running in Offline Simulation Mode (Bag Testing)
1.  **Play sample image recording (MCAP bag file):**
    ```bash
    python3 src/rec_vision/rec_vision/mcap_publisher.py
    ```
2.  **Publish a static coordinate transform (acting as the robot's mount):**
    ```bash
    ros2 run tf2_ros static_transform_publisher \
      --x 0.4 --y 0 --z 0.5 --yaw 0 --pitch 3.1415 --roll 0 \
      --frame-id base_link --child-frame-id camera_optical_frame
    ```
3.  **Start the calibration node (run once):**
    ```bash
    ros2 launch rec_vision color_calibrator.launch.py num_cajas:=3 camera_info_yaml:=src/lra_hmi/lra_hmi/config/default_config.yaml
    ```
4.  **Start the detector node:**
    ```bash
    ros2 launch rec_vision detector_tapones.launch.py camera_info_yaml:=src/lra_hmi/lra_hmi/config/default_config.yaml
    ```

### 6.3 Running in Lab Mode (Physical Setup)
Launch the primary cameras, TFs, and calibrators:
```bash
# Terminal 1: Launch camera drivers and transforms
ros2 launch lra_vision camera_manager.launch.py
ros2 launch lra_vision upload_urdf.launch.py

# Terminal 2: Run color calibrator
ros2 launch rec_vision color_calibrator.launch.py num_cajas:=3

# Terminal 3: Run classification detector
ros2 launch rec_vision detector_tapones.launch.py
```
