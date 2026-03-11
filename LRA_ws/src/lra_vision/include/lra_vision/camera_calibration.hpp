// =============================================================================
// LRA Vision Package - Camera Calibration
// OpenCV-based camera calibration with chessboard pattern
// ROS2 Jazzy Jalisco - C++17
// =============================================================================
/**
 * @file camera_calibration.hpp
 * @brief Camera calibration using OpenCV chessboard pattern detection.
 * 
 * This module provides comprehensive camera calibration functionality including:
 * - Automatic chessboard corner detection
 * - Intrinsic and extrinsic parameter computation
 * - Distortion coefficient estimation
 * - Calibration quality evaluation (reprojection error)
 * - Save/load calibration parameters in YAML format
 * 
 * @author Dr. Asil
 * @date March 2026
 * @copyright MIT License
 */

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

/**
 * @struct CalibrationConfig
 * @brief Configuration parameters for camera calibration.
 */
struct CalibrationConfig
{
  // Chessboard pattern parameters
  int board_width = 9;              ///< Number of inner corners horizontally
  int board_height = 6;             ///< Number of inner corners vertically
  double square_size = 0.025;       ///< Size of a chessboard square in meters
  
  // Calibration process parameters
  int min_images = 30;              ///< Minimum images required for calibration
  int max_images = 100;             ///< Maximum images to collect
  int max_iterations = 30;          ///< Maximum optimization iterations
  double reprojection_error_threshold = 0.5; ///< Max acceptable RMS error
  
  // Image capture parameters
  bool auto_capture = true;         ///< Automatically capture images
  double capture_interval = 1.0;    ///< Time between auto captures (seconds)
  double capture_timeout = 5.0;     ///< Timeout for manual capture (seconds)
  
  // Output parameters
  std::string output_path = "~/.ros/camera_calibration/";
  std::string camera_name = "logitech_streamcam";
  std::string save_format = "yaml"; ///< "yaml" or "xml"
  
  /**
   * @brief Load configuration from YAML file.
   * @param filepath Path to the YAML configuration file.
   * @return CalibrationConfig loaded from file.
   */
  static CalibrationConfig from_yaml(const std::string& filepath);
  
  /**
   * @brief Save configuration to YAML file.
   * @param filepath Path to save the configuration.
   */
  void to_yaml(const std::string& filepath) const;
};

/**
 * @struct CalibrationData
 * @brief Data collected during calibration process.
 */
struct CalibrationData
{
  std::vector<std::vector<cv::Point2f>> image_points;  ///< Detected corners in images
  std::vector<std::vector<cv::Point3f>> object_points; ///< 3D points in world coordinates
  cv::Size image_size;                                  ///< Image resolution
  std::vector<std::string> image_paths;                 ///< Paths to saved calibration images
  
  /**
   * @brief Clear all collected data.
   */
  void clear();
  
  /**
   * @brief Get number of collected image sets.
   * @return Number of valid image pairs collected.
   */
  size_t size() const { return image_points.size(); }
  
  /**
   * @brief Check if enough data has been collected.
   * @param min_required Minimum required images.
   * @return True if enough data is available.
   */
  bool has_sufficient_data(size_t min_required) const { return size() >= min_required; }
};

/**
 * @struct CalibrationResult
 * @brief Results from camera calibration.
 */
struct CalibrationResult
{
  bool success = false;            ///< True if calibration succeeded
  double rms_error = 0.0;          ///< RMS reprojection error
  
  // Intrinsic parameters
  cv::Mat camera_matrix;           ///< 3x3 camera matrix (fx, fy, cx, cy)
  cv::Mat dist_coeffs;             ///< Distortion coefficients (k1, k2, p1, p2, k3)
  
  // Image dimensions
  int image_width = 0;
  int image_height = 0;
  
  // Calibration quality metrics
  double mean_reprojection_error = 0.0;
  double max_reprojection_error = 0.0;
  double min_reprojection_error = 0.0;
  
  // Timestamp
  std::string calibration_timestamp;
  
  /**
   * @brief Get camera matrix as 3x3 array.
   * @return 2D array of camera matrix values.
   */
  std::array<std::array<double, 3>, 3> get_camera_matrix_array() const;
  
  /**
   * @brief Get distortion coefficients as array.
   * @return Array of distortion coefficients.
   */
  std::vector<double> get_distortion_array() const;
  
  /**
   * @brief Save calibration results to YAML file (ROS camera_info format).
   * @param filepath Path to save the calibration.
   */
  void save_to_yaml(const std::string& filepath) const;
  
  /**
   * @brief Load calibration results from YAML file.
   * @param filepath Path to load the calibration from.
   * @return CalibrationResult loaded from file.
   */
  static CalibrationResult from_yaml(const std::string& filepath);
  
  /**
   * @brief Convert to ROS sensor_msgs/CameraInfo format string.
   * @return YAML string in camera_info format.
   */
  std::string to_camera_info_yaml() const;
};

