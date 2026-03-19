// =============================================================================
// LRA Vision Package - Camera Manager Node
// Manages v4l2_camera node with auto-detection, status monitoring, and reconnect
// ROS2 Jazzy Jalisco - C++17
// =============================================================================

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <std_msgs/msg/string.hpp>
#include <std_srvs/srv/trigger.hpp>

#include "lra_vision/camera_detector.hpp"

#include <thread>
#include <atomic>
#include <chrono>
#include <array>
#include <memory>
#include <sstream>
#include <csignal>
#include <sys/wait.h>

namespace lra_vision
{

/**
 * @class CameraManagerNode
 * @brief Manages v4l2_camera node with auto-detection and monitoring.
 *
 * This node:
 * - Auto-detects camera using CameraDetector
 * - Launches v4l2_camera as subprocess with optimal parameters
 * - Monitors frame flow via image topic subscription
 * - Publishes status JSON
 * - Provides reconnect service
 */
class CameraManagerNode : public rclcpp::Node
{
public:
  explicit CameraManagerNode(const rclcpp::NodeOptions& options = rclcpp::NodeOptions())
  : Node("camera_manager", options)
  , v4l2_pid_(-1)
  , running_(true)
  , frames_received_(0)
  {
    // Declare parameters (nested structure matching camera_params.yaml)
    this->declare_parameter("camera.video_device", "/dev/video2");
    this->declare_parameter("camera.name", "logitech_streamcam");
    this->declare_parameter("camera.resolution.width", 640);
    this->declare_parameter("camera.resolution.height", 480);
    this->declare_parameter("camera.resolution.framerate", 60);
    this->declare_parameter("camera.pixel_format", "YUYV");
    this->declare_parameter("camera.auto_detect", true);
    this->declare_parameter("frames.optical_frame", "camera_optical_frame");
    this->declare_parameter("topics.image_raw", "camera/image_raw");
    this->declare_parameter("topics.camera_info", "camera/camera_info");
    this->declare_parameter("camera_manager.status_rate", 5.0);  // Hz

    // Get parameters
    video_device_ = this->get_parameter("camera.video_device").as_string();
    camera_name_ = this->get_parameter("camera.name").as_string();
    image_width_ = this->get_parameter("camera.resolution.width").as_int();
    image_height_ = this->get_parameter("camera.resolution.height").as_int();
    framerate_ = this->get_parameter("camera.resolution.framerate").as_int();
    pixel_format_ = this->get_parameter("camera.pixel_format").as_string();
    auto_detect_ = this->get_parameter("camera.auto_detect").as_bool();
    frame_id_ = this->get_parameter("frames.optical_frame").as_string();
    image_topic_ = this->get_parameter("topics.image_raw").as_string();
    camera_info_topic_ = this->get_parameter("topics.camera_info").as_string();
    status_rate_ = this->get_parameter("camera_manager.status_rate").as_double();

    // Initialize publishers
    status_pub_ = this->create_publisher<std_msgs::msg::String>("camera/status", 10);

    // Initialize services
    reconnect_srv_ = this->create_service<std_srvs::srv::Trigger>(
      "camera/reconnect",
      std::bind(&CameraManagerNode::handle_reconnect, this,
                std::placeholders::_1, std::placeholders::_2));

    // Auto-detect camera if enabled
    if (auto_detect_) {
      auto_detect_camera();
    }

    // Start v4l2_camera
    if (!start_v4l2_camera()) {
      RCLCPP_ERROR(this->get_logger(), "Failed to start v4l2_camera");
    }

    // Subscribe to image topic for monitoring
    image_sub_ = this->create_subscription<sensor_msgs::msg::Image>(
      image_topic_, rclcpp::QoS(10).best_effort(),
      std::bind(&CameraManagerNode::image_callback, this, std::placeholders::_1));

    // Status timer
    auto status_period = std::chrono::duration<double>(1.0 / status_rate_);
    status_timer_ = this->create_wall_timer(
      std::chrono::duration_cast<std::chrono::nanoseconds>(status_period),
      std::bind(&CameraManagerNode::publish_status, this));

    RCLCPP_INFO(this->get_logger(), "Camera manager node initialized");
    RCLCPP_INFO(this->get_logger(), "Monitoring topic: %s", image_topic_.c_str());
  }

