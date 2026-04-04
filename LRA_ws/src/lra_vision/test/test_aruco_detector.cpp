

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
    config_.marker_size = 0.05;
    config_.dictionary = cv::aruco::DICT_4X4_50;
  }

  void TearDown() override
  {

  }

  lra_vision::ArucoConfig config_;


  cv::Mat generateArUcoImage()
  {
    cv::Mat image = cv::Mat::zeros(800, 600, CV_8UC3);
    image.setTo(cv::Scalar(255, 255, 255));


    cv::Ptr<cv::aruco::Dictionary> dictionary = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_50);


    cv::Mat marker;
    cv::aruco::drawMarker(dictionary, 0, 200, marker);


    cv::Mat marker_color;
    cv::cvtColor(marker, marker_color, cv::COLOR_GRAY2BGR);

    cv::Rect roi(100, 100, 200, 200);
    marker_color.copyTo(image(roi));

    return image;
  }


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

TEST_F(ArUcoDetectorTest, TestArucoConfigDefaults)
{
  auto config = lra_vision::ArucoConfig::default_config();

  EXPECT_EQ(config.dictionary, cv::aruco::DICT_4X4_50);
  EXPECT_DOUBLE_EQ(config.marker_size, 0.05);
}

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


  cv::Point2f center = marker.get_center();
  EXPECT_FLOAT_EQ(center.x, 50.0f);
  EXPECT_FLOAT_EQ(center.y, 50.0f);


  cv::Mat R = marker.get_rotation_matrix();
  EXPECT_EQ(R.rows, 3);
  EXPECT_EQ(R.cols, 3);


  cv::Mat pose = marker.get_pose_matrix();
  EXPECT_EQ(pose.rows, 4);
  EXPECT_EQ(pose.cols, 4);
}

TEST_F(ArUcoDetectorTest, TestInitialization)
{
  EXPECT_NO_THROW({
    lra_vision::ArucoDetector detector(config_);
  });
}

TEST_F(ArUcoDetectorTest, TestDetectOnSyntheticImage)
{
  lra_vision::ArucoDetector detector(config_);

  cv::Mat test_image = generateArUcoImage();

  auto markers = detector.detect(test_image);


  EXPECT_GE(markers.size(), 1);

  if (!markers.empty()) {
    EXPECT_EQ(markers[0].id, 0);
    EXPECT_EQ(markers[0].corners.size(), 4);
  }
}

TEST_F(ArUcoDetectorTest, TestDetectMultipleMarkers)
{
  lra_vision::ArucoDetector detector(config_);

  cv::Mat test_image = generateMultipleArUcoImage(4);

  auto markers = detector.detect(test_image);


  EXPECT_GE(markers.size(), 1);
}

TEST_F(ArUcoDetectorTest, TestDetectSpecificIds)
{
  lra_vision::ArucoDetector detector(config_);

  cv::Mat test_image = generateMultipleArUcoImage(4);


  std::vector<int> target_ids = {0, 1, 2};

  auto markers = detector.detect_specific(test_image, target_ids);


  for (const auto& marker : markers) {
    EXPECT_TRUE(std::find(target_ids.begin(), target_ids.end(), marker.id) != target_ids.end());
  }
}

TEST_F(ArUcoDetectorTest, TestSetConfig)
{
  lra_vision::ArucoDetector detector(config_);

  lra_vision::ArucoConfig new_config = config_;
  new_config.marker_size = 0.10;

  EXPECT_NO_THROW(detector.set_config(new_config));

  EXPECT_DOUBLE_EQ(detector.get_config().marker_size, 0.10);
}

TEST_F(ArUcoDetectorTest, TestSetMarkerSize)
{
  lra_vision::ArucoDetector detector(config_);

  detector.set_marker_size(0.08);

  EXPECT_DOUBLE_EQ(detector.get_config().marker_size, 0.08);
}

TEST_F(ArUcoDetectorTest, TestSetCameraCalibration)
{
  lra_vision::ArucoDetector detector(config_);


  cv::Mat camera_matrix = cv::Mat::eye(3, 3, CV_64F);
  camera_matrix.at<double>(0, 0) = 1000.0;
  camera_matrix.at<double>(1, 1) = 1000.0;
  camera_matrix.at<double>(0, 2) = 640.0;
  camera_matrix.at<double>(1, 2) = 480.0;

  cv::Mat dist_coeffs = cv::Mat::zeros(5, 1, CV_64F);

  detector.set_camera_matrix(camera_matrix, dist_coeffs);

  EXPECT_TRUE(detector.has_camera_calibration());
}

TEST_F(ArUcoDetectorTest, TestDetectWithPose)
{
  lra_vision::ArucoDetector detector(config_);


  cv::Mat camera_matrix = cv::Mat::eye(3, 3, CV_64F);
  camera_matrix.at<double>(0, 0) = 1000.0;
  camera_matrix.at<double>(1, 1) = 1000.0;
  camera_matrix.at<double>(0, 2) = 400.0;
  camera_matrix.at<double>(1, 2) = 300.0;

  cv::Mat dist_coeffs = cv::Mat::zeros(5, 1, CV_64F);
  detector.set_camera_matrix(camera_matrix, dist_coeffs);

  cv::Mat test_image = generateArUcoImage();

  auto markers = detector.detect_with_pose(test_image);


  for (const auto& marker : markers) {
    EXPECT_GT(marker.corners.size(), 0);
  }
}

TEST_F(ArUcoDetectorTest, TestDrawMarkers)
{
  lra_vision::ArucoDetector detector(config_);

  cv::Mat test_image = generateArUcoImage();
  auto markers = detector.detect(test_image);

  cv::Mat display = test_image.clone();

  EXPECT_NO_THROW(detector.draw_markers(display, markers, true, true));


  EXPECT_FALSE(display.empty());
}

TEST_F(ArUcoDetectorTest, TestGetDictionaryAndParameters)
{
  lra_vision::ArucoDetector detector(config_);

  auto dictionary = detector.get_dictionary();
  EXPECT_NO_THROW(dictionary.bytesList);

  auto params = detector.get_parameters();

  EXPECT_GT(params.adaptiveThreshWinSizeMin, 0);
  EXPECT_GT(params.adaptiveThreshWinSizeMax, params.adaptiveThreshWinSizeMin);
}

int main(int argc, char** argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}