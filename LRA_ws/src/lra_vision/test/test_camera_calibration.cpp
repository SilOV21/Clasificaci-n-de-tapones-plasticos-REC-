// =============================================================================
// LRA Vision Package - Test Camera Calibration
// Unit tests for camera calibration functionality
// ROS2 Jazzy Jalisco - GTest
// =============================================================================

#include <gtest/gtest.h>
#include <opencv2/opencv.hpp>
#include "lra_vision/camera_calibration.hpp"

class CameraCalibrationTest : public ::testing::Test
{
protected:
  void SetUp() override
  {
    // Create default configuration
    config_.board_width = 9;
    config_.board_height = 6;
    config_.square_size = 0.025;
    config_.min_images = 3;  // Low for testing
    config_.max_images = 10;
  }
  
  void TearDown() override
  {
    // Cleanup
  }
  
  lra_vision::CalibrationConfig config_;
  
  // Generate synthetic chessboard image
  cv::Mat generateChessboardImage(int width, int height, int squares_x, int squares_y)
  {
    cv::Mat image(height, width, CV_8UC3, cv::Scalar(255, 255, 255));
    
    int square_w = width / (squares_x + 1);
    int square_h = height / (squares_y + 1);
    
    for (int i = 0; i <= squares_x; ++i) {
      for (int j = 0; j <= squares_y; ++j) {
        if ((i + j) % 2 == 0) {
          cv::rectangle(
            image,
            cv::Point(i * square_w, j * square_h),
            cv::Point((i + 1) * square_w, (j + 1) * square_h),
            cv::Scalar(0, 0, 0),
            cv::FILLED
          );
        }
      }
    }
    
    return image;
  }
};

// Test: CalibrationConfig default values
TEST_F(CameraCalibrationTest, TestCalibrationConfigDefaults)
{
  lra_vision::CalibrationConfig config;
  
  EXPECT_EQ(config.board_width, 9);
  EXPECT_EQ(config.board_height, 6);
  EXPECT_DOUBLE_EQ(config.square_size, 0.025);
  EXPECT_EQ(config.min_images, 30);
  EXPECT_TRUE(config.auto_capture);
}

// Test: CalibrationConfig from YAML
TEST_F(CameraCalibrationTest, TestCalibrationConfigFromYAML)
{
  // Create a temporary YAML file
  std::string yaml_content = R"(
calibration:
  board_width: 8
  board_height: 5
  square_size: 0.03
  min_images: 20
camera_name: test_camera
)";
  
  std::string temp_file = "/tmp/test_calibration_config.yaml";
  std::ofstream file(temp_file);
  file << yaml_content;
  file.close();
  
  auto config = lra_vision::CalibrationConfig::from_yaml(temp_file);
  
  EXPECT_EQ(config.board_width, 8);
  EXPECT_EQ(config.board_height, 5);
  EXPECT_DOUBLE_EQ(config.square_size, 0.03);
  EXPECT_EQ(config.min_images, 20);
  EXPECT_EQ(config.camera_name, "test_camera");
  
  // Cleanup
  std::remove(temp_file.c_str());
}

// Test: CalibrationData operations
TEST_F(CameraCalibrationTest, TestCalibrationData)
{
  lra_vision::CalibrationData data;
  
  EXPECT_EQ(data.size(), 0);
  EXPECT_FALSE(data.has_sufficient_data(10));
  
  // Add some data
  data.image_points.push_back({});
  data.object_points.push_back({});
  data.image_size = cv::Size(640, 480);
  
  EXPECT_EQ(data.size(), 1);
  EXPECT_TRUE(data.has_sufficient_data(1));
  EXPECT_FALSE(data.has_sufficient_data(2));
  
  // Clear data
  data.clear();
  EXPECT_EQ(data.size(), 0);
}

// Test: CalibrationResult structure
TEST_F(CameraCalibrationTest, TestCalibrationResult)
{
  lra_vision::CalibrationResult result;
  
  EXPECT_FALSE(result.success);
  EXPECT_DOUBLE_EQ(result.rms_error, 0.0);
  EXPECT_EQ(result.image_width, 0);
  EXPECT_EQ(result.image_height, 0);
  
  // Set some values
  result.success = true;
  result.rms_error = 0.5;
  result.image_width = 1920;
  result.image_height = 1080;
  result.camera_matrix = cv::Mat::eye(3, 3, CV_64F);
  result.dist_coeffs = cv::Mat::zeros(5, 1, CV_64F);
  
  EXPECT_TRUE(result.success);
  EXPECT_DOUBLE_EQ(result.rms_error, 0.5);
  
  // Test get_camera_matrix_array
  auto arr = result.get_camera_matrix_array();
  EXPECT_DOUBLE_EQ(arr[0][0], 1.0);
  EXPECT_DOUBLE_EQ(arr[1][1], 1.0);
  EXPECT_DOUBLE_EQ(arr[2][2], 1.0);
  
  // Test get_distortion_array
  auto dist = result.get_distortion_array();
  EXPECT_EQ(dist.size(), 5);
  for (int i = 0; i < 5; ++i) {
    EXPECT_DOUBLE_EQ(dist[i], 0.0);
  }
}

