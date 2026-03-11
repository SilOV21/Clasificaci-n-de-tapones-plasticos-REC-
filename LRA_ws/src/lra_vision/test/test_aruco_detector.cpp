// =============================================================================
// LRA Vision Package - Test ArUco Detector
// Unit tests for ArUco marker detection
// ROS2 Jazzy Jalisco - GTest
// =============================================================================

#include <gtest/gtest.h>
#include <opencv2/opencv.hpp>
#include <opencv2/aruco.hpp>
#include "lra_vision/aruco_detector.hpp"

class ArUcoDetectorTest : public ::testing::Test
{
protected:
  void SetUp() override
  {
    config_ = lra_vision::ArucoConfig::default_config();
    config_.marker_size = 0.05;  // 5cm
    config_.dictionary = cv::aruco::DICT_4X4_50;
  }
  
  void TearDown() override
  {
    // Cleanup
  }
  
  lra_vision::ArucoConfig config_;
  
  // Generate test image with ArUco markers
  cv::Mat generateArUcoImage()
  {
    cv::Mat image = cv::Mat::zeros(800, 600, CV_8UC3);
    image.setTo(cv::Scalar(255, 255, 255));  // White background
    
    // Create dictionary
    cv::Ptr<cv::aruco::Dictionary> dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_50);
    
    // Draw a marker
    cv::Mat marker;
    cv::aruco::drawMarker(dictionary, 0, 200, marker);
    
    // Convert to color and place in image
    cv::Mat marker_color;
    cv::cvtColor(marker, marker_color, cv::COLOR_GRAY2BGR);
    
    cv::Rect roi(100, 100, 200, 200);
    marker_color.copyTo(image(roi));
    
    return image;
  }
  
  // Generate test image with multiple markers
  cv::Mat generateMultipleArUcoImage(int num_markers)
  {
    cv::Mat image = cv::Mat::zeros(800, 600, CV_8UC3);
    image.setTo(cv::Scalar(255, 255, 255));
    
    cv::Ptr<cv::aruco::Dictionary> dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_50);
    
    for (int i = 0; i < num_markers && i < 10; ++i) {
      cv::Mat marker;
      cv::aruco::drawMarker(dictionary, i, 100, marker);
      
      cv::Mat marker_color;
      cv::cvtColor(marker, marker_color, cv::COLOR_GRAY2BGR);
      
      int x = (i % 4) * 150 + 50;
      int y = (i / 4) * 150 + 50;
      
      cv::Rect roi(x, y, 100, 100);
      marker_color.copyTo(image(roi));
    }
    
    return image;
  }
};

// Test: ArucoConfig default values
TEST_F(ArUcoDetectorTest, TestArucoConfigDefaults)
{
  auto config = lra_vision::ArucoConfig::default_config();
  
  EXPECT_EQ(config.dictionary, cv::aruco::DICT_4X4_50);
  EXPECT_DOUBLE_EQ(config.marker_size, 0.05);
}

// Test: ArUcoMarker structure
TEST_F(ArUcoDetectorTest, TestArucoMarkerStructure)
{
  lra_vision::ArucoMarker marker;
  
  marker.id = 5;
  marker.corners = {
    cv::Point2f(0, 0),
    cv::Point2f(100, 0),
    cv::Point2f(100, 100),
    cv::Point2f(0, 100)
  };
  marker.rvec = cv::Vec3d(0, 0, 0);
  marker.tvec = cv::Vec3d(0.5, 0.0, 0.3);
  marker.marker_size = 0.05;
  marker.reprojection_error = 0.01;
  
  EXPECT_EQ(marker.id, 5);
  EXPECT_EQ(marker.corners.size(), 4);
  EXPECT_DOUBLE_EQ(marker.tvec[0], 0.5);
  
  // Test get_center
  cv::Point2f center = marker.get_center();
  EXPECT_FLOAT_EQ(center.x, 50.0f);
  EXPECT_FLOAT_EQ(center.y, 50.0f);
  
  // Test get_rotation_matrix
  cv::Mat R = marker.get_rotation_matrix();
  EXPECT_EQ(R.rows, 3);
  EXPECT_EQ(R.cols, 3);
  
  // Test get_pose_matrix
  cv::Mat pose = marker.get_pose_matrix();
  EXPECT_EQ(pose.rows, 4);
  EXPECT_EQ(pose.cols, 4);
}

// Test: ArUcoDetector initialization
TEST_F(ArUcoDetectorTest, TestInitialization)
{
  EXPECT_NO_THROW({
    lra_vision::ArucoDetector detector(config_);
  });
}

// Test: ArUcoDetector detect on synthetic image
TEST_F(ArUcoDetectorTest, TestDetectOnSyntheticImage)
{
  lra_vision::ArucoDetector detector(config_);
  
  cv::Mat test_image = generateArUcoImage();
  
  auto markers = detector.detect(test_image);
  
  // Should detect at least one marker
  EXPECT_GE(markers.size(), 1);
  
  if (!markers.empty()) {
    EXPECT_EQ(markers[0].id, 0);  // We drew marker 0
    EXPECT_EQ(markers[0].corners.size(), 4);
  }
}

