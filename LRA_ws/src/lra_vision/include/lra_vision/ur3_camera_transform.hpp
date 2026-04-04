

#ifndef LRA_VISION__UR3_CAMERA_TRANSFORM_HPP_
#define LRA_VISION__UR3_CAMERA_TRANSFORM_HPP_

#include <array>
#include <vector>
#include <string>
#include <opencv2/opencv.hpp>
#include "lra_vision/camera_tf_broadcaster.hpp"

namespace lra_vision
{

namespace ur3_camera
{

extern const std::vector<std::string> UR3_LINK_NAMES;

CameraMountConfig get_default_mount_config();

CameraMountConfig get_side_mount_config(double angle_degrees, double distance);

CameraMountConfig get_side_mount_config();

CameraMountConfig get_in_hand_mount_config();

std::array<double, 3> camera_to_tcp(
  const std::array<double, 3>& camera_point,
  double tcp_offset);

std::array<double, 3> camera_to_tcp(const std::array<double, 3>& camera_point);

std::array<double, 6> compute_grip_pose(
  const std::array<double, 3>& object_position,
  double approach_height);

std::array<double, 6> compute_grip_pose(const std::array<double, 3>& object_position);

struct StreamCamParameters
{

  double focal_length_x = 1000.0;
  double focal_length_y = 1000.0;
  double center_x = 960.0;
  double center_y = 540.0;


  double k1 = 0.0;
  double k2 = 0.0;
  double p1 = 0.0;
  double p2 = 0.0;
  double k3 = 0.0;


  std::vector<std::pair<int, int>> resolutions = {
    {1920, 1080},
    {1280, 720},
    {640, 480},
    {320, 240}
  };


  std::vector<int> frame_rates = {30, 60};


  cv::Mat get_camera_matrix(int width, int height) const;


  cv::Mat get_distortion_coefficients() const;
};

}

}

#endif