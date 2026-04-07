# LRA Vision: A ROS2-Based Vision System for Robotic Manipulation

## Technical Documentation

**Version:** 1.0.0  
**Date:** 6 April 2026  
**ROS2 Distribution:** Humble Hawksbill (Docker) 
**License:** To be defined

---

## Authors and Affiliation

| Author | Affiliation |
|--------|-------------|
| | |

**Correspondence:**

**Institution:**  
Universidad Politécnica de Madrid  
Laboratorio de Automática y Robótica (LRA)  
REC Project: Plastic Cap Classification using UR3 Robotic Arm

---

## Abstract

This document presents the LRA Vision package, a comprehensive ROS2-based vision subsystem developed for the REC project at the Laboratorio de Automática y Robótica, Universidad Politécnica de Madrid. The system provides real-time camera interfacing, intrinsic calibration, and extrinsic hand-eye calibration capabilities for a camera mounted on a UR3 robotic manipulator. The architecture employs a modular design with primary nodes for Camera Management via `v4l2_camera`, Camera Calibration, ArUco Detection, and URDF-based TF Broadcasting via `robot_state_publisher`. 

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Methodology](#3-methodology)
4. [Implementation Details](#4-implementation-details)
5. [Experimental Setup](#5-experimental-setup)
6. [Calibration Methodology](#6-calibration-methodology)
7. [Usage Instructions](#7-usage-instructions)

---

## 1. Introduction

### 1.1 Problem Statement
Robotic manipulation tasks requiring visual servoing or object recognition depend critically on accurate camera calibration and precise knowledge of the camera pose relative to the robot end-effector.

### 1.2 Objectives
- **O1:** Provide a hardware-abstraction layer for the USB camera
- **O2:** Implement chessboard-based intrinsic calibration
- **O3:** Publish accurate TF transforms for the camera-UR3 kinematic chain via URDF
- **O4:** Enable ArUco marker detection

---

## 2. System Architecture

### 2.1 TF Transformation Tree

The coordinate frames follow the ROS2 REP-105 convention for optical frames:

`world` → `base_link` → … → `tool0` → `camera_link` → `camera_optical_frame`

---

## 3. Methodology

### 3.1 Camera Detection and Management
The system launches `v4l2_camera` to capture video and provide ROS2 topics for the raw image and camera info.

### 3.2 Intrinsic Calibration
Calibration is performed using a chessboard pattern, optimizing intrinsic parameters using OpenCV.

### 3.3 TF Transformation Tree
The static transform is published by `robot_state_publisher` using the definitions in `camera.xacro`.

---

### 4.1 Node Specifications

#### 4.1.1 Camera Manager Launch (`camera_manager.launch.py`)
Launches the `v4l2_camera` node with configured parameters for resolution, device, and topics.

#### 4.1.2 Camera Calibrator Node
Subscribes to images and provides services (`/capture`, `/calibrate`, `/save`, `/reset`) to collect chessboard data and save the calculated intrinsic calibration.

#### 4.1.3 ArUco Detector Node
Subscribes to image and calibration data to detect markers (e.g., `DICT_4X4_50`) and publishes `MarkerArray`, `PoseArray`, and annotated images.

#### 4.1.4 URDF Upload Launch (`upload_urdf.launch.py`)
Processes `camera.xacro` and launches `robot_state_publisher` and `joint_state_publisher` to publish static TF frames (`tool0` → `camera_link` → `camera_optical_frame`).

---

## 5. Experimental Setup

### 5.1 Software Environment
Tested on ROS2 Humble (via Docker)

---

## 6. Calibration Methodology

### 6.1 Intrinsic Calibration Procedure
1. **Launch calibrator**: `ros2 launch lra_vision camera_calibration.launch.py`
2. **Capture images**: `ros2 service call /calibrate_camera lra_vision/srv/CalibrateCamera "{action: 'capture'}"`
3. **Execute calibration**: `ros2 service call /calibrate_camera lra_vision/srv/CalibrateCamera "{action: 'calibrate'}"`    
4. **Save results**: `ros2 service call /calibrate_camera lra_vision/srv/CalibrateCamera "{action: 'save'}"`

---

## 7. Usage Instructions

### 7.1 Build Package
```bash
# Execute within ROS2 Humble Docker container
colcon build --packages-select lra_vision
source install/setup.bash
```

### 7.2 Launching Nodes
```bash
# Camera manager
ros2 launch lra_vision camera_manager.launch.py

# TF broadcaster (URDF)
ros2 launch lra_vision upload_urdf.launch.py

# Camera calibrator
ros2 launch lra_vision camera_calibration.launch.py

# ArUco detector
ros2 launch lra_vision aruco_detector.launch.py
```

### 7.3 Visualisation
```bash
# RViz visualisation
rviz2
```
