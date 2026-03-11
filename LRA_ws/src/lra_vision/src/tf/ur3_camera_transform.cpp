// =============================================================================
// LRA Vision Package - UR3 Camera Transform Implementation
// Specific transforms for UR3-Logitech StreamCam configuration
// ROS2 Jazzy Jalisco - C++17
// =============================================================================

#define _USE_MATH_DEFINES
#include "lra_vision/ur3_camera_transform.hpp"
#include <cmath>
#include <opencv2/opencv.hpp>

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
const std::vector<std::string> UR3_LINK_NAMES = {
  "base_link",
  "shoulder_link",
  "upper_arm_link",
  "forearm_link",
  "wrist_1_link",
  "wrist_2_link",
  "wrist_3_link",
  "tool0"
};

/**
 * @brief Default camera mounting configuration for UR3.
 * 
 * The camera is mounted:
 * - 5cm above the tool0 frame (end effector)
 * - Pointing downward (pitch = 180 degrees)
 * - Centered on the tool center point
 */
CameraMountConfig get_default_mount_config()
{
  CameraMountConfig config;
  config.translation_x = 0.0;      // Centered
  config.translation_y = 0.0;      // Centered
  config.translation_z = 0.05;     // 5cm above tool0
  config.roll = 0.0;               // No roll
  config.pitch = M_PI;             // 180 degrees (pointing down)
  config.yaw = 0.0;                // Forward facing
  config.parent_frame = "tool0";
  config.camera_frame = "camera_link";
  config.optical_frame = "camera_optical_frame";
  return config;
}

/**
 * @brief Get camera configuration for side mounting.
 * 
 * @param angle_degrees Angle from vertical (0 = straight down).
 * @param distance Distance from tool0 center in meters.
 */
CameraMountConfig get_side_mount_config(double angle_degrees, double distance)
{
  CameraMountConfig config;
  double angle_rad = angle_degrees * M_PI / 180.0;

  config.translation_x = distance * std::sin(angle_rad);
  config.translation_y = 0.0;
  config.translation_z = distance * std::cos(angle_rad);
  config.roll = 0.0;
  config.pitch = M_PI - angle_rad;  // Compensate for mounting angle
  config.yaw = 0.0;
  config.parent_frame = "tool0";
  config.camera_frame = "camera_link";
  config.optical_frame = "camera_optical_frame";
  return config;
}

CameraMountConfig get_side_mount_config()
{
  return get_side_mount_config(45.0, 0.08);
}

/**
 * @brief Get camera configuration for in-hand mounting.
 * 
 * Camera is mounted on the gripper, looking forward.
 */
CameraMountConfig get_in_hand_mount_config()
{
  CameraMountConfig config;
  config.translation_x = 0.05;     // 5cm forward from tool0
  config.translation_y = 0.0;
  config.translation_z = 0.02;     // 2cm above tool0
  config.roll = 0.0;
  config.pitch = 0.0;              // Looking forward
  config.yaw = 0.0;
  config.parent_frame = "tool0";
  config.camera_frame = "camera_link";
  config.optical_frame = "camera_optical_frame";
  return config;
}

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
  double tcp_offset)
{
  // For downward-facing camera mounted 5cm above tool0:
  // Camera X -> Robot -Y
  // Camera Y -> Robot -X
  // Camera Z -> Robot -Z (but inverted because camera looks down)

  std::array<double, 3> tcp_point;
  tcp_point[0] = -camera_point[1];              // X: -camera_y
  tcp_point[1] = -camera_point[0];              // Y: -camera_x
  tcp_point[2] = 0.05 - camera_point[2] + tcp_offset; // Z: 5cm - camera_z

  return tcp_point;
}

std::array<double, 3> camera_to_tcp(const std::array<double, 3>& camera_point)
{
  return camera_to_tcp(camera_point, 0.0);
}

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
  double approach_height)
{
  std::array<double, 6> pose;

  // Convert to TCP coordinates
  auto tcp_pos = camera_to_tcp(object_position);

  pose[0] = tcp_pos[0];  // X
  pose[1] = tcp_pos[1];  // Y
  pose[2] = tcp_pos[2] + approach_height;  // Z (above object)
  pose[3] = M_PI;        // Roll (gripper pointing down)
  pose[4] = 0.0;         // Pitch
  pose[5] = 0.0;         // Yaw

  return pose;
}

std::array<double, 6> compute_grip_pose(const std::array<double, 3>& object_position)
{
  return compute_grip_pose(object_position, 0.05);
}

/**
 * @brief Logitech StreamCam specific parameters.
 */
// StreamCamParameters struct moved to header file

// Implementation of StreamCamParameters methods
cv::Mat StreamCamParameters::get_camera_matrix(int width, int height) const
{
  double scale_x = width / 1920.0;
  double scale_y = height / 1080.0;

  cv::Mat K = cv::Mat::eye(3, 3, CV_64F);
  K.at<double>(0, 0) = focal_length_x * scale_x;
  K.at<double>(1, 1) = focal_length_y * scale_y;
  K.at<double>(0, 2) = center_x * scale_x;
  K.at<double>(1, 2) = center_y * scale_y;

  return K;
}

cv::Mat StreamCamParameters::get_distortion_coefficients() const
{
  cv::Mat D = cv::Mat::zeros(5, 1, CV_64F);
  D.at<double>(0, 0) = k1;
  D.at<double>(1, 0) = k2;
  D.at<double>(2, 0) = p1;
  D.at<double>(3, 0) = p2;
  D.at<double>(4, 0) = k3;
  return D;
}

}  // namespace ur3_camera

}  // namespace lra_vision