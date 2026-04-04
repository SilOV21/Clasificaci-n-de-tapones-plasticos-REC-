

#include "lra_vision/camera_calibration.hpp"

#include <chrono>
#include <iomanip>
#include <sstream>
#include <cmath>
#include <algorithm>

namespace lra_vision
{

CalibrationConfig CalibrationConfig::from_yaml(const std::string& filepath)
{
  CalibrationConfig config;

  try {
    YAML::Node yaml = YAML::LoadFile(filepath);

    if (yaml["calibration"]) {
      auto calib = yaml["calibration"];
      if (calib["board_width"]) config.board_width = calib["board_width"].as<int>();
      if (calib["board_height"]) config.board_height = calib["board_height"].as<int>();
      if (calib["square_size"]) config.square_size = calib["square_size"].as<double>();
      if (calib["min_images"]) config.min_images = calib["min_images"].as<int>();
      if (calib["max_images"]) config.max_images = calib["max_images"].as<int>();
      if (calib["max_iterations"]) config.max_iterations = calib["max_iterations"].as<int>();
      if (calib["reprojection_error_threshold"]) {
        config.reprojection_error_threshold = calib["reprojection_error_threshold"].as<double>();
      }
      if (calib["auto_capture"]) config.auto_capture = calib["auto_capture"].as<bool>();
      if (calib["capture_interval"]) config.capture_interval = calib["capture_interval"].as<double>();
      if (calib["capture_timeout"]) config.capture_timeout = calib["capture_timeout"].as<double>();
      if (calib["save_path"]) config.output_path = calib["save_path"].as<std::string>();
      if (calib["save_format"]) config.save_format = calib["save_format"].as<std::string>();
    }

    if (yaml["camera_name"]) {
      config.camera_name = yaml["camera_name"].as<std::string>();
    }
  } catch (const std::exception& e) {
    std::cerr << "Warning: Could not load calibration config from " << filepath
              << ": " << e.what() << std::endl;
  }

  return config;
}

void CalibrationConfig::to_yaml(const std::string& filepath) const
{
  YAML::Emitter out;
  out << YAML::BeginMap;

  out << YAML::Key << "calibration" << YAML::BeginMap;
  out << YAML::Key << "board_width" << YAML::Value << board_width;
  out << YAML::Key << "board_height" << YAML::Value << board_height;
  out << YAML::Key << "square_size" << YAML::Value << square_size;
  out << YAML::Key << "min_images" << YAML::Value << min_images;
  out << YAML::Key << "max_images" << YAML::Value << max_images;
  out << YAML::Key << "max_iterations" << YAML::Value << max_iterations;
  out << YAML::Key << "reprojection_error_threshold" << YAML::Value << reprojection_error_threshold;
  out << YAML::Key << "auto_capture" << YAML::Value << auto_capture;
  out << YAML::Key << "capture_interval" << YAML::Value << capture_interval;
  out << YAML::Key << "capture_timeout" << YAML::Value << capture_timeout;
  out << YAML::Key << "save_path" << YAML::Value << output_path;
  out << YAML::Key << "save_format" << YAML::Value << save_format;
  out << YAML::EndMap;

  out << YAML::Key << "camera_name" << YAML::Value << camera_name;

  out << YAML::EndMap;

  std::ofstream fout(filepath);
  fout << out.c_str();
}

void CalibrationData::clear()
{
  image_points.clear();
  object_points.clear();
  image_paths.clear();
  image_size = cv::Size();
}

std::array<std::array<double, 3>, 3> CalibrationResult::get_camera_matrix_array() const
{
  std::array<std::array<double, 3>, 3> arr = {{{0}}};

  if (!camera_matrix.empty()) {
    for (int i = 0; i < 3; ++i) {
      for (int j = 0; j < 3; ++j) {
        arr[i][j] = camera_matrix.at<double>(i, j);
      }
    }
  }

  return arr;
}

std::vector<double> CalibrationResult::get_distortion_array() const
{
  std::vector<double> coeffs;

  if (!dist_coeffs.empty()) {
    for (int i = 0; i < dist_coeffs.rows; ++i) {
      coeffs.push_back(dist_coeffs.at<double>(i, 0));
    }
  }

  return coeffs;
}

void CalibrationResult::save_to_yaml(const std::string& filepath) const
{
  YAML::Emitter out;
  out << YAML::BeginMap;

  out << YAML::Key << "camera_name" << YAML::Value << "logitech_streamcam";
  out << YAML::Key << "image_width" << YAML::Value << image_width;
  out << YAML::Key << "image_height" << YAML::Value << image_height;

  out << YAML::Key << "camera_matrix" << YAML::BeginMap;
  out << YAML::Key << "rows" << YAML::Value << 3;
  out << YAML::Key << "cols" << YAML::Value << 3;
  out << YAML::Key << "data" << YAML::Flow << YAML::BeginSeq;
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) {
      out << camera_matrix.at<double>(i, j);
    }
  }
  out << YAML::EndSeq << YAML::EndMap;

  out << YAML::Key << "distortion_coefficients" << YAML::BeginMap;
  out << YAML::Key << "rows" << YAML::Value << dist_coeffs.rows;
  out << YAML::Key << "cols" << YAML::Value << 1;
  out << YAML::Key << "data" << YAML::Flow << YAML::BeginSeq;
  for (int i = 0; i < dist_coeffs.rows; ++i) {
    out << dist_coeffs.at<double>(i, 0);
  }
  out << YAML::EndSeq << YAML::EndMap;

  out << YAML::Key << "rectification_matrix" << YAML::BeginMap;
  out << YAML::Key << "rows" << YAML::Value << 3;
  out << YAML::Key << "cols" << YAML::Value << 3;
  out << YAML::Key << "data" << YAML::Flow << YAML::BeginSeq;
  for (int i = 0; i < 9; ++i) {
    out << (i % 4 == 0 ? 1.0 : 0.0);
  }
  out << YAML::EndSeq << YAML::EndMap;

  out << YAML::Key << "projection_matrix" << YAML::BeginMap;
  out << YAML::Key << "rows" << YAML::Value << 3;
  out << YAML::Key << "cols" << YAML::Value << 4;
  out << YAML::Key << "data" << YAML::Flow << YAML::BeginSeq;

  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) {
      out << camera_matrix.at<double>(i, j);
    }
    out << 0.0;
  }
  out << YAML::EndSeq << YAML::EndMap;

  out << YAML::Key << "calibration_time" << YAML::Value << calibration_timestamp;
  out << YAML::Key << "rms_error" << YAML::Value << rms_error;

  out << YAML::EndMap;

  std::ofstream fout(filepath);
  fout << out.c_str();
}

