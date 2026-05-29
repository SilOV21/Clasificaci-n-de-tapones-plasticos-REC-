# UR3 Vision Control: Central Motion and Suction Gripper Sequencer for Cap Sorting

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

This document presents the **UR3 Vision Control** package, the main robotic manipulation module for the REC project. It manages the coordination of robot movements and gripper operations during the cap sorting process. Subscribed to cap detection coordinates (`/ur3/target_point`) and sorting bin targets (`/tapones/caja_asignada`), this package uses MoveIt's Inverse Kinematics (IK) service (`/compute_ik`) to find joint solutions for picking caps. It sequences movements through standard trajectory controllers and communicates with the universal robot's hardware interfaces to trigger pneumatic suction valves via the `/io_and_status_controller/set_io` service.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Methodology](#3-methodology)
4. [Implementation Details](#4-implementation-details)
5. [API Reference & Topics](#5-api-reference--topics)
6. [Usage Instructions](#6-usage-instructions)

---

## 1. Introduction

### 1.1 Problem Statement
In automated sorting lines, robots need to pick parts from unpredictable locations on a surface. This requires safe path planning, collision avoidance, gripper control, and precise coordination with the vision system to prevent sorting crashes.

### 1.2 Objectives
*   **O1: central Motion Coordination:** Implement a robust pick-and-place sequencer based on MoveIt IK.
*   **O2: Tool Configuration:** Interface with the physical tool attachment, accounting for a 23.0 cm Tool Center Point (TCP).
*   **O3: Suction Control Integration:** Expose services to activate/deactivate the vacuum gripper.
*   **O4: Visual Markers:** Publish marker shapes to display target coordinate points in RViz.

---

## 2. System Architecture

The robot manipulator is controlled by executing joint trajectories computed using Inverse Kinematics queries:

```
                  +--------------------------------+
                  |         REC Vision             |
                  +-------+----------------+-------+
                          |                |
                (3D Target Point)    (Box Assignment)
                          |                |
                          v                v
+----------------------------------------------------------+
|                     UR3 Pick & Sort                      |
|                                                          |
|  +----------------------------------------------------+  |
|  |                 State Sequencer                    |  |
|  |  * Coordinates picking loops                       |  |
|  |  * Queries MoveIt IK (/compute_ik)                 |  |
|  |  * Publishes trajectories to Joint Controller      |  |
|  |  * Triggers hardware IO services                   |  |
|  +-----------------------+----------------------------+  |
|                          |                               |
|        (Joint Trajectories)   (Gripper IO Calls)         |
|                          |            |                  |
+--------------------------+------------+------------------+
                           |            |
                           v            v
  +-------------------------------------+------------------+
  |               UR3 / UR3e Robotic Manipulator           |
  |  (scaled_joint_trajectory_controller, set_io service)  |
  +--------------------------------------------------------+
```

*   **MoveIt Interaction:** Instead of running full planning scenes which add overhead, this package uses direct IK service calls to `/compute_ik` for the `ur_manipulator` group.
*   **IO controller:** Controls suction using the `/io_and_status_controller/set_io` service to switch digital outputs on the robot tool header.

---

## 3. Methodology

### 3.1 Inverse Kinematics Resolution
For each detected cap, the system uses MoveIt's `/compute_ik` service to find joint states. 
1. The target pose is defined with the gripper perpendicular to the table surface:

$$
q_{\text{orient}} = [w=0, x=1, y=0, z=0]^T \quad (\text{Roll } 180^{\circ})
$$

2. In cases where joint limits are reached, the system rotates the wrist to try alternate orientations:

$$
\theta_{\text{wrist3}} \in \{0, \frac{\pi}{2}, -\frac{\pi}{2}, \pi\}
$$

3. A joint distance metric is applied to select the solution closest to the current joint positions:

$$
\text{cost} = \sum_{i=1}^{6} w_i \cdot |q_i - q_{i,\text{current}}|^2
$$

   where $w_i$ represents the joint weights configured in the node parameters.

### 3.2 Suction Cup & Gripper Dimensions
The physical tool center point (TCP) extension is 23.0 cm, comprising:
*   Pneumatic gripper module: 13.7 cm (`distancia_gripper`)
*   Suction cup extension: 9.3 cm (`distancia_ventosa`)

To safely pick caps, the sequencer uses three vertical offsets along the Z axis relative to the table surface:
1.  **Approach Pose:** $z_{\text{target}} + 23.0\text{ cm} + 8.0\text{ cm}$
2.  **Contact Pose:** $z_{\text{target}} + 23.0\text{ cm} - 5.0\text{ mm}$ (includes a 5 mm compression safety offset to ensure contact)
3.  **Retreat Pose:** $z_{\text{target}} + 23.0\text{ cm} + 12.0\text{ cm}$

### 3.3 Trajectory Planning Sequence
```
     (Start) ---> [Home Position]
                       |
                       | (Listens to /ur3/target_point)
                       v
                 [Approach Pose]
                       |
                       | (Linear approach)
                       v
                 [Contact Pose] ---> [Activate Suction IO]
                       |
                       | (Lift)
                       v
                 [Retreat Pose]
                       |
                       | (Move to color bin)
                       v
               [Drop-off Position] ---> [Deactivate Suction IO]
                       |
                       |
                       v
               Return to [Home Position]
```

---

## 4. Implementation Details

The package contains several nodes and scripts under the [ur3_vision_control](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/ur3_vision_control/ur3_vision_control/ur3_vision_control) module:

*   **[ur3_pick_sort.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/ur3_vision_control/ur3_vision_control/ur3_vision_control/ur3_pick_sort.py):** The main controller node. It handles the state machine, resolves IK solutions, checks joint jumps to prevent erratic movements, publishes collision objects representing the work table, and executes sorting operations.
*   **[ur3_controller.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/ur3_vision_control/ur3_vision_control/ur3_vision_control/ur3_controller.py):** A simpler control script used for validation and manual coordinates testing.
*   **[inicio.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/ur3_vision_control/ur3_vision_control/ur3_vision_control/inicio.py):** A startup utility script to move the robotic manipulator back to its Home configuration.
*   **[vision_fake_sort.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/ur3_vision_control/ur3_vision_control/ur3_vision_control/vision_fake_sort.py):** A simulation helper that publishes mock coordinates and color classifications to test the movement sequence without vision hardware.
*   **[launch.py](file:///home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws/src/ur3_vision_control/ur3_vision_control/launch/launch.py):** Aggregates all nodes into a single startup file:
    1.  Starts the MoveIt execution configurations.
    2.  Starts the camera stream and TF publishers.
    3.  Launches `ur3_pick_sort` after a delay of 8.0 seconds to wait for MoveIt.
    4.  Launches the classification detector after a delay of 25.0 seconds once the robot reaches its Home position.

---

## 5. API Reference & Topics

### 5.1 Subscribed Topics
*   `/ur3/target_point` (`geometry_msgs/Point`): 3D coordinates $(x,y,z)$ of the target cap.
*   `/tapones/caja_asignada` (`std_msgs/Int32`): The destination bin number (1 to 6) matching the classified color.
*   `/joint_states` (`sensor_msgs/JointState`): Real-time joint positions used to calculate joint distance costs.

### 5.2 Published Topics
*   `/scaled_joint_trajectory_controller/joint_trajectory` (`trajectory_msgs/JointTrajectory`): The trajectory commands sent to the robot controller.
*   `/vision_enable` (`std_msgs/Bool`, Latched): Tells the vision detector to halt processing during robot movement.
*   `/sorting_markers` (`visualization_msgs/MarkerArray`): Diagnostic markers displayed in RViz.
*   `/collision_object` (`moveit_msgs/CollisionObject`): Spawns protective virtual collision walls around the workspace.

### 5.3 Services Called
*   `/compute_ik` (`moveit_msgs/srv/GetPositionIK`): Computes joint states from Cartesian coordinates.
*   `/io_and_status_controller/set_io` (`ur_msgs/srv/SetIO`): Toggles tool outputs to control the suction gripper.

---

## 6. Usage Instructions

### 6.1 Compiling the Package
To compile this package along with its dependencies:
```bash
cd /home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws
colcon build --packages-select ur3_vision_control
source install/setup.bash
```

### 6.2 Running Simulation Mode
To verify movements and trajectory planning in simulation:
1.  **Launch the mock joint driver and MoveIt planner:**
    ```bash
    ros2 launch ur_robot_driver ur_control.launch.py ur_type:=ur3e robot_ip:=192.168.0.1 use_fake_hardware:=true launch_rviz:=true
    ```
2.  **Start the mock vision publisher:**
    ```bash
    ros2 run ur3_vision_control vision_fake_sort
    ```
3.  **Launch the pick-and-sort node with simulation flags enabled:**
    ```bash
    ros2 run ur3_vision_control ur3_pick_sort --ros-args -p simulate_gripper:=true
    ```

### 6.3 Running Lab Mode (Physical Robot)
Before running this launch command, ensure the UR3e manipulator is powered on and reachable at the configured IP:
```bash
ros2 launch ur3_vision_control launch.py
```
*This launch file manages startup delays to ensure MoveIt and tf services are fully initialized before running trajectories.*
