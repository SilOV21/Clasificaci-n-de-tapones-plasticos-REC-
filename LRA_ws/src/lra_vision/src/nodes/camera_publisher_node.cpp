// =============================================================================
// LRA Vision Package - Camera Publisher Node
// Publishes camera images from V4L2 device with auto-detection
// ROS2 Jazzy Jalisco - C++17
// =============================================================================

#include <rclcpp/rclcpp.hpp>
#include <rclcpp_components/register_node_macro.hpp>
#include <image_transport/image_transport.hpp>
#include <camera_info_manager/camera_info_manager.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/msg/camera_info.hpp>
#include <std_msgs/msg/string.hpp>
#include <std_srvs/srv/trigger.hpp>

#include <opencv2/opencv.hpp>
#include <cv_bridge/cv_bridge.hpp>

#include "lra_vision/camera_detector.hpp"

#include <thread>
#include <atomic>
#include <mutex>
#include <chrono>

namespace lra_vision
{

/**
 * @class CameraPublisherNode
 * @brief ROS2 node that publishes camera images from a V4L2 device.
 * 
 * This node:
 * - Auto-detects Logitech StreamCam or falls back to first available camera
 * - Publishes camera images and camera_info
 * - Supports both video2 and video3 device paths
 * - Provides service to reconnect to camera
 */
class CameraPublisherNode : public rclcpp::Node
{
public:
  explicit CameraPublisherNode(const rclcpp::NodeOptions& options = rclcpp::NodeOptions())
  : Node("camera_publisher", options)
  , running_(false)
  {
    // Declare parameters
    this->declare_parameter("video_device", "/dev/video2");
    this->declare_parameter("camera_name", "logitech_streamcam");
    this->declare_parameter("frame_id", "camera_optical_frame");
    this->declare_parameter("image_width", 1920);
    this->declare_parameter("image_height", 1080);
    this->declare_parameter("framerate", 30);
    this->declare_parameter("pixel_format", "YUYV");
    this->declare_parameter("auto_detect", true);
    this->declare_parameter("camera_info_url", "");
    this->declare_parameter("publish_rate", 30.0);
    
    // Get parameters
    video_device_ = this->get_parameter("video_device").as_string();
    camera_name_ = this->get_parameter("camera_name").as_string();
    frame_id_ = this->get_parameter("frame_id").as_string();
    image_width_ = this->get_parameter("image_width").as_int();
    image_height_ = this->get_parameter("image_height").as_int();
    framerate_ = this->get_parameter("framerate").as_int();
    pixel_format_ = this->get_parameter("pixel_format").as_string();
    auto_detect_ = this->get_parameter("auto_detect").as_bool();
    camera_info_url_ = this->get_parameter("camera_info_url").as_string();
    publish_rate_ = this->get_parameter("publish_rate").as_double();
    
    // Initialize publishers
    image_pub_ = image_transport::create_publisher(this, "image_raw", rmw_qos_profile_sensor_data);
    camera_info_pub_ = this->create_publisher<sensor_msgs::msg::CameraInfo>(
      "camera_info", rclcpp::QoS(10).reliability(RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT));
    
    // Initialize camera info manager
    camera_info_manager_ = std::make_shared<camera_info_manager::CameraInfoManager>(
      this, camera_name_, camera_info_url_);
    
    // Initialize services
    reconnect_srv_ = this->create_service<std_srvs::srv::Trigger>(
      "reconnect",
      std::bind(&CameraPublisherNode::handle_reconnect, this,
                std::placeholders::_1, std::placeholders::_2));
    
    // Status publisher
    status_pub_ = this->create_publisher<std_msgs::msg::String>("status", 10);
    
    // Auto-detect camera if enabled
    if (auto_detect_) {
      auto_detected_device_ = detect_camera();
      if (auto_detected_device_) {
        video_device_ = auto_detected_device_->device_path;
        RCLCPP_INFO(this->get_logger(), "Auto-detected camera: %s at %s",
                    auto_detected_device_->camera_name.c_str(),
                    video_device_.c_str());
      } else {
        RCLCPP_WARN(this->get_logger(), "Auto-detection failed, using configured device: %s",
                    video_device_.c_str());
      }
    }
    
    // Start capture thread
    start_capture();
    
    // Timer for publishing status
    status_timer_ = this->create_wall_timer(
      std::chrono::seconds(5),
      std::bind(&CameraPublisherNode::publish_status, this));
    
    RCLCPP_INFO(this->get_logger(), "Camera publisher node initialized");
    RCLCPP_INFO(this->get_logger(), "Publishing on topic: image_raw");
    RCLCPP_INFO(this->get_logger(), "Frame ID: %s", frame_id_.c_str());
  }
  