  ~CameraManagerNode()
  {
    running_ = false;
    stop_v4l2_camera();
  }

private:
  // Parameters
  std::string video_device_;
  std::string camera_name_;
  std::string frame_id_;
  int image_width_;
  int image_height_;
  int framerate_;
  std::string pixel_format_;
  bool auto_detect_;
  std::string image_topic_;
  std::string camera_info_topic_;
  double status_rate_;

  // v4l2_camera process
  pid_t v4l2_pid_;
  std::atomic<bool> running_;

  // Monitoring
  rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr image_sub_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr status_pub_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr reconnect_srv_;
  rclcpp::TimerBase::SharedPtr status_timer_;

  // Statistics
  std::chrono::steady_clock::time_point last_frame_time_;
  std::chrono::steady_clock::time_point start_time_;
  double current_fps_{0.0};
  std::mutex stats_mutex_;
  std::atomic<uint64_t> frames_received_{0};
  std::atomic<uint64_t> frames_dropped_{0};

  /**
   * @brief Auto-detect camera device.
   */
  void auto_detect_camera()
  {
    RCLCPP_INFO(this->get_logger(), "Auto-detecting camera...");

    // Try to find StreamCam first
    auto streamcam = CameraDetector::find_streamcam();
    if (streamcam) {
      video_device_ = streamcam->device_path;
      camera_name_ = streamcam->camera_name;
      RCLCPP_INFO(this->get_logger(), "Found Logitech StreamCam at %s",
                  video_device_.c_str());
      return;
    }

    // Try video2, then video3, then first available
    for (const auto& device : {"/dev/video2", "/dev/video3"}) {
      auto cam_info = CameraDetector::get_camera_info(device);
      if (cam_info && cam_info->capabilities.is_capture_device) {
        video_device_ = cam_info->device_path;
        camera_name_ = cam_info->camera_name;
        RCLCPP_INFO(this->get_logger(), "Using camera at %s: %s",
                    video_device_.c_str(), camera_name_.c_str());
        return;
      }
    }

    // Fall back to first available
    auto cameras = CameraDetector::get_capture_devices();
    if (!cameras.empty()) {
      video_device_ = cameras[0].device_path;
      camera_name_ = cameras[0].camera_name;
      RCLCPP_INFO(this->get_logger(), "Using first available camera: %s at %s",
                  camera_name_.c_str(), video_device_.c_str());
    } else {
      RCLCPP_WARN(this->get_logger(), "No cameras found, using configured device: %s",
                  video_device_.c_str());
    }
  }

  /**
   * @brief Start v4l2_camera node as subprocess.
   */
  bool start_v4l2_camera()
  {
    // Stop existing process if running
    stop_v4l2_camera();

    RCLCPP_INFO(this->get_logger(), "Starting v4l2_camera with device: %s", video_device_.c_str());

    // Build command arguments
    std::vector<std::string> args = {
      "ros2", "run", "v4l2_camera", "v4l2_camera_node",
      "--ros-args",
      "-p", "video_device:=" + video_device_,
      "-p", "image_size:=[" + std::to_string(image_width_) + "," + std::to_string(image_height_) + "]",
      "-p", "time_per_frame:=" + std::to_string(1000000000 / framerate_),  // nanoseconds
      "-p", "pixel_format:=\"" + pixel_format_ + "\"",
      "-p", "camera_frame_id:=\"" + frame_id_ + "\"",
      "-p", "image_topic:=\"" + image_topic_ + "\"",
      "-p", "camera_info_topic:=\"" + camera_info_topic_ + "\""
    };

    // Fork and exec
    pid_t pid = fork();
    if (pid == -1) {
      RCLCPP_ERROR(this->get_logger(), "Failed to fork process");
      return false;
    }

    if (pid == 0) {
      // Child process - convert args to char* array
      std::vector<char*> c_args;
      for (auto& arg : args) {
        c_args.push_back(const_cast<char*>(arg.c_str()));
      }
      c_args.push_back(nullptr);

      // Execute v4l2_camera
      execvp(c_args[0], c_args.data());
      // If we get here, exec failed
      RCLCPP_ERROR(this->get_logger(), "Failed to exec v4l2_camera");
      exit(1);
    }

    // Parent process
    v4l2_pid_ = pid;
    start_time_ = std::chrono::steady_clock::now();

    RCLCPP_INFO(this->get_logger(), "v4l2_camera started with PID %d", v4l2_pid_);

    // Wait a moment for v4l2_camera to initialize
    std::this_thread::sleep_for(std::chrono::milliseconds(500));

    // Check if process is still running
    if (kill(v4l2_pid_, 0) != 0) {
      RCLCPP_ERROR(this->get_logger(), "v4l2_camera process failed to start");
      v4l2_pid_ = -1;
      return false;
    }

    return true;
  }