// Test: CameraCalibrator initialization
TEST_F(CameraCalibrationTest, TestCalibratorInitialization)
{
  lra_vision::CameraCalibrator calibrator(config_);
  
  EXPECT_FALSE(calibrator.is_calibrated());
  EXPECT_EQ(calibrator.get_image_count(), 0);
  EXPECT_FALSE(calibrator.has_sufficient_data());
}

// Test: CameraCalibrator add_image with synthetic data
TEST_F(CameraCalibrationTest, TestAddImage)
{
  lra_vision::CameraCalibrator calibrator(config_);
  
  // Generate a chessboard image
  cv::Mat chessboard = generateChessboardImage(800, 600, 9, 6);
  
  // Add the image
  bool found = calibrator.add_image(chessboard, false);
  
  // Chessboard should be detected
  EXPECT_TRUE(found);
  EXPECT_EQ(calibrator.get_image_count(), 1);
}

// Test: CameraCalibrator generate_object_points
TEST_F(CameraCalibrationTest, TestGenerateObjectPoints)
{
  lra_vision::CameraCalibrator calibrator(config_);
  
  // Add an image to trigger object point generation
  cv::Mat chessboard = generateChessboardImage(800, 600, 9, 6);
  calibrator.add_image(chessboard, false);
  
  // Object points should be generated for 9x6 = 54 corners
  // But we can't directly access them, so we check the image count
  EXPECT_EQ(calibrator.get_image_count(), 1);
}

// Test: CameraCalibrator clear
TEST_F(CameraCalibrationTest, TestClear)
{
  lra_vision::CameraCalibrator calibrator(config_);
  
  cv::Mat chessboard = generateChessboardImage(800, 600, 9, 6);
  calibrator.add_image(chessboard, false);
  
  EXPECT_EQ(calibrator.get_image_count(), 1);
  
  calibrator.clear();
  
  EXPECT_EQ(calibrator.get_image_count(), 0);
  EXPECT_FALSE(calibrator.is_calibrated());
}

// Test: CameraCalibrator with synthetic calibration
TEST_F(CameraCalibrationTest, TestSyntheticCalibration)
{
  lra_vision::CalibrationConfig test_config = config_;
  test_config.min_images = 3;
  
  lra_vision::CameraCalibrator calibrator(test_config);
  
  // Generate multiple chessboard images from different perspectives
  for (int i = 0; i < 5; ++i) {
    cv::Mat chessboard = generateChessboardImage(800, 600, 9, 6);
    
    // Add some perspective distortion
    cv::Mat rotated;
    cv::Point2f center(400, 300);
    cv::Mat rot = cv::getRotationMatrix2D(center, i * 5, 1.0);
    cv::warpAffine(chessboard, rotated, rot, chessboard.size());
    
    calibrator.add_image(rotated, false);
  }
  
  EXPECT_EQ(calibrator.get_image_count(), 5);
  EXPECT_TRUE(calibrator.has_sufficient_data());
  
  // Perform calibration
  auto result = calibrator.calibrate();
  
  // With synthetic data, calibration should succeed
  EXPECT_TRUE(result.success);
  EXPECT_GT(result.rms_error, 0.0);
}

// Test: CalibrationResult save/load
TEST_F(CameraCalibrationTest, TestSaveLoadCalibration)
{
  lra_vision::CalibrationResult result;
  result.success = true;
  result.rms_error = 0.5;
  result.image_width = 1920;
  result.image_height = 1080;
  result.camera_matrix = cv::Mat::eye(3, 3, CV_64F);
  result.camera_matrix.at<double>(0, 0) = 1000.0;
  result.camera_matrix.at<double>(1, 1) = 1000.0;
  result.camera_matrix.at<double>(0, 2) = 960.0;
  result.camera_matrix.at<double>(1, 2) = 540.0;
  result.dist_coeffs = cv::Mat::zeros(5, 1, CV_64F);
  result.calibration_timestamp = "2026-03-10 00:00:00";
  
  // Save to YAML
  std::string temp_file = "/tmp/test_calibration_result.yaml";
  result.save_to_yaml(temp_file);
  
  // Load from YAML
  auto loaded = lra_vision::CalibrationResult::from_yaml(temp_file);
  
  EXPECT_TRUE(loaded.success);
  EXPECT_DOUBLE_EQ(loaded.rms_error, 0.5);
  EXPECT_EQ(loaded.image_width, 1920);
  EXPECT_EQ(loaded.image_height, 1080);
  
  // Cleanup
  std::remove(temp_file.c_str());
}

int main(int argc, char** argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}