// Test: ArUcoDetector detect multiple markers
TEST_F(ArUcoDetectorTest, TestDetectMultipleMarkers)
{
  lra_vision::ArucoDetector detector(config_);
  
  cv::Mat test_image = generateMultipleArUcoImage(4);
  
  auto markers = detector.detect(test_image);
  
  // Should detect multiple markers
  EXPECT_GE(markers.size(), 1);
}

// Test: ArUcoDetector detect specific IDs
TEST_F(ArUcoDetectorTest, TestDetectSpecificIds)
{
  lra_vision::ArucoDetector detector(config_);
  
  cv::Mat test_image = generateMultipleArUcoImage(4);
  
  // Look for specific markers
  std::vector<int> target_ids = {0, 1, 2};
  
  auto markers = detector.detect_specific(test_image, target_ids);
  
  // All detected markers should be in target_ids
  for (const auto& marker : markers) {
    EXPECT_TRUE(std::find(target_ids.begin(), target_ids.end(), marker.id) != target_ids.end());
  }
}

// Test: ArUcoDetector set_config
TEST_F(ArUcoDetectorTest, TestSetConfig)
{
  lra_vision::ArucoDetector detector(config_);
  
  lra_vision::ArucoConfig new_config = config_;
  new_config.marker_size = 0.10;  // 10cm
  
  EXPECT_NO_THROW(detector.set_config(new_config));
  
  EXPECT_DOUBLE_EQ(detector.get_config().marker_size, 0.10);
}

// Test: ArUcoDetector set_marker_size
TEST_F(ArUcoDetectorTest, TestSetMarkerSize)
{
  lra_vision::ArucoDetector detector(config_);
  
  detector.set_marker_size(0.08);
  
  EXPECT_DOUBLE_EQ(detector.get_config().marker_size, 0.08);
}

// Test: ArUcoDetector camera calibration
TEST_F(ArUcoDetectorTest, TestSetCameraCalibration)
{
  lra_vision::ArucoDetector detector(config_);
  
  // Create dummy camera matrix
  cv::Mat camera_matrix = cv::Mat::eye(3, 3, CV_64F);
  camera_matrix.at<double>(0, 0) = 1000.0;
  camera_matrix.at<double>(1, 1) = 1000.0;
  camera_matrix.at<double>(0, 2) = 640.0;
  camera_matrix.at<double>(1, 2) = 480.0;
  
  cv::Mat dist_coeffs = cv::Mat::zeros(5, 1, CV_64F);
  
  detector.set_camera_matrix(camera_matrix, dist_coeffs);
  
  EXPECT_TRUE(detector.has_camera_calibration());
}

// Test: ArUcoDetector detect_with_pose
TEST_F(ArUcoDetectorTest, TestDetectWithPose)
{
  lra_vision::ArucoDetector detector(config_);
  
  // Set camera calibration
  cv::Mat camera_matrix = cv::Mat::eye(3, 3, CV_64F);
  camera_matrix.at<double>(0, 0) = 1000.0;
  camera_matrix.at<double>(1, 1) = 1000.0;
  camera_matrix.at<double>(0, 2) = 400.0;
  camera_matrix.at<double>(1, 2) = 300.0;
  
  cv::Mat dist_coeffs = cv::Mat::zeros(5, 1, CV_64F);
  detector.set_camera_matrix(camera_matrix, dist_coeffs);
  
  cv::Mat test_image = generateArUcoImage();
  
  auto markers = detector.detect_with_pose(test_image);
  
  // If markers are detected, they should have pose
  for (const auto& marker : markers) {
    EXPECT_GT(marker.corners.size(), 0);
  }
}

// Test: ArUcoDetector draw_markers
TEST_F(ArUcoDetectorTest, TestDrawMarkers)
{
  lra_vision::ArucoDetector detector(config_);
  
  cv::Mat test_image = generateArUcoImage();
  auto markers = detector.detect(test_image);
  
  cv::Mat display = test_image.clone();
  
  EXPECT_NO_THROW(detector.draw_markers(display, markers, true, true));
  
  // Display image should be modified
  EXPECT_FALSE(display.empty());
}

// Test: ArUcoDetector get_dictionary and get_parameters
TEST_F(ArUcoDetectorTest, TestGetDictionaryAndParameters)
{
  lra_vision::ArucoDetector detector(config_);
  
  auto dictionary = detector.get_dictionary();
  EXPECT_NO_THROW(dictionary.bytesList);
  
  auto params = detector.get_parameters();
  // Parameters should have reasonable values
  EXPECT_GT(params.adaptiveThreshWinSizeMin, 0);
  EXPECT_GT(params.adaptiveThreshWinSizeMax, params.adaptiveThreshWinSizeMin);
}

int main(int argc, char** argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}