  /**
   * @brief Stop v4l2_camera subprocess.
   */
  void stop_v4l2_camera()
  {
    if (v4l2_pid_ > 0) {
      RCLCPP_INFO(this->get_logger(), "Stopping v4l2_camera (PID %d)", v4l2_pid_);

      // Try graceful shutdown first
      kill(v4l2_pid_, SIGTERM);

      // Wait for process to exit
      int status;
      pid_t result = waitpid(v4l2_pid_, &status, WNOHANG);

      if (result == 0) {
        // Process still running, wait a bit
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
        result = waitpid(v4l2_pid_, &status, WNOHANG);

        if (result == 0) {
          // Force kill
          RCLCPP_WARN(this->get_logger(), "Force killing v4l2_camera");
          kill(v4l2_pid_, SIGKILL);
          waitpid(v4l2_pid_, &status, 0);
        }
      }

      v4l2_pid_ = -1;
    }
  }

  /**
   * @brief Image topic callback for monitoring.
   */
  void image_callback(const sensor_msgs::msg::Image::SharedPtr msg)
  {
    std::lock_guard<std::mutex> lock(stats_mutex_);

    frames_received_++;

    auto now = std::chrono::steady_clock::now();
    if (last_frame_time_.time_since_epoch().count() > 0) {
      auto delta = std::chrono::duration_cast<std::chrono::microseconds>(now - last_frame_time_).count();
      if (delta > 0) {
        current_fps_ = 1000000.0 / delta;
      }
    }
    last_frame_time_ = now;
  }

  /**
   * @brief Handle reconnect service call.
   */
  void handle_reconnect(
    const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    (void)request;

    RCLCPP_INFO(this->get_logger(), "Reconnect service called");

    // Reset statistics
    {
      std::lock_guard<std::mutex> lock(stats_mutex_);
      frames_received_ = 0;
      frames_dropped_ = 0;
      current_fps_ = 0.0;
      last_frame_time_ = std::chrono::steady_clock::time_point();
    }

    // Re-detect if auto-detect is enabled
    if (auto_detect_) {
      auto_detect_camera();
    }

    // Restart v4l2_camera
    bool success = start_v4l2_camera();

    response->success = success;
    response->message = success ? "Camera reconnected successfully" : "Failed to reconnect camera";

    RCLCPP_INFO(this->get_logger(), "%s", response->message.c_str());
  }

  /**
   * @brief Publish status message.
   */
  void publish_status()
  {
    auto msg = std_msgs::msg::String();

    std::lock_guard<std::mutex> lock(stats_mutex_);

    // Calculate runtime
    auto runtime = std::chrono::steady_clock::now() - start_time_;
    auto runtime_sec = std::chrono::duration_cast<std::chrono::seconds>(runtime).count();

    // Build JSON status
    std::ostringstream ss;
    ss << "{";
    ss << "\"device\": \"" << video_device_ << "\", ";
    ss << "\"camera_name\": \"" << camera_name_ << "\", ";
    ss << "\"connected\": " << (v4l2_pid_ > 0 && kill(v4l2_pid_, 0) == 0 ? "true" : "false") << ", ";
    ss << "\"frames_received\": " << frames_received_.load() << ", ";
    ss << "\"frames_dropped\": " << frames_dropped_.load() << ", ";
    ss << "\"current_fps\": " << std::fixed << std::setprecision(2) << current_fps_ << ", ";
    ss << "\"resolution\": \"" << image_width_ << "x" << image_height_ << "\", ";
    ss << "\"framerate\": " << framerate_ << ", ";
    ss << "\"runtime_seconds\": " << runtime_sec;
    ss << "}";

    msg.data = ss.str();
    status_pub_->publish(msg);
  }
};

}  // namespace lra_vision

// Main function for standalone execution
int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);

  auto node = std::make_shared<lra_vision::CameraManagerNode>();

  rclcpp::spin(node);

  rclcpp::shutdown();
  return 0;
}
