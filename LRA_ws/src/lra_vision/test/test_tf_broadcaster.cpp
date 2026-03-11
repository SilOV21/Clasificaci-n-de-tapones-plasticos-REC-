// =============================================================================
// LRA Vision Package - Test TF Broadcaster
// Unit tests for camera-UR3 TF transforms
// ROS2 Jazzy Jalisco - GTest
// =============================================================================

#include <gtest/gtest.h>
#include <rclcpp/rclcpp.hpp>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Matrix3x3.h>
#include <opencv2/opencv.hpp>
#include "lra_vision/camera_tf_broadcaster.hpp"
#include "lra_vision/ur3_camera_transform.hpp"

class TfBroadcasterTest : public ::testing::Test
{
protected:
  void SetUp() override
  {
    rclcpp::init(0, nullptr);
    node_ = std::make_shared<rclcpp::Node>("test_tf_broadcaster");
  }
  
  void TearDown() override
  {
    node_.reset();
    rclcpp::shutdown();
  }
  
  rclcpp::Node::SharedPtr node_;
};

// Test: CameraMountConfig default values
TEST_F(TfBroadcasterTest, TestCameraMountConfigDefaults)
{
  lra_vision::CameraMountConfig config;
  
  EXPECT_DOUBLE_EQ(config.translation_x, 0.0);
  EXPECT_DOUBLE_EQ(config.translation_y, 0.0);
  EXPECT_DOUBLE_EQ(config.translation_z, 0.05);
  EXPECT_DOUBLE_EQ(config.roll, 0.0);
  EXPECT_DOUBLE_EQ(config.pitch, 0.0);
  EXPECT_DOUBLE_EQ(config.yaw, 0.0);
  EXPECT_EQ(config.parent_frame, "tool0");
  EXPECT_EQ(config.camera_frame, "camera_link");
  EXPECT_EQ(config.optical_frame, "camera_optical_frame");
}

// Test: CameraMountConfig overhead preset
TEST_F(TfBroadcasterTest, TestCameraMountConfigOverhead)
{
  auto config = lra_vision::CameraMountConfig::overhead(0.05);
  
  EXPECT_DOUBLE_EQ(config.translation_x, 0.0);
  EXPECT_DOUBLE_EQ(config.translation_y, 0.0);
  EXPECT_DOUBLE_EQ(config.translation_z, 0.05);
  EXPECT_DOUBLE_EQ(config.roll, 0.0);
  EXPECT_DOUBLE_EQ(config.pitch, M_PI);
  EXPECT_DOUBLE_EQ(config.yaw, 0.0);
}

// Test: CameraMountConfig angled preset
TEST_F(TfBroadcasterTest, TestCameraMountConfigAngled)
{
  auto config = lra_vision::CameraMountConfig::angled(45.0, 0.05);
  
  // Should have some X translation for angled view
  EXPECT_GT(config.translation_x, 0.0);
  EXPECT_DOUBLE_EQ(config.translation_y, 0.0);
  EXPECT_GT(config.translation_z, 0.0);
}

// Test: Euler to quaternion conversion
TEST_F(TfBroadcasterTest, TestEulerToQuaternion)
{
  // Test identity rotation
  auto q_identity = lra_vision::tf_utils::euler_to_quaternion(0, 0, 0);
  EXPECT_NEAR(q_identity[3], 1.0, 0.001);  // w should be 1
  
  // Test 180 degree rotation around Y (pointing down)
  auto q_down = lra_vision::tf_utils::euler_to_quaternion(0, M_PI, 0);
  EXPECT_NEAR(q_down[3], 0.0, 0.001);  // w should be near 0
  
  // Test 90 degree rotation around Z
  auto q_90z = lra_vision::tf_utils::euler_to_quaternion(0, 0, M_PI/2);
  EXPECT_NEAR(q_90z[3], std::cos(M_PI/4), 0.001);
}

// Test: Quaternion to Euler conversion
TEST_F(TfBroadcasterTest, TestQuaternionToEuler)
{
  // Test round-trip conversion
  double roll = 0.1;
  double pitch = 0.2;
  double yaw = 0.3;
  
  auto q = lra_vision::tf_utils::euler_to_quaternion(roll, pitch, yaw);
  auto euler = lra_vision::tf_utils::quaternion_to_euler(q);
  
  EXPECT_NEAR(euler[0], roll, 0.001);
  EXPECT_NEAR(euler[1], pitch, 0.001);
  EXPECT_NEAR(euler[2], yaw, 0.001);
}

// Test: Make transform with RPY
TEST_F(TfBroadcasterTest, TestMakeTransformRPY)
{
  auto transform = lra_vision::tf_utils::make_transform_rpy(
    "parent", "child",
    0.1, 0.2, 0.3,
    0.0, M_PI, 0.0  // 180 degree rotation around Y
  );
  
  EXPECT_EQ(transform.header.frame_id, "parent");
  EXPECT_EQ(transform.child_frame_id, "child");
  EXPECT_DOUBLE_EQ(transform.transform.translation.x, 0.1);
  EXPECT_DOUBLE_EQ(transform.transform.translation.y, 0.2);
  EXPECT_DOUBLE_EQ(transform.transform.translation.z, 0.3);
}

