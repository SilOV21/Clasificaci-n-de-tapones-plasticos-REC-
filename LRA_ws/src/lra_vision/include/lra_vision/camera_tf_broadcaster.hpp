// =============================================================================
// LRA Vision Package - Camera TF Broadcaster
// TF broadcasting for camera-UR3 relationship
// ROS2 Jazzy Jalisco - C++17
// =============================================================================
/**
 * @file camera_tf_broadcaster.hpp
 * @brief TF broadcaster for camera-robot transformation.
 * 
 * This module provides TF broadcasting for the Logitech StreamCam
 * mounted on the UR3 robotic arm. The camera is positioned 5cm above
 * the end effector with configurable orientation.
 * 
 * Frame Structure:
 * - world: Fixed world frame
 * - base_link: UR3 base frame
 * - shoulder_link, upper_arm_link, forearm_link, wrist_1_link, wrist_2_link, wrist_3_link: UR3 joints
 * - tool0: End effector frame
 * - camera_link: Camera mounting frame (5cm above tool0)
 * - camera_optical_frame: Camera optical frame (Z forward, X right, Y down)
 * 
 * @author Dr. Asil
 * @date March 2026
 * @copyright MIT License
 */

#ifndef LRA_VISION__CAMERA_TF_BROADCASTER_HPP_
#define LRA_VISION__CAMERA_TF_BROADCASTER_HPP_

#include <string>
#include <memory>
#include <array>

#include <rclcpp/rclcpp.hpp>
#include <tf2_ros/transform_broadcaster.h>
#include <tf2_ros/static_transform_broadcaster.h>
#include <tf2_ros/buffer.h>
#include <tf2_ros/transform_listener.h>
#include <tf2/transform_datatypes.h>
#include <tf2/exceptions.h>
#include <tf2/time.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <geometry_msgs/msg/pose.hpp>
#include <geometry_msgs/msg/point_stamped.hpp>
#include <std_msgs/msg/header.hpp>

namespace lra_vision
{

/**
 * @struct CameraMountConfig
 * @brief Configuration for camera mounting on UR3.
 */
struct CameraMountConfig
{
  // Translation from tool0 to camera (in meters)
  double translation_x = 0.0;      ///< X translation (forward)
  double translation_y = 0.0;      ///< Y translation (left)
  double translation_z = 0.05;     ///< Z translation (up) - 5cm above UR3
  
  // Rotation (RPY in radians)
  double roll = 0.0;               ///< Roll angle
  double pitch = 0.0;              ///< Pitch angle (typically -90deg for downward view)
  double yaw = 0.0;                ///< Yaw angle
  
  // Frame names
  std::string parent_frame = "tool0";         ///< Parent frame (UR3 end effector)
  std::string camera_frame = "camera_link";    ///< Camera frame
  std::string optical_frame = "camera_optical_frame"; ///< Optical frame
  
  /**
   * @brief Create default configuration for overhead mounting.
   * @param height Height above tool0 in meters (default 5cm).
   * @return Configuration for overhead camera.
   */
  static CameraMountConfig overhead(double height = 0.05);
  
  /**
   * @brief Create configuration for angled mounting.
   * @param angle_degrees Tilt angle in degrees.
   * @param height Height above tool0 in meters.
   * @return Configuration for angled camera.
   */
  static CameraMountConfig angled(double angle_degrees, double height = 0.05);
  
  /**
   * @brief Load configuration from YAML file.
   * @param filepath Path to YAML configuration.
   * @return Loaded configuration.
   */
  static CameraMountConfig from_yaml(const std::string& filepath);
};

/**
 * @class CameraTfBroadcaster
 * @brief Broadcasts TF transforms for camera-robot relationship.
 * 
 * This class manages the TF tree for the camera mounted on the UR3:
 * - Broadcasts static transform from tool0 to camera_link
 * - Broadcasts static transform from camera_link to camera_optical_frame
 * - Can listen to UR3 joint states for dynamic transform updates
 * 
 * @example
 * @code
 * rclcpp::init(argc, argv);
 * auto node = std::make_shared<rclcpp::Node>("tf_broadcaster");
 * 
 * CameraMountConfig config;
 * config.translation_z = 0.05; // 5cm above UR3
 * 
 * CameraTfBroadcaster broadcaster(node, config);
 * 
 * rclcpp::spin(node);
 * @endcode
 */
class CameraTfBroadcaster
{
public:
  /**
   * @brief Construct TF broadcaster with configuration.
   * @param node ROS2 node.
   * @param config Camera mounting configuration.
   */
  CameraTfBroadcaster(
    rclcpp::Node::SharedPtr node,
    const CameraMountConfig& config = CameraMountConfig()
  );
  
  /**
   * @brief Initialize broadcasters and publish static transforms.
   */
  void initialize();
  
  /**
   * @brief Update and publish transforms (call periodically).
   */
  void update();
  
