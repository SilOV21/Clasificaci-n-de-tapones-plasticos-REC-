

#define _USE_MATH_DEFINES
#include "lra_vision/camera_tf_broadcaster.hpp"

#include <cmath>
#include <fstream>
#include <yaml-cpp/yaml.h>

namespace lra_vision
{

CameraMountConfig CameraMountConfig::overhead(double height)
{
  CameraMountConfig config;
  config.translation_x = 0.0;
  config.translation_y = 0.0;
  config.translation_z = height;
  config.roll = 0.0;
  config.pitch = M_PI;
  config.yaw = 0.0;
  return config;
}

CameraMountConfig CameraMountConfig::angled(double angle_degrees, double height)
{
  CameraMountConfig config;
  config.translation_x = 0.0;
  config.translation_y = 0.0;
  config.translation_z = height;
  config.roll = 0.0;
  config.pitch = angle_degrees * M_PI / 180.0;
  config.yaw = 0.0;
  return config;
}

CameraMountConfig CameraMountConfig::from_yaml(const std::string& filepath)
{
  CameraMountConfig config;

  try {
    YAML::Node yaml = YAML::LoadFile(filepath);

    if (yaml["camera_mount"]) {
      auto mount = yaml["camera_mount"];
      if (mount["translation_x"]) config.translation_x = mount["translation_x"].as<double>();
      if (mount["translation_y"]) config.translation_y = mount["translation_y"].as<double>();
      if (mount["translation_z"]) config.translation_z = mount["translation_z"].as<double>();
      if (mount["roll"]) config.roll = mount["roll"].as<double>();
      if (mount["pitch"]) config.pitch = mount["pitch"].as<double>();
      if (mount["yaw"]) config.yaw = mount["yaw"].as<double>();
      if (mount["parent_frame"]) config.parent_frame = mount["parent_frame"].as<std::string>();
      if (mount["camera_frame"]) config.camera_frame = mount["camera_frame"].as<std::string>();
      if (mount["optical_frame"]) config.optical_frame = mount["optical_frame"].as<std::string>();
    }
  } catch (const std::exception& e) {
    std::cerr << "Warning: Could not load camera mount config from " << filepath
              << ": " << e.what() << std::endl;
  }

  return config;
}

CameraTfBroadcaster::CameraTfBroadcaster(
  rclcpp::Node::SharedPtr node,
  const CameraMountConfig& config)
: node_(node)
, config_(config)
{

  static_broadcaster_ = std::make_shared<tf2_ros::StaticTransformBroadcaster>(node_);
  dynamic_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(node_);


  tf_buffer_ = std::make_shared<tf2_ros::Buffer>(node_->get_clock());
  tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);
}

void CameraTfBroadcaster::initialize()
{
  publish_static_transforms();
}

void CameraTfBroadcaster::publish_static_transforms()
{

  auto camera_transform = create_transform(
    config_.translation_x,
    config_.translation_y,
    config_.translation_z,
    config_.roll,
    config_.pitch,
    config_.yaw
  );

  camera_transform.header.frame_id = config_.parent_frame;
  camera_transform.child_frame_id = config_.camera_frame;
  camera_transform.header.stamp = node_->get_clock()->now();


  auto optical_transform = create_optical_transform();
  optical_transform.header.frame_id = config_.camera_frame;
  optical_transform.child_frame_id = config_.optical_frame;
  optical_transform.header.stamp = node_->get_clock()->now();


  static_broadcaster_->sendTransform({camera_transform, optical_transform});
}

void CameraTfBroadcaster::update()
{




  auto camera_transform = create_transform(
    config_.translation_x,
    config_.translation_y,
    config_.translation_z,
    config_.roll,
    config_.pitch,
    config_.yaw
  );

  camera_transform.header.frame_id = config_.parent_frame;
  camera_transform.child_frame_id = config_.camera_frame;
  camera_transform.header.stamp = node_->get_clock()->now();

  dynamic_broadcaster_->sendTransform(camera_transform);
}

geometry_msgs::msg::TransformStamped CameraTfBroadcaster::get_camera_transform() const
{
  return create_transform(
    config_.translation_x,
    config_.translation_y,
    config_.translation_z,
    config_.roll,
    config_.pitch,
    config_.yaw
  );
}

geometry_msgs::msg::Pose CameraTfBroadcaster::get_camera_pose_world() const
{
  geometry_msgs::msg::Pose pose;

  try {

    auto transform = tf_buffer_->lookupTransform(
      "world",
      config_.camera_frame,
      tf2::TimePointZero
    );

    pose.position.x = transform.transform.translation.x;
    pose.position.y = transform.transform.translation.y;
    pose.position.z = transform.transform.translation.z;
    pose.orientation = transform.transform.rotation;

  } catch (const tf2::TransformException& ex) {
    RCLCPP_WARN(node_->get_logger(), "Could not get camera pose in world frame: %s", ex.what());
  }

  return pose;
}

std::array<double, 3> CameraTfBroadcaster::transform_to_world(const std::array<double, 3>& point) const
{
  try {
    geometry_msgs::msg::PointStamped camera_point;
    camera_point.header.frame_id = config_.camera_frame;
    camera_point.point.x = point[0];
    camera_point.point.y = point[1];
    camera_point.point.z = point[2];

    auto world_point = tf_buffer_->transform(camera_point, "world");

    return {world_point.point.x, world_point.point.y, world_point.point.z};

  } catch (const tf2::TransformException& ex) {
    RCLCPP_WARN(node_->get_logger(), "Could not transform point to world: %s", ex.what());
    return point;
  }
}