  ~CameraPublisherNode()
  {
    stop_capture();
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
  std::string camera_info_url_;
  double publish_rate_;
  
  // Camera detection
  std::optional<CameraInfo> auto_detected_device_;
  
  // OpenCV video capture
  cv::VideoCapture cap_;
  std::atomic<bool> running_;
  std::thread capture_thread_;
  std::mutex capture_mutex_;
  
  // ROS2 components
  image_transport::Publisher image_pub_;
  rclcpp::Publisher<sensor_msgs::msg::CameraInfo>::SharedPtr camera_info_pub_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr status_pub_;
  std::shared_ptr<camera_info_manager::CameraInfoManager> camera_info_manager_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr reconnect_srv_;
  rclcpp::TimerBase::SharedPtr status_timer_;
  
  // Statistics
  std::atomic<int> frames_published_{0};
  std::atomic<int> frames_dropped_{0};
  std::chrono::steady_clock::time_point last_frame_time_;
  
  /**
   * @brief Detect and find the appropriate camera device.
   */
  std::optional<CameraInfo> detect_camera()
  {
    RCLCPP_INFO(this->get_logger(), "Scanning for cameras...");
    
    auto cameras = CameraDetector::get_capture_devices();
    
    if (cameras.empty()) {
      RCLCPP_ERROR(this->get_logger(), "No cameras found!");
      return std::nullopt;
    }
    
    RCLCPP_INFO(this->get_logger(), "Found %zu camera(s)", cameras.size());
    
    // Try to find StreamCam first
    auto streamcam = CameraDetector::find_streamcam();
    if (streamcam) {
      RCLCPP_INFO(this->get_logger(), "Found Logitech StreamCam at %s",
                  streamcam->device_path.c_str());
      return streamcam;
    }
    
    // Try video2, then video3, then first available
    for (const auto& device : {"/dev/video2", "/dev/video3"}) {
      auto cam_info = CameraDetector::get_camera_info(device);
      if (cam_info && cam_info->capabilities.is_capture_device) {
        RCLCPP_INFO(this->get_logger(), "Using camera at %s: %s",
                    device, cam_info->camera_name.c_str());
        return cam_info;
      }
    }
    
    // Fall back to first available
    RCLCPP_INFO(this->get_logger(), "Using first available camera: %s at %s",
                cameras[0].camera_name.c_str(), cameras[0].device_path.c_str());
    return cameras[0];
  }
  
  /**
   * @brief Open the camera device.
   */
  bool open_camera()
  {
    std::lock_guard<std::mutex> lock(capture_mutex_);
    
    if (cap_.isOpened()) {
      cap_.release();
    }
    
    int device_index = -1;
    
    // Parse device index from path
    if (video_device_.find("/dev/video") == 0) {
      device_index = std::stoi(video_device_.substr(10));
    } else {
      RCLCPP_ERROR(this->get_logger(), "Invalid video device path: %s", video_device_.c_str());
      return false;
    }
    
    RCLCPP_INFO(this->get_logger(), "Opening camera: %s (index %d)", 
                video_device_.c_str(), device_index);
    
    // Try different backends
    std::vector<int> backends = {cv::CAP_V4L2, cv::CAP_ANY};
    
    for (int backend : backends) {
      cap_.open(device_index, backend);
      
      if (cap_.isOpened()) {
        break;
      }
    }
    
    if (!cap_.isOpened()) {
      RCLCPP_ERROR(this->get_logger(), "Failed to open camera at %s", video_device_.c_str());
      return false;
    }
    
    // Set camera properties
    cap_.set(cv::CAP_PROP_FRAME_WIDTH, image_width_);
    cap_.set(cv::CAP_PROP_FRAME_HEIGHT, image_height_);
    cap_.set(cv::CAP_PROP_FPS, framerate_);
    cap_.set(cv::CAP_PROP_FOURCC, cv::VideoWriter::fourcc('Y', 'U', 'Y', 'V'));
    
    // Log actual settings
    int actual_width = static_cast<int>(cap_.get(cv::CAP_PROP_FRAME_WIDTH));
    int actual_height = static_cast<int>(cap_.get(cv::CAP_PROP_FRAME_HEIGHT));
    double actual_fps = cap_.get(cv::CAP_PROP_FPS);
    
    RCLCPP_INFO(this->get_logger(), "Camera opened: %dx%d @ %.1f fps",
                actual_width, actual_height, actual_fps);
    
    // Update parameters if different
    if (actual_width != image_width_ || actual_height != image_height_) {
      RCLCPP_WARN(this->get_logger(), 
                  "Camera using different resolution: %dx%d instead of %dx%d",
                  actual_width, actual_height, image_width_, image_height_);
      image_width_ = actual_width;
      image_height_ = actual_height;
    }
    
    return true;
  }
  
  /**
   * @brief Start the capture thread.
   */
  void start_capture()
  {
    if (running_) {
      return;
    }
    
    if (!open_camera()) {
      RCLCPP_ERROR(this->get_logger(), "Could not start capture - camera not opened");
      return;
    }
    
    running_ = true;
    capture_thread_ = std::thread(&CameraPublisherNode::capture_loop, this);
  }
  
  /**
   * @brief Stop the capture thread.
   */
  void stop_capture()
  {
    running_ = false;
    
    if (capture_thread_.joinable()) {
      capture_thread_.join();
    }
    
    std::lock_guard<std::mutex> lock(capture_mutex_);
    if (cap_.isOpened()) {
      cap_.release();
    }
  }
  
  /**
   * @brief Main capture loop.
   */
  void capture_loop()
  {
    cv::Mat frame;
    rclcpp::Time last_publish_time = this->get_clock()->now();
    double min_interval = 1.0 / publish_rate_;
    
    while (running_ && rclcpp::ok()) {
      {
        std::lock_guard<std::mutex> lock(capture_mutex_);
        
        if (!cap_.isOpened()) {
          RCLCPP_WARN(this->get_logger(), "Camera not opened, attempting to reconnect...");
          if (!open_camera()) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
            continue;
          }
        }
        
        if (!cap_.read(frame)) {
          RCLCPP_WARN(this->get_logger(), "Failed to read frame from camera");
          frames_dropped_++;
          std::this_thread::sleep_for(std::chrono::milliseconds(10));
          continue;
        }
      }
      
      // Rate limiting
      auto now = this->get_clock()->now();
      double elapsed = (now - last_publish_time).seconds();
      
      if (elapsed < min_interval) {
        continue;
      }
      last_publish_time = now;
      
      // Convert to ROS message
      auto msg = cv_bridge::CvImage(std_msgs::msg::Header(), "bgr8", frame).toImageMsg();
      msg->header.stamp = now;
      msg->header.frame_id = frame_id_;
      
      // Publish image
      image_pub_.publish(msg);
      
      // Publish camera info
      auto camera_info = camera_info_manager_->getCameraInfo();
      camera_info.header = msg->header;
      camera_info.width = image_width_;
      camera_info.height = image_height_;
      camera_info_pub_->publish(camera_info);
      
      frames_published_++;
      last_frame_time_ = std::chrono::steady_clock::now();
    }
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
    
    stop_capture();
    
    // Re-detect if auto-detect is enabled
    if (auto_detect_) {
      auto_detected_device_ = detect_camera();
      if (auto_detected_device_) {
        video_device_ = auto_detected_device_->device_path;
      }
    }
    
    start_capture();
    
    response->success = cap_.isOpened();
    response->message = response->success ? "Camera reconnected successfully" : "Failed to reconnect camera";
    
    RCLCPP_INFO(this->get_logger(), "%s", response->message.c_str());
  }
  
  /**
   * @brief Publish status message.
   */
  void publish_status()
  {
    auto msg = std_msgs::msg::String();
    
    std::ostringstream ss;
    ss << "{";
    ss << "\"device\": \"" << video_device_ << "\", ";
    ss << "\"connected\": " << (cap_.isOpened() ? "true" : "false") << ", ";
    ss << "\"frames_published\": " << frames_published_.load() << ", ";
    ss << "\"frames_dropped\": " << frames_dropped_.load() << ", ";
    ss << "\"resolution\": \"" << image_width_ << "x" << image_height_ << "\"";
    ss << "}";
    
    msg.data = ss.str();
    status_pub_->publish(msg);
  }
};

}  // namespace lra_vision

// Register as component
RCLCPP_COMPONENTS_REGISTER_NODE(lra_vision::CameraPublisherNode)

// Main function for standalone execution
int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  
  auto node = std::make_shared<lra_vision::CameraPublisherNode>();
  
  rclcpp::executors::MultiThreadedExecutor executor;
  executor.add_node(node);
  
  executor.spin();
  
  rclcpp::shutdown();
  return 0;
}