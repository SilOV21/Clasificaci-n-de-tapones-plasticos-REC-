// =============================================================================
// LRA Vision Package - Test Camera Detector
// Unit tests for V4L2 camera detection
// ROS2 Jazzy Jalisco - GTest
// =============================================================================

#include <gtest/gtest.h>
#include "lra_vision/camera_detector.hpp"

class CameraDetectorTest : public ::testing::Test
{
protected:
  void SetUp() override
  {
    // Test setup
  }
  
  void TearDown() override
  {
    // Test cleanup
  }
};

// Test: Detect all cameras on the system
TEST_F(CameraDetectorTest, TestDetectAllCameras)
{
  auto cameras = lra_vision::CameraDetector::detect_all_cameras();
  
  // Should return a vector (may be empty if no cameras)
  EXPECT_NO_THROW(cameras.size());
  
  // Each camera should have valid device path
  for (const auto& cam : cameras) {
    EXPECT_TRUE(cam.device_path.find("/dev/video") == 0);
    EXPECT_FALSE(cam.camera_name.empty());
  }
}

// Test: Find StreamCam (may not be present on test system)
TEST_F(CameraDetectorTest, TestFindStreamCam)
{
  auto streamcam = lra_vision::CameraDetector::find_streamcam();
  
  // Should not throw
  EXPECT_NO_THROW(streamcam.has_value());
  
  if (streamcam.has_value()) {
    EXPECT_TRUE(streamcam->is_streamcam);
    EXPECT_TRUE(streamcam->capabilities.is_capture_device);
  }
}

// Test: Find camera by name pattern
TEST_F(CameraDetectorTest, TestFindCameraByName)
{
  // Search for any camera
  auto cam = lra_vision::CameraDetector::find_camera_by_name("video");
  
  // Should not throw
  EXPECT_NO_THROW(cam.has_value());
  
  // Search for non-existent camera
  auto nonexistent = lra_vision::CameraDetector::find_camera_by_name("nonexistent_camera_xyz");
  EXPECT_FALSE(nonexistent.has_value());
}

// Test: Get camera info for specific device
TEST_F(CameraDetectorTest, TestGetCameraInfo)
{
  // Test with non-existent device
  auto invalid = lra_vision::CameraDetector::get_camera_info("/dev/video999");
  EXPECT_FALSE(invalid.has_value());
  
  // Test with valid device (may or may not exist)
  auto cameras = lra_vision::CameraDetector::detect_all_cameras();
  if (!cameras.empty()) {
    auto info = lra_vision::CameraDetector::get_camera_info(cameras[0].device_path);
    if (info.has_value()) {
      EXPECT_EQ(info->device_path, cameras[0].device_path);
    }
  }
}

// Test: Validate camera device
TEST_F(CameraDetectorTest, TestIsValidCameraDevice)
{
  // Invalid device path
  EXPECT_FALSE(lra_vision::CameraDetector::is_valid_camera_device("/dev/nonexistent"));
  
  // Test with first available camera
  auto cameras = lra_vision::CameraDetector::detect_all_cameras();
  if (!cameras.empty()) {
    EXPECT_TRUE(lra_vision::CameraDetector::is_valid_camera_device(cameras[0].device_path));
  }
}

// Test: Get first capture device
TEST_F(CameraDetectorTest, TestGetFirstCaptureDevice)
{
  auto first = lra_vision::CameraDetector::get_first_capture_device();
  
  EXPECT_NO_THROW(first.has_value());
  
  if (first.has_value()) {
    EXPECT_TRUE(first->capabilities.is_capture_device);
  }
}

// Test: Get all capture devices
TEST_F(CameraDetectorTest, TestGetCaptureDevices)
{
  auto devices = lra_vision::CameraDetector::get_capture_devices();
  
  for (const auto& dev : devices) {
    EXPECT_TRUE(dev.capabilities.is_capture_device);
    EXPECT_FALSE(dev.camera_name.empty());
  }
}

// Test: CameraCapabilities structure
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

// Test: CameraInfo structure
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