CalibrationResult CalibrationResult::from_yaml(const std::string& filepath)
{
  CalibrationResult result;

  try {
    YAML::Node yaml = YAML::LoadFile(filepath);

    result.image_width = yaml["image_width"].as<int>();
    result.image_height = yaml["image_height"].as<int>();

    auto cam_matrix = yaml["camera_matrix"]["data"];
    result.camera_matrix = cv::Mat(3, 3, CV_64F);
    for (int i = 0; i < 9; ++i) {
      result.camera_matrix.at<double>(i / 3, i % 3) = cam_matrix[i].as<double>();
    }

    auto dist = yaml["distortion_coefficients"]["data"];
    int dist_rows = yaml["distortion_coefficients"]["rows"].as<int>();
    result.dist_coeffs = cv::Mat(dist_rows, 1, CV_64F);
    for (int i = 0; i < dist_rows; ++i) {
      result.dist_coeffs.at<double>(i, 0) = dist[i].as<double>();
    }

    if (yaml["rms_error"]) {
      result.rms_error = yaml["rms_error"].as<double>();
    }

    if (yaml["calibration_time"]) {
      result.calibration_timestamp = yaml["calibration_time"].as<std::string>();
    }

    result.success = true;

  } catch (const std::exception& e) {
    std::cerr << "Error loading calibration from " << filepath << ": " << e.what() << std::endl;
    result.success = false;
  }

  return result;
}

