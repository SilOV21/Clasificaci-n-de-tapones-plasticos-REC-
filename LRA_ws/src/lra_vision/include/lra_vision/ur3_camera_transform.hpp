// =============================================================================
// LRA Vision Package - UR3 Camera Transform Header
// Specific transforms for UR3-Logitech StreamCam configuration
// ROS2 Jazzy Jalisco - C++17
// =============================================================================
/**
 * @file ur3_camera_transform.hpp
 * @brief UR3-specific camera mounting configurations and transforms.
 *
 * The Logitech StreamCam is mounted 5cm above the UR3 end effector (tool0 frame).
 * This module provides utilities for computing transforms between the camera
 * and robot coordinate systems.
 *
 * @author Dr. Asil
 * @date March 2026
 * @copyright MIT License
 */

#ifndef LRA_VISION__UR3_CAMERA_TRANSFORM_HPP_
#define LRA_VISION__UR3_CAMERA_TRANSFORM_HPP_

#include <array>
#include <vector>
#include <string>
#include <opencv2/opencv.hpp>
#include "lra_vision/camera_tf_broadcaster.hpp"

namespace lra_vision
{

/**
 * @namespace ur3_camera
 * @brief UR3-specific camera mounting configurations.
 *
 * The Logitech StreamCam is mounted 5cm above the UR3 end effector (tool0 frame).
 * This namespace provides utilities for computing transforms between the camera
 * and robot coordinate systems.
 */
namespace ur3_camera
{

/**
 * @brief UR3 link names in order from base to end effector.
 */
extern const std::vector<std::string> UR3_LINK_NAMES;

/**
 * @brief Default camera mounting configuration for UR3.
 *
 * The camera is mounted:
 * - 5cm above the tool0 frame (end effector)
 * - Pointing downward (pitch = 180 degrees)
 * - Centered on the tool center point
 */
CameraMountConfig get_default_mount_config();

/**
 * @brief Get camera configuration for side mounting.
 *
 * @param angle_degrees Angle from vertical (0 = straight down).
 * @param distance Distance from tool0 center in meters.
 */
CameraMountConfig get_side_mount_config(double angle_degrees, double distance);

/**
 * @brief Get camera configuration for side mounting with default parameters.
 */
CameraMountConfig get_side_mount_config();

/**
 * @brief Get camera configuration for in-hand mounting.
 *
 * Camera is mounted on the gripper, looking forward.
 */
CameraMountConfig get_in_hand_mount_config();

/**
 * @brief Compute transform from camera to TCP (Tool Center Point).
 *
 * Given a point in camera coordinates, compute where it is relative
 * to the tool center point. This is useful for picking objects.
 *
 * @param camera_point Point in camera frame (x, y, z in meters).
 * @param tcp_offset Offset from tool0 to TCP (default: 0 for tool0 = TCP).
 * @return Point in TCP coordinates.
 */
std::array<double, 3> camera_to_tcp(
  const std::array<double, 3>& camera_point,
  double tcp_offset);

/**
 * @brief Compute transform from camera to TCP (Tool Center Point) with default offset.
 *
 * @param camera_point Point in camera frame (x, y, z in meters).
 * @return Point in TCP coordinates.
 */
std::array<double, 3> camera_to_tcp(const std::array<double, 3>& camera_point);

/**
 * @brief Compute grip pose from camera observation.
 *
 * Given a detected object position in camera frame, compute the
 * robot pose needed to grasp it.
 *
 * @param object_position Object position in camera frame (meters).
 * @param approach_height Height to approach from (meters above object).
 * @return Gripper pose as (x, y, z, roll, pitch, yaw).
 */
std::array<double, 6> compute_grip_pose(
  const std::array<double, 3>& object_position,
  double approach_height);

/**
 * @brief Compute grip pose from camera observation with default approach height.
 *
 * @param object_position Object position in camera frame (meters).
 * @return Gripper pose as (x, y, z, roll, pitch, yaw).
 */
std::array<double, 6> compute_grip_pose(const std::array<double, 3>& object_position);

/**
 * @brief Logitech StreamCam specific parameters.
 */
struct StreamCamParameters
{
  // Intrinsic parameters (typical values for 1080p mode)
  double focal_length_x = 1000.0;    // Approximate focal length (pixels)
  double focal_length_y = 1000.0;
  double center_x = 960.0;           // Image center (1920x1080)
  double center_y = 540.0;

  // Distortion coefficients (typical for webcams)
  double k1 = 0.0;
  double k2 = 0.0;
  double p1 = 0.0;
  double p2 = 0.0;
  double k3 = 0.0;

  // Supported resolutions
  std::vector<std::pair<int, int>> resolutions = {
    {1920, 1080},  // Full HD
    {1280, 720},   // HD
    {640, 480},    // VGA
    {320, 240}     // QVGA
  };

  // Supported frame rates
  std::vector<int> frame_rates = {30, 60};

  /**
   * @brief Get camera matrix for a specific resolution.
   */
  cv::Mat get_camera_matrix(int width, int height) const;

  /**
   * @brief Get distortion coefficients.
   */
  cv::Mat get_distortion_coefficients() const;
};

}  // namespace ur3_camera

}  // namespace lra_vision

#endif  // LRA_VISION__UR3_CAMERA_TRANSFORM_HPP_