/**
 * @class CameraCalibrator
 * @brief Performs camera calibration using chessboard pattern detection.
 * 
 * This class provides complete camera calibration functionality:
 * - Detects chessboard corners in images
 * - Collects calibration data from multiple views
 * - Computes intrinsic and distortion parameters
 * - Evaluates calibration quality
 * 
 * @example
 * @code
 * CalibrationConfig config;
 * config.board_width = 9;
 * config.board_height = 6;
 * 
 * CameraCalibrator calibrator(config);
 * 
 * // Add images for calibration
 * for (const auto& img : images) {
 *   calibrator.add_image(img);
 * }
 * 
 * // Perform calibration
 * auto result = calibrator.calibrate();
 * if (result.success) {
 *   std::cout << "RMS Error: " << result.rms_error << std::endl;
 *   result.save_to_yaml("camera_calibration.yaml");
 * }
 * @endcode
 */
class CameraCalibrator
{
public:
  /**
   * @brief Construct calibrator with configuration.
   * @param config Calibration configuration parameters.
   */
  explicit CameraCalibrator(const CalibrationConfig& config = CalibrationConfig());
  
  /**
   * @brief Add an image for calibration.
   * @param image Image containing the chessboard pattern.
   * @param visualize If true, displays detected corners.
   * @return True if chessboard pattern was detected.
   */
  bool add_image(const cv::Mat& image, bool visualize = false);
  
  /**
   * @brief Add an image from file path.
   * @param filepath Path to the image file.
   * @param visualize If true, displays detected corners.
   * @return True if chessboard pattern was detected.
   */
  bool add_image_from_file(const std::string& filepath, bool visualize = false);
  
  /**
   * @brief Perform calibration with collected images.
   * @return CalibrationResult containing calibration parameters.
   */
  CalibrationResult calibrate();
  
  /**
   * @brief Undistort an image using computed calibration.
   * @param image Input distorted image.
   * @return Undistorted image.
   */
  cv::Mat undistort_image(const cv::Mat& image) const;
  
  /**
   * @brief Get undistortion maps for remapping.
   * @param map1 First undistortion map (x coordinates).
   * @param map2 Second undistortion map (y coordinates).
   */
  void get_undistortion_maps(cv::Mat& map1, cv::Mat& map2) const;
  
  /**
   * @brief Clear all collected calibration data.
   */
  void clear();
  
  /**
   * @brief Get number of collected image sets.
   * @return Number of valid image sets.
   */
  size_t get_image_count() const { return calibration_data_.size(); }
  
  /**
   * @brief Check if enough images have been collected.
   * @return True if minimum required images collected.
   */
  bool has_sufficient_data() const;
  
  /**
   * @brief Get current configuration.
   * @return Calibration configuration.
   */
  const CalibrationConfig& get_config() const { return config_; }
  
  /**
   * @brief Get collected calibration data.
   * @return Reference to calibration data.
   */
  const CalibrationData& get_data() const { return calibration_data_; }
  
  /**
   * @brief Check if calibration has been performed.
   * @return True if calibration result is available.
   */
  bool is_calibrated() const { return calibration_result_.success; }
  
  /**
   * @brief Get last calibration result.
   * @return Optional calibration result if available.
   */
  std::optional<CalibrationResult> get_result() const;
  
  /**
   * @brief Load calibration from file.
   * @param filepath Path to calibration file.
   * @return True if loaded successfully.
   */
  bool load_calibration(const std::string& filepath);
  
  /**
   * @brief Save current calibration to file.
   * @param filepath Path to save calibration.
   * @return True if saved successfully.
   */
  bool save_calibration(const std::string& filepath) const;

private:
  CalibrationConfig config_;
  CalibrationData calibration_data_;
  CalibrationResult calibration_result_;
  
  // Pre-computed undistortion maps
  mutable cv::Mat undistort_map1_;
  mutable cv::Mat undistort_map2_;
  mutable bool undistort_maps_computed_ = false;
  
  /**
   * @brief Generate 3D object points for chessboard pattern.
   * @return Vector of 3D points for the chessboard.
   */
  std::vector<cv::Point3f> generate_object_points() const;
  
  /**
   * @brief Detect chessboard corners in an image.
   * @param image Input image.
   * @param corners Output detected corners.
   * @param visualize If true, display detected corners.
   * @return True if corners were detected.
   */
  bool detect_chessboard(
    const cv::Mat& image,
    std::vector<cv::Point2f>& corners,
    bool visualize = false
  ) const;
  
  /**
   * @brief Compute undistortion maps from calibration result.
   */
  void compute_undistortion_maps();
};

/**
 * @brief Utility functions for calibration visualization.
 */
namespace calibration_utils
{
/**
 * @brief Draw detected corners on image.
 * @param image Image to draw on.
 * @param corners Detected corner positions.
 * @param found Whether pattern was found.
 * @return Image with corners drawn.
 */
cv::Mat draw_corners(
  const cv::Mat& image,
  const std::vector<cv::Point2f>& corners,
  bool found
);

/**
 * @brief Visualize calibration quality with reprojection.
 * @param image Original image.
 * @param result Calibration result.
 * @param object_points Object points used for calibration.
 * @param image_points Image points used for calibration.
 * @return Visualization image.
 */
cv::Mat visualize_reprojection(
  const cv::Mat& image,
  const CalibrationResult& result,
  const std::vector<cv::Point3f>& object_points,
  const std::vector<cv::Point2f>& image_points
);

/**
 * @brief Print calibration result summary.
 * @param result Calibration result to print.
 */
void print_calibration_summary(const CalibrationResult& result);

}  // namespace calibration_utils

}  // namespace lra_vision

#endif  // LRA_VISION__CAMERA_CALIBRATION_HPP_