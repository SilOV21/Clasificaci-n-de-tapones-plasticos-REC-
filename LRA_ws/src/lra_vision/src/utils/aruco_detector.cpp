#include "lra_vision/aruco_detector.hpp"

#include <fstream>
#include <opencv2/calib3d.hpp>

namespace lra_vision
{

// =============================================================================
// ArucoMarker Implementation
// =============================================================================

cv::Point2f ArucoMarker::get_center() const
{
  if (corners.empty()) {
    return cv::Point2f(0, 0);
  }
  
  cv::Point2f center(0, 0);
  for (const auto& corner : corners) {
    center += corner;
  }
  center /= static_cast<float>(corners.size());
  
  return center;
}

cv::Mat ArucoMarker::get_rotation_matrix() const
{
  cv::Mat R;
  cv::Rodrigues(rvec, R);
  return R;
}

cv::Mat ArucoMarker::get_pose_matrix() const
{
  cv::Mat pose = cv::Mat::eye(4, 4, CV_64F);
  
  cv::Mat R = get_rotation_matrix();
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) {
      pose.at<double>(i, j) = R.at<double>(i, j);
    }
    pose.at<double>(i, 3) = tvec[i];
  }
  
  return pose;
}

// =============================================================================
// ArucoConfig Implementation
// =============================================================================

ArucoConfig ArucoConfig::default_config()
{
  ArucoConfig config;
  
  // Use DICT_4X4_50 as default - good balance of size and uniqueness
  config.dictionary = cv::aruco::DICT_4X4_50;
  config.marker_size = 0.05; // 5cm markers
  
  // Detection parameters optimized for StreamCam
  config.corner_refinement_method = cv::aruco::CORNER_REFINE_SUBPIX;
  config.corner_refinement_win_size = 5;
  config.corner_refinement_max_iterations = 30;
  config.corner_refinement_min_accuracy = 0.1;
  
  return config;
}

ArucoConfig ArucoConfig::from_yaml(const std::string& filepath)
{
  ArucoConfig config = default_config();
  
  // TODO: Implement YAML loading
  (void)filepath;
  
  return config;
}

// =============================================================================
// ArucoDetector Implementation
// =============================================================================

ArucoDetector::ArucoDetector(const ArucoConfig& config)
: config_(config)
{
  initialize_detector();
}

void ArucoDetector::initialize_detector()
{
  dictionary_ = cv::aruco::getPredefinedDictionary(config_.dictionary);

  parameters_ = cv::aruco::DetectorParameters::create();
  parameters_->adaptiveThreshWinSizeMin = config_.adaptive_thresh_win_size_min;
  parameters_->adaptiveThreshWinSizeMax = config_.adaptive_thresh_win_size_max;
  parameters_->adaptiveThreshWinSizeStep = config_.adaptive_thresh_win_size_step;
  parameters_->adaptiveThreshConstant = config_.adaptive_thresh_const;
  parameters_->minMarkerPerimeterRate = config_.min_marker_perimeter_rate;
  parameters_->maxMarkerPerimeterRate = config_.max_marker_perimeter_rate;
  parameters_->polygonalApproxAccuracyRate = config_.polygonal_approx_accuracy_rate;
  parameters_->minCornerDistanceRate = config_.min_corner_distance_rate;
  parameters_->minDistanceToBorder = config_.min_distance_to_border;
  parameters_->minMarkerDistanceRate = config_.min_marker_distance_rate;
  parameters_->cornerRefinementMethod = config_.corner_refinement_method;
  parameters_->cornerRefinementWinSize = config_.corner_refinement_win_size;
  parameters_->cornerRefinementMaxIterations = config_.corner_refinement_max_iterations;
  parameters_->cornerRefinementMinAccuracy = config_.corner_refinement_min_accuracy;
}

void ArucoDetector::set_config(const ArucoConfig& config)
{
  config_ = config;
  initialize_detector();
}

void ArucoDetector::set_camera_matrix(const cv::Mat& camera_matrix, const cv::Mat& dist_coeffs)
{
  camera_matrix_ = camera_matrix.clone();
  dist_coeffs_ = dist_coeffs.clone();
  has_calibration_ = true;
}

