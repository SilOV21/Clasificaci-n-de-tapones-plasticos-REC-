

#include <gtest/gtest.h>
#include "lra_vision/camera_detector.hpp"

class CameraDetectorTest : public ::testing::Test
{
protected:
  void SetUp() override
  {

  }

  void TearDown() override
  {

  }
};

TEST_F(CameraDetectorTest, TestDetectAllCameras)
{
  auto cameras = lra_vision::CameraDetector::detect_all_cameras();


  EXPECT_NO_THROW(cameras.size());


  for (const auto& cam : cameras) {
    EXPECT_TRUE(cam.device_path.find("/dev/video") == 0);
    EXPECT_FALSE(cam.camera_name.empty());
  }
}

TEST_F(CameraDetectorTest, TestFindStreamCam)
{
  auto streamcam = lra_vision::CameraDetector::find_streamcam();


  EXPECT_NO_THROW(streamcam.has_value());

  if (streamcam.has_value()) {
    EXPECT_TRUE(streamcam->is_streamcam);
    EXPECT_TRUE(streamcam->capabilities.is_capture_device);
  }
}

TEST_F(CameraDetectorTest, TestFindCameraByName)
{

  auto cam = lra_vision::CameraDetector::find_camera_by_name("video");


  EXPECT_NO_THROW(cam.has_value());


  auto nonexistent = lra_vision::CameraDetector::find_camera_by_name("nonexistent_camera_xyz");
  EXPECT_FALSE(nonexistent.has_value());
}

TEST_F(CameraDetectorTest, TestGetCameraInfo)
{

  auto invalid = lra_vision::CameraDetector::get_camera_info("/dev/video999");
  EXPECT_FALSE(invalid.has_value());


  auto cameras = lra_vision::CameraDetector::detect_all_cameras();
  if (!cameras.empty()) {
    auto info = lra_vision::CameraDetector::get_camera_info(cameras[0].device_path);
    if (info.has_value()) {
      EXPECT_EQ(info->device_path, cameras[0].device_path);
    }
  }
}

TEST_F(CameraDetectorTest, TestIsValidCameraDevice)
{

  EXPECT_FALSE(lra_vision::CameraDetector::is_valid_camera_device("/dev/nonexistent"));


  auto cameras = lra_vision::CameraDetector::detect_all_cameras();
  if (!cameras.empty()) {
    EXPECT_TRUE(lra_vision::CameraDetector::is_valid_camera_device(cameras[0].device_path));
  }
}

TEST_F(CameraDetectorTest, TestGetFirstCaptureDevice)
{
  auto first = lra_vision::CameraDetector::get_first_capture_device();

  EXPECT_NO_THROW(first.has_value());

  if (first.has_value()) {
    EXPECT_TRUE(first->capabilities.is_capture_device);
  }
}

TEST_F(CameraDetectorTest, TestGetCaptureDevices)
{
  auto devices = lra_vision::CameraDetector::get_capture_devices();

  for (const auto& dev : devices) {
    EXPECT_TRUE(dev.capabilities.is_capture_device);
    EXPECT_FALSE(dev.camera_name.empty());
  }
}

TEST_F(CameraDetectorTest, TestCameraCapabilities)
{
  lra_vision::CameraCapabilities caps;
  caps.device_path = "/dev/video0";
  caps.driver = "uvcvideo";
  caps.card = "Logitech StreamCam";
  caps.bus_info = "usb-0000:00:1a.0-1";
  caps.version = 0x00050a;
  caps.is_capture_device = true;
  caps.is_output_device = false;

  EXPECT_EQ(caps.device_path, "/dev/video0");
  EXPECT_EQ(caps.driver, "uvcvideo");
  EXPECT_TRUE(caps.is_capture_device);
  EXPECT_FALSE(caps.is_output_device);
}

TEST_F(CameraDetectorTest, TestCameraInfo)
{
  lra_vision::CameraInfo info;
  info.device_path = "/dev/video2";
  info.camera_name = "Logitech StreamCam";
  info.is_streamcam = true;

  EXPECT_EQ(info.device_path, "/dev/video2");
  EXPECT_EQ(info.camera_name, "Logitech StreamCam");
  EXPECT_TRUE(info.is_streamcam);
}

int main(int argc, char** argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}