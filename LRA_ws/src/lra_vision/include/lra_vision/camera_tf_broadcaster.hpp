

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

struct CameraMountConfig
{

  double translation_x = 0.0;
  double translation_y = 0.0;
  double translation_z = 0.05;


  double roll = 0.0;
  double pitch = 0.0;
  double yaw = 0.0;


  std::string parent_frame = "tool0";
  std::string camera_frame = "camera_link";
  std::string optical_frame = "camera_optical_frame";


  static CameraMountConfig overhead(double height = 0.05);


  static CameraMountConfig angled(double angle_degrees, double height = 0.05);


  static CameraMountConfig from_yaml(const std::string& filepath);
};

class CameraTfBroadcaster
{
public:

  CameraTfBroadcaster(
    rclcpp::Node::SharedPtr node,
    const CameraMountConfig& config = CameraMountConfig()
  );


  void initialize();


  void update();


  void publish_static_transforms();


  geometry_msgs::msg::TransformStamped get_camera_transform() const;


  geometry_msgs::msg::Pose get_camera_pose_world() const;


  std::array<double, 3> transform_to_world(const std::array<double, 3>& point) const;


  std::array<double, 3> transform_to_camera(const std::array<double, 3>& point) const;


  void update_config(const CameraMountConfig& config);


  const CameraMountConfig& get_config() const { return config_; }


  void set_parent_frame(const std::string& frame_name);


  bool can_transform(
    const std::string& target_frame,
    const std::string& source_frame
  ) const;

private:
  rclcpp::Node::SharedPtr node_;
  CameraMountConfig config_;


  std::shared_ptr<tf2_ros::StaticTransformBroadcaster> static_broadcaster_;
  std::shared_ptr<tf2_ros::TransformBroadcaster> dynamic_broadcaster_;


  std::shared_ptr<tf2_ros::Buffer> tf_buffer_;
  std::shared_ptr<tf2_ros::TransformListener> tf_listener_;


  geometry_msgs::msg::TransformStamped create_transform(
    double x, double y, double z,
    double roll, double pitch, double yaw
  ) const;


  geometry_msgs::msg::TransformStamped create_optical_transform() const;
};

namespace tf_utils
{

std::array<double, 4> euler_to_quaternion(double roll, double pitch, double yaw);

std::array<double, 3> quaternion_to_euler(const std::array<double, 4>& q);

geometry_msgs::msg::TransformStamped make_transform(
  const std::string& parent_frame,
  const std::string& child_frame,
  double x, double y, double z,
  double qx, double qy, double qz, double qw
);

geometry_msgs::msg::TransformStamped make_transform_rpy(
  const std::string& parent_frame,
  const std::string& child_frame,
  double x, double y, double z,
  double roll, double pitch, double yaw
);

}

}

#endif