std::string CalibrationResult::to_camera_info_yaml() const
{
  YAML::Emitter out;
  out << YAML::BeginMap;

  out << YAML::Key << "camera_name" << YAML::Value << "logitech_streamcam";
  out << YAML::Key << "image_width" << YAML::Value << image_width;
  out << YAML::Key << "image_height" << YAML::Value << image_height;

  out << YAML::Key << "camera_matrix" << YAML::BeginMap;
  out << YAML::Key << "rows" << YAML::Value << 3;
  out << YAML::Key << "cols" << YAML::Value << 3;
  out << YAML::Key << "data" << YAML::Flow << YAML::BeginSeq;
  for (int i = 0; i < 9; ++i) {
    out << camera_matrix.at<double>(i / 3, i % 3);
  }
  out << YAML::EndSeq << YAML::EndMap;

  out << YAML::Key << "distortion_model" << YAML::Value << "plumb_bob";
  out << YAML::Key << "distortion_coefficients" << YAML::BeginMap;
  out << YAML::Key << "rows" << YAML::Value << 5;
  out << YAML::Key << "cols" << YAML::Value << 1;
  out << YAML::Key << "data" << YAML::Flow << YAML::BeginSeq;

  for (int i = 0; i < 5; ++i) {
    if (i < dist_coeffs.rows) {
      out << dist_coeffs.at<double>(i, 0);
    } else {
      out << 0.0;
    }
  }
  out << YAML::EndSeq << YAML::EndMap;

  out << YAML::Key << "rectification_matrix" << YAML::BeginMap;
  out << YAML::Key << "rows" << YAML::Value << 3;
  out << YAML::Key << "cols" << YAML::Value << 3;
  out << YAML::Key << "data" << YAML::Flow << YAML::BeginSeq;
  for (int i = 0; i < 9; ++i) {
    out << (i % 4 == 0 ? 1.0 : 0.0);
  }
  out << YAML::EndSeq << YAML::EndMap;

  out << YAML::Key << "projection_matrix" << YAML::BeginMap;
  out << YAML::Key << "rows" << YAML::Value << 3;
  out << YAML::Key << "cols" << YAML::Value << 4;
  out << YAML::Key << "data" << YAML::Flow << YAML::BeginSeq;
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) {
      out << camera_matrix.at<double>(i, j);
    }
    out << 0.0;
  }
  out << YAML::EndSeq << YAML::EndMap;

  out << YAML::EndMap;

  return std::string(out.c_str());
}

CameraCalibrator::CameraCalibrator(const CalibrationConfig& config)
: config_(config)
{
}

std::vector<cv::Point3f> CameraCalibrator::generate_object_points() const
{
  std::vector<cv::Point3f> object_points;

  for (int i = 0; i < config_.board_height; ++i) {
    for (int j = 0; j < config_.board_width; ++j) {
      object_points.emplace_back(
        static_cast<float>(j * config_.square_size),
        static_cast<float>(i * config_.square_size),
        0.0f
      );
    }
  }

  return object_points;
}

bool CameraCalibrator::detect_chessboard(
  const cv::Mat& image,
  std::vector<cv::Point2f>& corners,
  bool visualize) const
{
  cv::Mat gray;
  if (image.channels() == 3) {
    cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);
  } else {
    gray = image.clone();
  }

  cv::Size pattern_size(config_.board_width, config_.board_height);

  bool found = cv::findChessboardCorners(
    gray,
    pattern_size,
    corners,
    cv::CALIB_CB_ADAPTIVE_THRESH | cv::CALIB_CB_NORMALIZE_IMAGE | cv::CALIB_CB_FAST_CHECK
  );

  if (found) {

    cv::cornerSubPix(
      gray,
      corners,
      cv::Size(11, 11),
      cv::Size(-1, -1),
      cv::TermCriteria(cv::TermCriteria::EPS + cv::TermCriteria::MAX_ITER, 30, 0.001)
    );
  }

  if (visualize) {
    cv::Mat display;
    cv::cvtColor(gray, display, cv::COLOR_GRAY2BGR);
    cv::drawChessboardCorners(display, pattern_size, corners, found);
    cv::imshow("Chessboard Detection", display);
    cv::waitKey(1);
  }

  return found;
}

bool CameraCalibrator::add_image(const cv::Mat& image, bool visualize)
{
  std::vector<cv::Point2f> corners;

  if (!detect_chessboard(image, corners, visualize)) {
    return false;
  }


  if (calibration_data_.image_points.empty()) {
    calibration_data_.image_size = image.size();
  }


  calibration_data_.object_points.push_back(generate_object_points());
  calibration_data_.image_points.push_back(corners);

  return true;
}

