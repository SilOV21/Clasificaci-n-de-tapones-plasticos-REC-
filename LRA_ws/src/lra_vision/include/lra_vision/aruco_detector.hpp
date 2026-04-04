

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

struct ArucoMarker
{
  int id;
  std::vector<cv::Point2f> corners;
  cv::Vec3d rvec;
  cv::Vec3d tvec;
  double marker_size;
  double reprojection_error;


  cv::Point2f get_center() const;


  cv::Mat get_rotation_matrix() const;


  cv::Mat get_pose_matrix() const;
};

struct ArucoConfig
{

  cv::aruco::PREDEFINED_DICTIONARY_NAME dictionary = cv::aruco::DICT_4X4_50;


  double marker_size = 0.05;


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


  static ArucoConfig default_config();


  static ArucoConfig from_yaml(const std::string& filepath);
};

class ArucoDetector
{
public:

  explicit ArucoDetector(const ArucoConfig& config = ArucoConfig::default_config());






  std::vector<ArucoMarker> detect(const cv::Mat& image);


  std::vector<ArucoMarker> detect_with_pose(const cv::Mat& image);


  std::vector<ArucoMarker> detect_specific(
    const cv::Mat& image,
    const std::vector<int>& marker_ids
  );


  void refine_corners(const cv::Mat& image, std::vector<ArucoMarker>& markers);






  void set_camera_matrix(const cv::Mat& camera_matrix, const cv::Mat& dist_coeffs);


  bool load_camera_calibration(const std::string& filepath);


  bool has_camera_calibration() const { return has_calibration_; }






  void draw_markers(
    cv::Mat& image,
    const std::vector<ArucoMarker>& markers,
    bool draw_axes = true,
    bool draw_ids = true
  ) const;


  void draw_axis_marker(cv::Mat& image, const ArucoMarker& marker, float axis_length = 0.03f) const;






  const ArucoConfig& get_config() const { return config_; }


  void set_config(const ArucoConfig& config);


  cv::Ptr<cv::aruco::Dictionary> get_dictionary() const { return dictionary_; }


  cv::Ptr<cv::aruco::DetectorParameters> get_parameters() const { return parameters_; }


  void set_marker_size(double size) { config_.marker_size = size; }

private:
  ArucoConfig config_;
  cv::Ptr<cv::aruco::Dictionary> dictionary_;
  cv::Ptr<cv::aruco::DetectorParameters> parameters_;

  bool has_calibration_ = false;
  cv::Mat camera_matrix_;
  cv::Mat dist_coeffs_;


  void initialize_detector();


  std::vector<ArucoMarker> convert_results(
    const std::vector<int>& ids,
    const std::vector<std::vector<cv::Point2f>>& corners,
    const std::vector<cv::Vec3d>& rvecs = {},
    const std::vector<cv::Vec3d>& tvecs = {}
  ) const;
};

}

#endif