bool ArucoDetector::load_camera_calibration(const std::string& filepath)
{
  try {
    cv::FileStorage fs(filepath, cv::FileStorage::READ);
    if (!fs.isOpened()) {
      return false;
    }
    
    fs["camera_matrix"] >> camera_matrix_;
    fs["distortion_coefficients"] >> dist_coeffs_;
    
    has_calibration_ = !camera_matrix_.empty() && !dist_coeffs_.empty();
    return has_calibration_;
    
  } catch (const cv::Exception& e) {
    std::cerr << "Error loading calibration: " << e.what() << std::endl;
    return false;
  }
}

std::vector<ArucoMarker> ArucoDetector::detect(const cv::Mat& image)
{
  std::vector<ArucoMarker> markers;

  std::vector<int> ids;
  std::vector<std::vector<cv::Point2f>> corners;
  std::vector<std::vector<cv::Point2f>> rejected;

  cv::aruco::detectMarkers(image, dictionary_, corners, ids, parameters_, rejected);

  if (ids.empty()) {
    return markers;
  }

  markers = convert_results(ids, corners);

  return markers;
}

std::vector<ArucoMarker> ArucoDetector::detect_with_pose(const cv::Mat& image)
{
  std::vector<ArucoMarker> markers;

  if (!has_calibration_) {
    // Fall back to detection without pose
    return detect(image);
  }

  std::vector<int> ids;
  std::vector<std::vector<cv::Point2f>> corners;
  std::vector<std::vector<cv::Point2f>> rejected;

  cv::aruco::detectMarkers(image, dictionary_, corners, ids, parameters_, rejected);

  if (ids.empty()) {
    return markers;
  }

  // Estimate poses using solvePnP instead of the deprecated estimatePoseSingleMarkers
  std::vector<cv::Vec3d> rvecs, tvecs;
  rvecs.reserve(ids.size());
  tvecs.reserve(ids.size());

  for (size_t i = 0; i < ids.size(); i++) {
    // Create object points for the marker (square)
    std::vector<cv::Point3f> object_points;
    float half_size = static_cast<float>(config_.marker_size) / 2.0f;
    object_points = {
      cv::Point3f(-half_size, -half_size, 0),
      cv::Point3f(half_size, -half_size, 0),
      cv::Point3f(half_size, half_size, 0),
      cv::Point3f(-half_size, half_size, 0)
    };

    // Solve PnP for this marker
    cv::Vec3d rvec, tvec;
    bool success = cv::solvePnP(object_points, corners[i], camera_matrix_, dist_coeffs_, rvec, tvec);

    if (success) {
      rvecs.push_back(rvec);
      tvecs.push_back(tvec);
    } else {
      // If PnP fails, use zero vectors
      rvecs.push_back(cv::Vec3d(0, 0, 0));
      tvecs.push_back(cv::Vec3d(0, 0, 0));
    }
  }

  markers = convert_results(ids, corners, rvecs, tvecs);

  // Calculate reprojection errors
  for (size_t i = 0; i < markers.size(); ++i) {
    if (i < rvecs.size() && i < tvecs.size()) {
      std::vector<cv::Point2f> reprojected;
      std::vector<cv::Point3f> object_points;

      // Generate object points for this marker
      float half_size = static_cast<float>(config_.marker_size) / 2.0f;
      object_points = {
        cv::Point3f(-half_size, -half_size, 0),
        cv::Point3f(half_size, -half_size, 0),
        cv::Point3f(half_size, half_size, 0),
        cv::Point3f(-half_size, half_size, 0)
      };

      cv::projectPoints(object_points, rvecs[i], tvecs[i],
                         camera_matrix_, dist_coeffs_, reprojected);

      double error = 0;
      for (int j = 0; j < 4; ++j) {
        error += cv::norm(corners[i][j] - reprojected[j]);
      }
      markers[i].reprojection_error = error / 4.0;
    }
  }

  return markers;
}

std::vector<ArucoMarker> ArucoDetector::detect_specific(
  const cv::Mat& image,
  const std::vector<int>& marker_ids)
{
  std::vector<ArucoMarker> all_markers = detect_with_pose(image);
  
  std::vector<ArucoMarker> filtered_markers;
  for (const auto& marker : all_markers) {
    if (std::find(marker_ids.begin(), marker_ids.end(), marker.id) != marker_ids.end()) {
      filtered_markers.push_back(marker);
    }
  }
  
  return filtered_markers;
}

