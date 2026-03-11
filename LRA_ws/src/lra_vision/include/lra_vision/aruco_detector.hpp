// =============================================================================
// LRA Vision Package - ArUco Detector
// ArUco marker detection for hand-eye calibration
// ROS2 Jazzy Jalisco - C++17
// =============================================================================
/**
 * @file aruco_detector.hpp
 * @brief ArUco marker detection for camera-robot hand-eye calibration.
 * 
 * This module provides ArUco marker detection functionality for:
 * - Camera pose estimation
 * - Hand-eye calibration support
 * - Marker-based coordinate frame registration
 * 
 * @author Dr. Asil
 * @date March 2026
 * @copyright MIT License
 */

#ifndef LRA_VISION__ARUCO_DETECTOR_HPP_
#define LRA_VISION__ARUCO_DETECTOR_HPP_

#include <string>
#include <vector>
#include <optional>
#include <memory>

#include <opencv2/opencv.hpp>
#include <opencv2/aruco.hpp>
#include <opencv2/calib3d.hpp>

namespace lra_vision
{

/**
 * @struct ArucoMarker
 * @brief Represents a detected ArUco marker.
 */
struct ArucoMarker
{
  int id;                          ///< Marker ID
  std::vector<cv::Point2f> corners; ///< Four corner points (top-left, top-right, bottom-right, bottom-left)
  cv::Vec3d rvec;                  ///< Rotation vector
  cv::Vec3d tvec;                  ///< Translation vector
  double marker_size;              ///< Marker size in meters
  double reprojection_error;       ///< Reprojection error
  
  /**
   * @brief Get the center point of the marker.
   * @return Center point in image coordinates.
   */
  cv::Point2f get_center() const;
  
  /**
   * @brief Get the rotation as a 3x3 matrix.
   * @return Rotation matrix.
   */
  cv::Mat get_rotation_matrix() const;
  
  /**
   * @brief Get the pose as a 4x4 transformation matrix.
   * @return 4x4 transformation matrix.
   */
  cv::Mat get_pose_matrix() const;
};

/**
 * @struct ArucoConfig
 * @brief Configuration for ArUco detection.
 */
struct ArucoConfig
{
  // Dictionary
  cv::aruco::PREDEFINED_DICTIONARY_NAME dictionary = cv::aruco::DICT_4X4_50;
  
  // Marker parameters
  double marker_size = 0.05;       ///< Marker size in meters
  
  // Detection parameters
  int adaptive_thresh_win_size_min = 3;
  int adaptive_thresh_win_size_max = 23;
  int adaptive_thresh_win_size_step = 10;
  double adaptive_thresh_const = 7.0;
  double min_marker_perimeter_rate = 0.03;
  double max_marker_perimeter_rate = 4.0;
  double polygonal_approx_accuracy_rate = 0.03;
  double min_corner_distance_rate = 0.05;
  int min_distance_to_border = 3;
  double min_marker_distance_rate = 0.05;
  int corner_refinement_method = cv::aruco::CORNER_REFINE_SUBPIX;
  int corner_refinement_win_size = 5;
  int corner_refinement_max_iterations = 30;
  double corner_refinement_min_accuracy = 0.1;
  
  /**
   * @brief Create default configuration.
   * @return Default ArUco configuration.
   */
  static ArucoConfig default_config();
  
  /**
   * @brief Load configuration from YAML file.
   * @param filepath Path to YAML file.
   * @return Loaded configuration.
   */
  static ArucoConfig from_yaml(const std::string& filepath);
};

/**
 * @class ArucoDetector
 * @brief Detects ArUco markers for hand-eye calibration.
 * 
 * Provides ArUco marker detection with pose estimation:
 * - Supports multiple ArUco dictionaries
 * - Corner refinement for sub-pixel accuracy
 * - Pose estimation using camera calibration
 * - Visualization utilities
 * 
 * @example
 * @code
 * ArucoConfig config = ArucoConfig::default_config();
 * ArucoDetector detector(config);
 * 
 * // Set camera calibration
 * detector.set_camera_matrix(camera_matrix, dist_coeffs);
 * 
 * // Detect markers
 * cv::Mat image = cv::imread("markers.jpg");
 * auto markers = detector.detect(image);
 * 
 * for (const auto& marker : markers) {
 *   std::cout << "Marker " << marker.id << " at " << marker.tvec << std::endl;
 * }
 * @endcode
 */
class ArucoDetector
{
public:
  /**
   * @brief Construct detector with configuration.
   * @param config Detection configuration.
   */
  explicit ArucoDetector(const ArucoConfig& config = ArucoConfig::default_config());
  
