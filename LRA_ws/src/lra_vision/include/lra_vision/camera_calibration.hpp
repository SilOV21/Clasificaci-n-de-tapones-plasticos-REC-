

#ifndef LRA_VISION__CAMERA_CALIBRATION_HPP_
#define LRA_VISION__CAMERA_CALIBRATION_HPP_

#include <string>
#include <vector>
#include <memory>
#include <optional>
#include <fstream>

#include <opencv2/opencv.hpp>
#include <opencv2/calib3d.hpp>
#include <opencv2/imgproc.hpp>
#include <yaml-cpp/yaml.h>

namespace lra_vision
{

struct CalibrationConfig
{

  int board_width = 9;
  int board_height = 6;
  double square_size = 0.025;

  int min_images = 30;
  int max_images = 100;
  int max_iterations = 30;
  double reprojection_error_threshold = 0.5;

  bool auto_capture = true;
  double capture_interval = 1.0;
  double capture_timeout = 5.0;

  std::string output_path = "~/.ros/camera_calibration/";
  std::string camera_name = "logitech_streamcam";
  std::string save_format = "yaml";

  static CalibrationConfig from_yaml(const std::string& filepath);

  void to_yaml(const std::string& filepath) const;
};

struct CalibrationData
{
  std::vector<std::vector<cv::Point2f>> image_points;
  std::vector<std::vector<cv::Point3f>> object_points;
  cv::Size image_size;
  std::vector<std::string> image_paths;

  void clear();

  size_t size() const { return image_points.size(); }

  bool has_sufficient_data(size_t min_required) const { return size() >= min_required; }
};

struct CalibrationResult
{
  bool success = false;
  double rms_error = 0.0;

  cv::Mat camera_matrix;
  cv::Mat dist_coeffs;

  int image_width = 0;
  int image_height = 0;

  double mean_reprojection_error = 0.0;
  double max_reprojection_error = 0.0;
  double min_reprojection_error = 0.0;

  std::string calibration_timestamp;

  std::array<std::array<double, 3>, 3> get_camera_matrix_array() const;

  std::vector<double> get_distortion_array() const;

  void save_to_yaml(const std::string& filepath) const;

  static CalibrationResult from_yaml(const std::string& filepath);

  std::string to_camera_info_yaml() const;
};

class CameraCalibrator
{
public:

  explicit CameraCalibrator(const CalibrationConfig& config = CalibrationConfig());

  bool detect_chessboard(
    const cv::Mat& image,
    std::vector<cv::Point2f>& corners,
    bool visualize = false
  ) const;

  bool add_image(const cv::Mat& image, bool visualize = false);

  CalibrationResult calibrate();

  void clear();

  size_t get_image_count() const { return calibration_data_.size(); }

  bool has_sufficient_data() const;

  const CalibrationData& get_data() const { return calibration_data_; }

  bool is_calibrated() const { return calibration_result_.success; }

  const CalibrationConfig& get_config() const { return config_; }

  bool load_calibration(const std::string& filepath);

  bool save_calibration(const std::string& filepath) const;

private:
  CalibrationConfig config_;
  CalibrationData calibration_data_;
  CalibrationResult calibration_result_;

  std::vector<cv::Point3f> generate_object_points() const;

  void compute_undistortion_maps();
};

namespace calibration_utils
{

cv::Mat draw_corners(
  const cv::Mat& image,
  const std::vector<cv::Point2f>& corners,
  bool found
);

void print_calibration_summary(const CalibrationResult& result);

}

}

#endif