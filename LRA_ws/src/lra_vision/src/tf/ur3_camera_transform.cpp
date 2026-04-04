

#define _USE_MATH_DEFINES
#include "lra_vision/ur3_camera_transform.hpp"
#include <cmath>
#include <opencv2/opencv.hpp>

namespace lra_vision
{

namespace ur3_camera
{

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

CameraMountConfig get_default_mount_config()
{
  CameraMountConfig config;
  config.translation_x = 0.0;
  config.translation_y = 0.0;
  config.translation_z = 0.05;
  config.roll = 0.0;
  config.pitch = M_PI;
  config.yaw = 0.0;
  config.parent_frame = "tool0";
  config.camera_frame = "camera_link";
  config.optical_frame = "camera_optical_frame";
  return config;
}

CameraMountConfig get_side_mount_config(double angle_degrees, double distance)
{
  CameraMountConfig config;
  double angle_rad = angle_degrees * M_PI / 180.0;

  config.translation_x = distance * std::sin(angle_rad);
  config.translation_y = 0.0;
  config.translation_z = distance * std::cos(angle_rad);
  config.roll = 0.0;
  config.pitch = M_PI - angle_rad;
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

CameraMountConfig get_in_hand_mount_config()
{
  CameraMountConfig config;
  config.translation_x = 0.05;
  config.translation_y = 0.0;
  config.translation_z = 0.02;
  config.roll = 0.0;
  config.pitch = 0.0;
  config.yaw = 0.0;
  config.parent_frame = "tool0";
  config.camera_frame = "camera_link";
  config.optical_frame = "camera_optical_frame";
  return config;
}

std::array<double, 3> camera_to_tcp(
  const std::array<double, 3>& camera_point,
  double tcp_offset)
{





  std::array<double, 3> tcp_point;
  tcp_point[0] = -camera_point[1];
  tcp_point[1] = -camera_point[0];
  tcp_point[2] = 0.05 - camera_point[2] + tcp_offset;

  return tcp_point;
}

std::array<double, 3> camera_to_tcp(const std::array<double, 3>& camera_point)
{
  return camera_to_tcp(camera_point, 0.0);
}

std::array<double, 6> compute_grip_pose(
  const std::array<double, 3>& object_position,
  double approach_height)
{
  std::array<double, 6> pose;


  auto tcp_pos = camera_to_tcp(object_position);

  pose[0] = tcp_pos[0];
  pose[1] = tcp_pos[1];
  pose[2] = tcp_pos[2] + approach_height;
  pose[3] = M_PI;
  pose[4] = 0.0;
  pose[5] = 0.0;

  return pose;
}

std::array<double, 6> compute_grip_pose(const std::array<double, 3>& object_position)
{
  return compute_grip_pose(object_position, 0.05);
}

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

}

}