  /**
   * @brief Publish static transforms (call once after initialization).
   */
  void publish_static_transforms();
  
  /**
   * @brief Get current camera transform relative to parent frame.
   * @return TransformStamped from parent to camera.
   */
  geometry_msgs::msg::TransformStamped get_camera_transform() const;
  
  /**
   * @brief Get camera pose in world frame.
   * @return Pose of camera in world frame.
   */
  geometry_msgs::msg::Pose get_camera_pose_world() const;
  
  /**
   * @brief Transform a point from camera frame to world frame.
   * @param point Point in camera frame (x, y, z).
   * @return Point in world frame.
   */
  std::array<double, 3> transform_to_world(const std::array<double, 3>& point) const;
  
  /**
   * @brief Transform a point from world frame to camera frame.
   * @param point Point in world frame (x, y, z).
   * @return Point in camera frame.
   */
  std::array<double, 3> transform_to_camera(const std::array<double, 3>& point) const;
  
  /**
   * @brief Update mounting configuration.
   * @param config New configuration.
   */
  void update_config(const CameraMountConfig& config);
  
  /**
   * @brief Get current configuration.
   * @return Current mounting configuration.
   */
  const CameraMountConfig& get_config() const { return config_; }
  
  /**
   * @brief Set the parent frame dynamically.
   * @param frame_name New parent frame name.
   */
  void set_parent_frame(const std::string& frame_name);
  
  /**
   * @brief Check if transform is available.
   * @param target_frame Target frame.
   * @param source_frame Source frame.
   * @return True if transform can be computed.
   */
  bool can_transform(
    const std::string& target_frame,
    const std::string& source_frame
  ) const;

private:
  rclcpp::Node::SharedPtr node_;
  CameraMountConfig config_;
  
  // TF broadcasters
  std::shared_ptr<tf2_ros::StaticTransformBroadcaster> static_broadcaster_;
  std::shared_ptr<tf2_ros::TransformBroadcaster> dynamic_broadcaster_;
  
  // TF buffer for lookups
  std::shared_ptr<tf2_ros::Buffer> tf_buffer_;
  std::shared_ptr<tf2_ros::TransformListener> tf_listener_;
  
  /**
   * @brief Create transform from RPY angles.
   * @param x Translation X.
   * @param y Translation Y.
   * @param z Translation Z.
   * @param roll Roll angle in radians.
   * @param pitch Pitch angle in radians.
   * @param yaw Yaw angle in radians.
   * @return TransformStamped message.
   */
  geometry_msgs::msg::TransformStamped create_transform(
    double x, double y, double z,
    double roll, double pitch, double yaw
  ) const;
  
  /**
   * @brief Create the optical frame transform (Z forward convention).
   * @return Transform from camera_link to camera_optical_frame.
   */
  geometry_msgs::msg::TransformStamped create_optical_transform() const;
};

/**
 * @brief Utility functions for TF operations.
 */
namespace tf_utils
{
/**
 * @brief Convert Euler angles to quaternion.
 * @param roll Roll angle in radians.
 * @param pitch Pitch angle in radians.
 * @param yaw Yaw angle in radians.
 * @return Quaternion (x, y, z, w).
 */
std::array<double, 4> euler_to_quaternion(double roll, double pitch, double yaw);

/**
 * @brief Convert quaternion to Euler angles.
 * @param q Quaternion (x, y, z, w).
 * @return Euler angles (roll, pitch, yaw) in radians.
 */
std::array<double, 3> quaternion_to_euler(const std::array<double, 4>& q);

/**
 * @brief Create a TransformStamped message.
 * @param parent_frame Parent frame ID.
 * @param child_frame Child frame ID.
 * @param x Translation X.
 * @param y Translation Y.
 * @param z Translation Z.
 * @param qx Quaternion X.
 * @param qy Quaternion Y.
 * @param qz Quaternion Z.
 * @param qw Quaternion W.
 * @return TransformStamped message.
 */
geometry_msgs::msg::TransformStamped make_transform(
  const std::string& parent_frame,
  const std::string& child_frame,
  double x, double y, double z,
  double qx, double qy, double qz, double qw
);

/**
 * @brief Create a TransformStamped message from RPY.
 * @param parent_frame Parent frame ID.
 * @param child_frame Child frame ID.
 * @param x Translation X.
 * @param y Translation Y.
 * @param z Translation Z.
 * @param roll Roll angle in radians.
 * @param pitch Pitch angle in radians.
 * @param yaw Yaw angle in radians.
 * @return TransformStamped message.
 */
geometry_msgs::msg::TransformStamped make_transform_rpy(
  const std::string& parent_frame,
  const std::string& child_frame,
  double x, double y, double z,
  double roll, double pitch, double yaw
);

}  // namespace tf_utils

}  // namespace lra_vision

#endif  // LRA_VISION__CAMERA_TF_BROADCASTER_HPP_