std::array<double, 3> CameraTfBroadcaster::transform_to_camera(const std::array<double, 3>& point) const
{
  try {
    geometry_msgs::msg::PointStamped world_point;
    world_point.header.frame_id = "world";
    world_point.point.x = point[0];
    world_point.point.y = point[1];
    world_point.point.z = point[2];

    auto camera_point = tf_buffer_->transform(world_point, config_.camera_frame);

    return {camera_point.point.x, camera_point.point.y, camera_point.point.z};

  } catch (const tf2::TransformException& ex) {
    RCLCPP_WARN(node_->get_logger(), "Could not transform point to camera: %s", ex.what());
    return point;
  }
}

void CameraTfBroadcaster::update_config(const CameraMountConfig& config)
{
  config_ = config;
  publish_static_transforms();
}

void CameraTfBroadcaster::set_parent_frame(const std::string& frame_name)
{
  config_.parent_frame = frame_name;
  publish_static_transforms();
}

bool CameraTfBroadcaster::can_transform(
  const std::string& target_frame,
  const std::string& source_frame) const
{
  return tf_buffer_->canTransform(target_frame, source_frame, tf2::TimePointZero);
}

geometry_msgs::msg::TransformStamped CameraTfBroadcaster::create_transform(
  double x, double y, double z,
  double roll, double pitch, double yaw) const
{
  geometry_msgs::msg::TransformStamped transform;

  transform.transform.translation.x = x;
  transform.transform.translation.y = y;
  transform.transform.translation.z = z;

  auto quat = tf_utils::euler_to_quaternion(roll, pitch, yaw);
  transform.transform.rotation.x = quat[0];
  transform.transform.rotation.y = quat[1];
  transform.transform.rotation.z = quat[2];
  transform.transform.rotation.w = quat[3];

  return transform;
}

geometry_msgs::msg::TransformStamped CameraTfBroadcaster::create_optical_transform() const
{


  geometry_msgs::msg::TransformStamped transform;

  transform.transform.translation.x = 0;
  transform.transform.translation.y = 0;
  transform.transform.translation.z = 0;


  auto quat = tf_utils::euler_to_quaternion(-M_PI / 2, 0, -M_PI / 2);
  transform.transform.rotation.x = quat[0];
  transform.transform.rotation.y = quat[1];
  transform.transform.rotation.z = quat[2];
  transform.transform.rotation.w = quat[3];

  return transform;
}

namespace tf_utils
{

std::array<double, 4> euler_to_quaternion(double roll, double pitch, double yaw)
{
  double cy = std::cos(yaw * 0.5);
  double sy = std::sin(yaw * 0.5);
  double cp = std::cos(pitch * 0.5);
  double sp = std::sin(pitch * 0.5);
  double cr = std::cos(roll * 0.5);
  double sr = std::sin(roll * 0.5);

  std::array<double, 4> q;
  q[0] = sr * cp * cy - cr * sp * sy;
  q[1] = cr * sp * cy + sr * cp * sy;
  q[2] = cr * cp * sy - sr * sp * cy;
  q[3] = cr * cp * cy + sr * sp * sy;

  return q;
}

std::array<double, 3> quaternion_to_euler(const std::array<double, 4>& q)
{
  std::array<double, 3> euler;


  double sinr_cosp = 2.0 * (q[3] * q[0] + q[1] * q[2]);
  double cosr_cosp = 1.0 - 2.0 * (q[0] * q[0] + q[1] * q[1]);
  euler[0] = std::atan2(sinr_cosp, cosr_cosp);


  double sinp = 2.0 * (q[3] * q[1] - q[2] * q[0]);
  if (std::abs(sinp) >= 1.0) {
    euler[1] = std::copysign(M_PI / 2, sinp);
  } else {
    euler[1] = std::asin(sinp);
  }


  double siny_cosp = 2.0 * (q[3] * q[2] + q[0] * q[1]);
  double cosy_cosp = 1.0 - 2.0 * (q[1] * q[1] + q[2] * q[2]);
  euler[2] = std::atan2(siny_cosp, cosy_cosp);

  return euler;
}

geometry_msgs::msg::TransformStamped make_transform(
  const std::string& parent_frame,
  const std::string& child_frame,
  double x, double y, double z,
  double qx, double qy, double qz, double qw)
{
  geometry_msgs::msg::TransformStamped transform;

  transform.header.frame_id = parent_frame;
  transform.child_frame_id = child_frame;

  transform.transform.translation.x = x;
  transform.transform.translation.y = y;
  transform.transform.translation.z = z;

  transform.transform.rotation.x = qx;
  transform.transform.rotation.y = qy;
  transform.transform.rotation.z = qz;
  transform.transform.rotation.w = qw;

  return transform;
}

geometry_msgs::msg::TransformStamped make_transform_rpy(
  const std::string& parent_frame,
  const std::string& child_frame,
  double x, double y, double z,
  double roll, double pitch, double yaw)
{
  auto q = euler_to_quaternion(roll, pitch, yaw);

  return make_transform(parent_frame, child_frame, x, y, z, q[0], q[1], q[2], q[3]);
}

}

}