// Test: Make transform with quaternion
TEST_F(TfBroadcasterTest, TestMakeTransformQuaternion)
{
  auto q = lra_vision::tf_utils::euler_to_quaternion(0, M_PI, 0);
  
  auto transform = lra_vision::tf_utils::make_transform(
    "parent", "child",
    0.0, 0.0, 0.05,
    q[0], q[1], q[2], q[3]
  );
  
  EXPECT_EQ(transform.header.frame_id, "parent");
  EXPECT_EQ(transform.child_frame_id, "child");
  EXPECT_DOUBLE_EQ(transform.transform.translation.z, 0.05);
  
  // Check quaternion
  EXPECT_NEAR(transform.transform.rotation.x, q[0], 0.001);
  EXPECT_NEAR(transform.transform.rotation.y, q[1], 0.001);
  EXPECT_NEAR(transform.transform.rotation.z, q[2], 0.001);
  EXPECT_NEAR(transform.transform.rotation.w, q[3], 0.001);
}

// Test: CameraTfBroadcaster initialization
TEST_F(TfBroadcasterTest, TestCameraTfBroadcasterInit)
{
  lra_vision::CameraMountConfig config;
  config.translation_z = 0.05;
  
  EXPECT_NO_THROW({
    lra_vision::CameraTfBroadcaster broadcaster(node_, config);
  });
}

// Test: CameraTfBroadcaster get_camera_transform
TEST_F(TfBroadcasterTest, TestGetCameraTransform)
{
  lra_vision::CameraMountConfig config;
  config.translation_z = 0.05;
  config.pitch = M_PI;
  
  lra_vision::CameraTfBroadcaster broadcaster(node_, config);
  
  auto transform = broadcaster.get_camera_transform();
  
  EXPECT_DOUBLE_EQ(transform.transform.translation.x, 0.0);
  EXPECT_DOUBLE_EQ(transform.transform.translation.y, 0.0);
  EXPECT_DOUBLE_EQ(transform.transform.translation.z, 0.05);
}

// Test: CameraTfBroadcaster update_config
TEST_F(TfBroadcasterTest, TestUpdateConfig)
{
  lra_vision::CameraMountConfig config;
  config.translation_z = 0.05;
  
  lra_vision::CameraTfBroadcaster broadcaster(node_, config);
  
  // Update config
  lra_vision::CameraMountConfig new_config;
  new_config.translation_z = 0.10;
  
  EXPECT_NO_THROW(broadcaster.update_config(new_config));
  
  const auto& updated = broadcaster.get_config();
  EXPECT_DOUBLE_EQ(updated.translation_z, 0.10);
}

// Test: CameraTfBroadcaster set_parent_frame
TEST_F(TfBroadcasterTest, TestSetParentFrame)
{
  lra_vision::CameraMountConfig config;
  
  lra_vision::CameraTfBroadcaster broadcaster(node_, config);
  
  EXPECT_NO_THROW(broadcaster.set_parent_frame("base_link"));
  
  const auto& updated = broadcaster.get_config();
  EXPECT_EQ(updated.parent_frame, "base_link");
}

// Test: Optical frame transform creation
TEST_F(TfBroadcasterTest, TestOpticalFrameTransform)
{
  // Optical frame should have Z forward, X right, Y down
  // This is a rotation of -90 deg around Z, then -90 deg around X
  // from standard camera_link orientation
  
  // Expected quaternion for optical frame
  auto q = lra_vision::tf_utils::euler_to_quaternion(-M_PI/2, 0, -M_PI/2);
  
  // Verify it's a valid rotation (quaternion should be normalized)
  double norm = std::sqrt(q[0]*q[0] + q[1]*q[1] + q[2]*q[2] + q[3]*q[3]);
  EXPECT_NEAR(norm, 1.0, 0.001);
}

// Test: UR3 camera namespace functions
TEST_F(TfBroadcasterTest, TestUR3CameraUtilities)
{
  // Test default mount config
  auto default_config = lra_vision::ur3_camera::get_default_mount_config();
  
  EXPECT_DOUBLE_EQ(default_config.translation_z, 0.05);
  EXPECT_DOUBLE_EQ(default_config.pitch, M_PI);
  EXPECT_EQ(default_config.parent_frame, "tool0");
  
  // Test side mount config
  auto side_config = lra_vision::ur3_camera::get_side_mount_config(45.0, 0.08);
  
  EXPECT_GT(side_config.translation_x, 0.0);  // Should have some forward offset
  EXPECT_GT(side_config.translation_z, 0.0);  // Should have some up offset
  
  // Test camera_to_tcp
  std::array<double, 3> camera_point = {0.0, 0.0, 0.1};  // 10cm in front of camera
  auto tcp_point = lra_vision::ur3_camera::camera_to_tcp(camera_point);
  
  // Verify transformation
  // For downward camera: camera X -> robot -Y, camera Y -> robot -X, camera Z -> robot -(Z-5cm)
  EXPECT_NEAR(tcp_point[0], 0.0, 0.001);   // -Y
  EXPECT_NEAR(tcp_point[1], 0.0, 0.001);    // -X
  EXPECT_NEAR(tcp_point[2], -0.05, 0.001); // 5cm - 10cm = -5cm
  
  // Test StreamCamParameters
  lra_vision::ur3_camera::StreamCamParameters params;
  
  EXPECT_GT(params.focal_length_x, 0.0);
  EXPECT_GT(params.focal_length_y, 0.0);
  EXPECT_FALSE(params.resolutions.empty());
  
  // Test get_camera_matrix
  cv::Mat K = params.get_camera_matrix(1920, 1080);
  EXPECT_EQ(K.rows, 3);
  EXPECT_EQ(K.cols, 3);
  
  // Test get_distortion_coefficients
  cv::Mat D = params.get_distortion_coefficients();
  EXPECT_EQ(D.rows, 5);
  EXPECT_EQ(D.cols, 1);
}

int main(int argc, char** argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}