  // ========================================================================
  // Detection Functions
  // ========================================================================
  
  /**
   * @brief Detect ArUco markers in an image.
   * @param image Input image.
   * @return Vector of detected markers.
   */
  std::vector<ArucoMarker> detect(const cv::Mat& image);
  
  /**
   * @brief Detect markers and estimate pose.
   * @param image Input image.
   * @return Vector of detected markers with pose.
   */
  std::vector<ArucoMarker> detect_with_pose(const cv::Mat& image);
  
  /**
   * @brief Detect markers of specific IDs.
   * @param image Input image.
   * @param marker_ids Vector of marker IDs to detect.
   * @return Vector of detected markers.
   */
  std::vector<ArucoMarker> detect_specific(
    const cv::Mat& image,
    const std::vector<int>& marker_ids
  );
  
  /**
   * @brief Refine detected marker corners.
   * @param image Input image.
   * @param markers Markers to refine (modified in place).
   */
  void refine_corners(const cv::Mat& image, std::vector<ArucoMarker>& markers);
  
  // ========================================================================
  // Camera Calibration
  // ========================================================================
  
  /**
   * @brief Set camera calibration parameters.
   * @param camera_matrix 3x3 camera matrix.
   * @param dist_coeffs Distortion coefficients.
   */
  void set_camera_matrix(const cv::Mat& camera_matrix, const cv::Mat& dist_coeffs);
  
  /**
   * @brief Load camera calibration from file.
   * @param filepath Path to calibration file.
   * @return True if loaded successfully.
   */
  bool load_camera_calibration(const std::string& filepath);
  
  /**
   * @brief Check if camera calibration is set.
   * @return True if calibration is available.
   */
  bool has_camera_calibration() const { return has_calibration_; }
  
  // ========================================================================
  // Visualization
  // ========================================================================
  
  /**
   * @brief Draw detected markers on image.
   * @param image Input image (modified in place).
   * @param markers Detected markers.
   * @param draw_axes If true, draw 3D coordinate axes.
   * @param draw_ids If true, draw marker IDs.
   */
  void draw_markers(
    cv::Mat& image,
    const std::vector<ArucoMarker>& markers,
    bool draw_axes = true,
    bool draw_ids = true
  ) const;
  
  /**
   * @brief Draw coordinate axes on marker.
   * @param image Input image (modified in place).
   * @param marker Marker to draw axes for.
   * @param axis_length Length of axes in meters.
   */
  void draw_axis_marker(cv::Mat& image, const ArucoMarker& marker, float axis_length = 0.03f) const;
  
  // ========================================================================
  // Configuration
  // ========================================================================
  
  /**
   * @brief Get current configuration.
   * @return Current detection configuration.
   */
  const ArucoConfig& get_config() const { return config_; }
  
  /**
   * @brief Set detection configuration.
   * @param config New configuration.
   */
  void set_config(const ArucoConfig& config);
  
  /**
   * @brief Get dictionary pointer.
   * @return ArUco dictionary pointer.
   */
  cv::Ptr<cv::aruco::Dictionary> get_dictionary() const { return dictionary_; }
  
  /**
   * @brief Get detection parameters pointer.
   * @return Detection parameters pointer.
   */
  cv::Ptr<cv::aruco::DetectorParameters> get_parameters() const { return parameters_; }
  
  /**
   * @brief Set marker size.
   * @param size Marker size in meters.
   */
  void set_marker_size(double size) { config_.marker_size = size; }

private:
  ArucoConfig config_;
  cv::Ptr<cv::aruco::Dictionary> dictionary_;
  cv::Ptr<cv::aruco::DetectorParameters> parameters_;

  bool has_calibration_ = false;
  cv::Mat camera_matrix_;
  cv::Mat dist_coeffs_;
  
  /**
   * @brief Initialize detector with configuration.
   */
  void initialize_detector();
  
  /**
   * @brief Convert raw detection results to ArucoMarker structures.
   * @param ids Detected marker IDs.
   * @param corners Detected marker corners.
   * @param rvecs Rotation vectors (if pose estimated).
   * @param tvecs Translation vectors (if pose estimated).
   * @return Vector of ArucoMarker structures.
   */
  std::vector<ArucoMarker> convert_results(
    const std::vector<int>& ids,
    const std::vector<std::vector<cv::Point2f>>& corners,
    const std::vector<cv::Vec3d>& rvecs = {},
    const std::vector<cv::Vec3d>& tvecs = {}
  ) const;
};

}  // namespace lra_vision

#endif  // LRA_VISION__ARUCO_DETECTOR_HPP_