void ArucoDetector::refine_corners(const cv::Mat& image, std::vector<ArucoMarker>& markers)
{
  if (markers.empty() || image.empty()) {
    return;
  }
  
  cv::Mat gray;
  if (image.channels() == 3) {
    cv::cvtColor(image, gray, cv::COLOR_BGR2GRAY);
  } else {
    gray = image.clone();
  }
  
  for (auto& marker : markers) {
    cv::cornerSubPix(
      gray,
      marker.corners,
      cv::Size(config_.corner_refinement_win_size, config_.corner_refinement_win_size),
      cv::Size(-1, -1),
      cv::TermCriteria(
        cv::TermCriteria::EPS + cv::TermCriteria::MAX_ITER,
        config_.corner_refinement_max_iterations,
        config_.corner_refinement_min_accuracy
      )
    );
  }
}

void ArucoDetector::draw_markers(
  cv::Mat& image,
  const std::vector<ArucoMarker>& markers,
  bool show_axes,
  bool draw_ids) const
{
  if (markers.empty()) {
    return;
  }

  // Prepare data for drawing
  std::vector<std::vector<cv::Point2f>> all_corners;
  std::vector<int> all_ids;

  for (const auto& marker : markers) {
    all_corners.push_back(marker.corners);
    all_ids.push_back(marker.id);
  }

  // Draw detected markers
  cv::aruco::drawDetectedMarkers(image, all_corners, all_ids);

  // Draw axes if pose is available and requested
  if (show_axes && has_calibration_) {
    for (const auto& marker : markers) {
      // Check if pose is valid (not all zeros)
      bool has_pose = (marker.rvec[0] != 0 || marker.rvec[1] != 0 || marker.rvec[2] != 0) ||
                      (marker.tvec[0] != 0 || marker.tvec[1] != 0 || marker.tvec[2] != 0);
      if (has_pose) {
        draw_axis_marker(image, marker, 0.03f);
      }
    }
  }
}

void ArucoDetector::draw_axis_marker(cv::Mat& image, const ArucoMarker& marker, float axis_length) const
{
  if (!has_calibration_) {
    return;
  }
  
  // Draw 3D axis manually since cv::aruco::drawAxis may not be available in all OpenCV versions
  std::vector<cv::Point3f> axis_points = {
    cv::Point3f(0, 0, 0),
    cv::Point3f(axis_length, 0, 0),  // X - red
    cv::Point3f(0, axis_length, 0),  // Y - green
    cv::Point3f(0, 0, axis_length)   // Z - blue
  };
  
  std::vector<cv::Point2f> image_points;
  cv::projectPoints(axis_points, marker.rvec, marker.tvec, 
                     camera_matrix_, dist_coeffs_, image_points);
  
  // Draw the axes
  cv::line(image, image_points[0], image_points[1], cv::Scalar(0, 0, 255), 2);  // X - red
  cv::line(image, image_points[0], image_points[2], cv::Scalar(0, 255, 0), 2);  // Y - green
  cv::line(image, image_points[0], image_points[3], cv::Scalar(255, 0, 0), 2);  // Z - blue
}

std::vector<ArucoMarker> ArucoDetector::convert_results(
  const std::vector<int>& ids,
  const std::vector<std::vector<cv::Point2f>>& corners,
  const std::vector<cv::Vec3d>& rvecs,
  const std::vector<cv::Vec3d>& tvecs) const
{
  std::vector<ArucoMarker> markers;
  
  for (size_t i = 0; i < ids.size(); ++i) {
    ArucoMarker marker;
    marker.id = ids[i];
    marker.corners = corners[i];
    marker.marker_size = config_.marker_size;
    
    if (i < rvecs.size()) {
      marker.rvec = rvecs[i];
    } else {
      marker.rvec = cv::Vec3d(0, 0, 0);
    }
    
    if (i < tvecs.size()) {
      marker.tvec = tvecs[i];
    } else {
      marker.tvec = cv::Vec3d(0, 0, 0);
    }
    
    marker.reprojection_error = 0.0;
    
    markers.push_back(marker);
  }
  
  return markers;
}

}  // namespace lra_vision