CalibrationResult CameraCalibrator::calibrate()
{
  CalibrationResult result;

  if (calibration_data_.size() < static_cast<size_t>(config_.min_images)) {
    std::cerr << "Insufficient images for calibration: " << calibration_data_.size()
              << " < " << config_.min_images << std::endl;
    return result;
  }


  cv::Mat camera_matrix = cv::Mat::eye(3, 3, CV_64F);
  cv::Mat dist_coeffs = cv::Mat::zeros(5, 1, CV_64F);


  camera_matrix.at<double>(0, 0) = calibration_data_.image_size.width;
  camera_matrix.at<double>(1, 1) = calibration_data_.image_size.width;
  camera_matrix.at<double>(0, 2) = calibration_data_.image_size.width / 2.0;
  camera_matrix.at<double>(1, 2) = calibration_data_.image_size.height / 2.0;


  std::vector<cv::Mat> rvecs, tvecs;


  double rms = cv::calibrateCamera(
    calibration_data_.object_points,
    calibration_data_.image_points,
    calibration_data_.image_size,
    camera_matrix,
    dist_coeffs,
    rvecs,
    tvecs,
    cv::CALIB_FIX_PRINCIPAL_POINT | cv::CALIB_ZERO_TANGENT_DIST,
    cv::TermCriteria(cv::TermCriteria::EPS + cv::TermCriteria::MAX_ITER, config_.max_iterations, 1e-6)
  );


  result.success = true;
  result.rms_error = rms;
  result.camera_matrix = camera_matrix;
  result.dist_coeffs = dist_coeffs;
  result.image_width = calibration_data_.image_size.width;
  result.image_height = calibration_data_.image_size.height;


  std::vector<double> per_view_errors;
  double total_error = 0;
  int total_points = 0;

  for (size_t i = 0; i < calibration_data_.object_points.size(); ++i) {
    std::vector<cv::Point2f> reprojected;
    cv::projectPoints(
      calibration_data_.object_points[i],
      rvecs[i],
      tvecs[i],
      camera_matrix,
      dist_coeffs,
      reprojected
    );

    double error = cv::norm(calibration_data_.image_points[i], reprojected, cv::NORM_L2);
    per_view_errors.push_back(error / reprojected.size());
    total_error += error;
    total_points += reprojected.size();
  }

  result.mean_reprojection_error = total_error / total_points;
  result.max_reprojection_error = *std::max_element(per_view_errors.begin(), per_view_errors.end());
  result.min_reprojection_error = *std::min_element(per_view_errors.begin(), per_view_errors.end());


  auto now = std::chrono::system_clock::now();
  auto now_time = std::chrono::system_clock::to_time_t(now);
  std::stringstream ss;
  ss << std::put_time(std::localtime(&now_time), "%Y-%m-%d %H:%M:%S");
  result.calibration_timestamp = ss.str();


  calibration_result_ = result;

  return result;
}

void CameraCalibrator::clear()
{
  calibration_data_.clear();
  calibration_result_ = CalibrationResult();
}

bool CameraCalibrator::has_sufficient_data() const
{
  return calibration_data_.size() >= static_cast<size_t>(config_.min_images);
}

bool CameraCalibrator::load_calibration(const std::string& filepath)
{
  calibration_result_ = CalibrationResult::from_yaml(filepath);

  if (calibration_result_.success) {
    return true;
  }

  return false;
}

bool CameraCalibrator::save_calibration(const std::string& filepath) const
{
  if (!calibration_result_.success) {
    return false;
  }

  try {
    calibration_result_.save_to_yaml(filepath);
    return true;
  } catch (const std::exception& e) {
    std::cerr << "Error saving calibration: " << e.what() << std::endl;
    return false;
  }
}

namespace calibration_utils
{

cv::Mat draw_corners(
  const cv::Mat& image,
  const std::vector<cv::Point2f>& corners,
  bool found
)
{
  cv::Mat display = image.clone();

  if (found && !corners.empty()) {
    cv::Size pattern_size(9, 6);
    cv::drawChessboardCorners(display, pattern_size, corners, found);
  }

  return display;
}

void print_calibration_summary(const CalibrationResult& result)
{
  std::cout << "\n========== CALIBRATION RESULTS ==========\n";
  std::cout << "Success: " << (result.success ? "Yes" : "No") << "\n";
  std::cout << "RMS Error: " << result.rms_error << " pixels\n";
  std::cout << "Image Size: " << result.image_width << " x " << result.image_height << "\n\n";

  if (result.success) {
    std::cout << "Camera Matrix:\n";
    for (int i = 0; i < 3; ++i) {
      std::cout << "  ";
      for (int j = 0; j < 3; ++j) {
        std::cout << std::fixed << std::setprecision(4)
                  << result.camera_matrix.at<double>(i, j) << " ";
      }
      std::cout << "\n";
    }

    std::cout << "\nDistortion Coefficients: ";
    for (int i = 0; i < result.dist_coeffs.rows; ++i) {
      std::cout << result.dist_coeffs.at<double>(i, 0) << " ";
    }
    std::cout << "\n\n";

    std::cout << "Reprojection Errors:\n";
    std::cout << "  Mean: " << result.mean_reprojection_error << " pixels\n";
    std::cout << "  Min:  " << result.min_reprojection_error << " pixels\n";
    std::cout << "  Max:  " << result.max_reprojection_error << " pixels\n";
  }

  std::cout << "==========================================\n";
}

}

}