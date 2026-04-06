#include <rclcpp/rclcpp.hpp>
#include <image_transport/image_transport.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/msg/camera_info.hpp>
#include <std_msgs/msg/bool.hpp>
#include "lra_vision/msg/calibration_status.hpp"
#include <std_srvs/srv/trigger.hpp>
#include <geometry_msgs/msg/point_stamped.hpp>

#include "lra_vision/srv/calibrate_camera.hpp"

#include <opencv2/opencv.hpp>
#include <cv_bridge/cv_bridge.h>

#include "lra_vision/camera_calibration.hpp"

#include <filesystem>
#include <sstream>
#include <iomanip>

namespace lra_vision
{

class CameraCalibratorNode : public rclcpp::Node
{
public:
  explicit CameraCalibratorNode(const rclcpp::NodeOptions& options = rclcpp::NodeOptions())
  : Node("camera_calibrator", options)
  {

    this->declare_parameter("board_width", 8);
    this->declare_parameter("board_height", 5);
    this->declare_parameter("square_size", 0.025);
    this->declare_parameter("min_images", 30);
    this->declare_parameter("max_images", 100);
    this->declare_parameter("auto_capture", true);
    this->declare_parameter("capture_interval", 1.0);
    this->declare_parameter("visualize", true);
    this->declare_parameter("save_path", "~/.ros/camera_calibration/");
    this->declare_parameter("camera_name", "logitech_streamcam");
    this->declare_parameter("image_topic", "/camera/image_raw");
    this->declare_parameter("output_file", "camera_info.yaml");


    CalibrationConfig config;
    config.board_width = this->get_parameter("board_width").as_int();
    config.board_height = this->get_parameter("board_height").as_int();
    config.square_size = this->get_parameter("square_size").as_double();
    config.min_images = this->get_parameter("min_images").as_int();
    config.max_images = this->get_parameter("max_images").as_int();
    config.auto_capture = this->get_parameter("auto_capture").as_bool();
    config.capture_interval = this->get_parameter("capture_interval").as_double();
    config.output_path = this->get_parameter("save_path").as_string();
    config.camera_name = this->get_parameter("camera_name").as_string();

    visualize_ = this->get_parameter("visualize").as_bool();
    image_topic_ = this->get_parameter("image_topic").as_string();
    output_file_ = this->get_parameter("output_file").as_string();


    calibrator_ = std::make_unique<CameraCalibrator>(config);


    image_sub_ = image_transport::create_subscription(
      this, image_topic_,
      std::bind(&CameraCalibratorNode::image_callback, this, std::placeholders::_1),
      "raw", rmw_qos_profile_sensor_data);


    debug_pub_ = image_transport::create_publisher(this, "calibration/debug");
    status_pub_ = this->create_publisher<lra_vision::msg::CalibrationStatus>("calibration/status", 10);
    ready_pub_ = this->create_publisher<std_msgs::msg::Bool>("calibration/ready", 10);


    capture_srv_ = this->create_service<std_srvs::srv::Trigger>(
      "capture",
      std::bind(&CameraCalibratorNode::handle_capture, this,
                std::placeholders::_1, std::placeholders::_2));

    calibrate_srv_ = this->create_service<std_srvs::srv::Trigger>(
      "calibrate",
      std::bind(&CameraCalibratorNode::handle_calibrate, this,
                std::placeholders::_1, std::placeholders::_2));

    save_srv_ = this->create_service<std_srvs::srv::Trigger>(
      "save",
      std::bind(&CameraCalibratorNode::handle_save, this,
                std::placeholders::_1, std::placeholders::_2));

    reset_srv_ = this->create_service<std_srvs::srv::Trigger>(
      "reset",
      std::bind(&CameraCalibratorNode::handle_reset, this,
                std::placeholders::_1, std::placeholders::_2));


    calibrate_camera_srv_ = this->create_service<lra_vision::srv::CalibrateCamera>(
      "calibrate_camera",
      std::bind(&CameraCalibratorNode::handle_calibrate_camera, this,
                std::placeholders::_1, std::placeholders::_2));


    status_timer_ = this->create_wall_timer(
      std::chrono::seconds(1),
      std::bind(&CameraCalibratorNode::publish_status, this));

    if (config.auto_capture) {
      capture_timer_ = this->create_wall_timer(
        std::chrono::milliseconds(static_cast<int>(config.capture_interval * 1000)),
        std::bind(&CameraCalibratorNode::auto_capture, this));
    }


    std::filesystem::path save_path(config.output_path);
    save_path = save_path.string();
    if (save_path.string().substr(0, 1) == "~") {
      const char* home = std::getenv("HOME");
      if (home) {
        save_path = std::string(home) + save_path.string().substr(1);
      }
    }

    try {
      std::filesystem::create_directories(save_path);
      save_path_ = save_path.string();
      RCLCPP_INFO(this->get_logger(), "Save path: %s", save_path_.c_str());
    } catch (const std::exception& e) {
      RCLCPP_ERROR(this->get_logger(), "Failed to create save directory: %s", e.what());
      save_path_ = "/tmp/camera_calibration";
    }

    RCLCPP_INFO(this->get_logger(), "Camera calibrator node initialized");
    RCLCPP_INFO(this->get_logger(), "Chessboard: %dx%d, square size: %.3fm",
                config.board_width, config.board_height, config.square_size);
    RCLCPP_INFO(this->get_logger(), "Min images: %d, Max images: %d",
                config.min_images, config.max_images);
    RCLCPP_INFO(this->get_logger(), "Subscribed to: %s", image_topic_.c_str());
  }

private:

  bool visualize_;
  std::string image_topic_;
  std::string output_file_;
  std::string save_path_;


  std::unique_ptr<CameraCalibrator> calibrator_;


  std::atomic<bool> capturing_{false};
  std::atomic<bool> last_pattern_found_{false};
  cv::Size last_image_size_;


  image_transport::Subscriber image_sub_;
  image_transport::Publisher debug_pub_;
  rclcpp::Publisher<lra_vision::msg::CalibrationStatus>::SharedPtr status_pub_;
  rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr ready_pub_;

  rclcpp::Service<lra_vision::srv::CalibrateCamera>::SharedPtr calibrate_camera_srv_;

  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr capture_srv_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr calibrate_srv_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr save_srv_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr reset_srv_;

  rclcpp::TimerBase::SharedPtr status_timer_;
  rclcpp::TimerBase::SharedPtr capture_timer_;


  rclcpp::Time last_capture_time_{0, 0, RCL_ROS_TIME};


  void image_callback(const sensor_msgs::msg::Image::ConstSharedPtr& msg)
  {
    try {

      cv_bridge::CvImagePtr cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
      cv::Mat image = cv_ptr->image;

      last_image_size_ = image.size();


      std::vector<cv::Point2f> corners;
      bool found = calibrator_->detect_chessboard(image, corners, false);
      last_pattern_found_ = found;


      if (found && capturing_.exchange(false)) {
        calibrator_->add_image(image, false);
      }


      if (visualize_ && debug_pub_.getNumSubscribers() > 0) {
        cv::Mat display = image.clone();

        if (found) {
          cv::drawChessboardCorners(
            display,
            cv::Size(calibrator_->get_config().board_width,
                     calibrator_->get_config().board_height),
            corners, found);
        }


        std::stringstream ss;
        ss << "Images: " << calibrator_->get_image_count()
           << "/" << calibrator_->get_config().min_images;
        cv::putText(display, ss.str(), cv::Point(10, 30),
                    cv::FONT_HERSHEY_SIMPLEX, 1.0, cv::Scalar(0, 255, 0), 2);

        if (calibrator_->has_sufficient_data()) {
          cv::putText(display, "Ready to calibrate!", cv::Point(10, 70),
                      cv::FONT_HERSHEY_SIMPLEX, 1.0, cv::Scalar(0, 255, 0), 2);
        }


        auto debug_msg = cv_bridge::CvImage(msg->header, "bgr8", display).toImageMsg();
        debug_pub_.publish(debug_msg);
      }

    } catch (const cv_bridge::Exception& e) {
      RCLCPP_ERROR(this->get_logger(), "CV Bridge error: %s", e.what());
    } catch (const std::exception& e) {
      RCLCPP_ERROR(this->get_logger(), "Error processing image: %s", e.what());
    }
  }


  void auto_capture()
  {
    if (!last_pattern_found_) {
      return;
    }

    if (calibrator_->get_image_count() >= static_cast<size_t>(calibrator_->get_config().max_images)) {
      return;
    }


    if (!capturing_) {
      capturing_ = true;
      RCLCPP_INFO(this->get_logger(), "Auto-capture triggered for next frame");
    }
  }


  void handle_capture(
    const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    (void)request;

    if (calibrator_->get_image_count() >= static_cast<size_t>(calibrator_->get_config().max_images)) {
      response->success = false;
      response->message = "Maximum images captured";
      return;
    }

    if (!last_pattern_found_) {
      response->success = false;
      response->message = "No pattern detected in last image";
      return;
    }


    capturing_ = true;

    response->success = true;
    response->message = "Capture triggered - processing...";

    RCLCPP_INFO(this->get_logger(), "Manual capture triggered, waiting for next frame with pattern");
  }


  void handle_calibrate(
    const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    (void)request;

    if (!calibrator_->has_sufficient_data()) {
      response->success = false;
      response->message = "Insufficient images: " + std::to_string(calibrator_->get_image_count()) +
                          "/" + std::to_string(calibrator_->get_config().min_images);
      RCLCPP_WARN(this->get_logger(), "%s", response->message.c_str());
      return;
    }

    RCLCPP_INFO(this->get_logger(), "Starting calibration with %zu images...",
                calibrator_->get_image_count());

    auto result = calibrator_->calibrate();

    if (result.success) {
      response->success = true;
      response->message = "Calibration successful";

      RCLCPP_INFO(this->get_logger(), "Calibration completed");

      calibration_utils::print_calibration_summary(result);
    } else {
      response->success = false;
      response->message = "Calibration failed";
      RCLCPP_ERROR(this->get_logger(), "Calibration failed!");
    }
  }


  void handle_save(
    const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    (void)request;

    if (!calibrator_->is_calibrated()) {
      response->success = false;
      response->message = "Not calibrated yet. Run calibrate service first.";
      RCLCPP_WARN(this->get_logger(), "%s", response->message.c_str());
      return;
    }

    std::string filepath = save_path_ + "/" + output_file_;

    if (calibrator_->save_calibration(filepath)) {
      response->success = true;
      response->message = "Calibration saved to: " + filepath;
      RCLCPP_INFO(this->get_logger(), "Calibration saved to: %s", filepath.c_str());
    } else {
      response->success = false;
      response->message = "Failed to save calibration";
      RCLCPP_ERROR(this->get_logger(), "Failed to save calibration to: %s", filepath.c_str());
    }
  }


  void handle_reset(
    const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    (void)request;

    calibrator_->clear();

    response->success = true;
    response->message = "Calibration data cleared";
    RCLCPP_INFO(this->get_logger(), "Calibration data cleared");
  }


  void handle_calibrate_camera(
    const std::shared_ptr<lra_vision::srv::CalibrateCamera::Request> request,
    std::shared_ptr<lra_vision::srv::CalibrateCamera::Response> response)
  {
    if (request->action == "start" || request->action == "reset") {
      calibrator_->clear();
      response->success = true;
      response->message = "Calibration data cleared and re-initialized";
      RCLCPP_INFO(this->get_logger(), "Calibrator reset via service");
    }
    else if (request->action == "capture") {
      if (calibrator_->get_image_count() >= static_cast<size_t>(calibrator_->get_config().max_images)) {
        response->success = false;
        response->message = "Maximum images captured";
        return;
      }

      if (!last_pattern_found_) {
        response->success = false;
        response->message = "No pattern detected in last image";
        return;
      }

      capturing_ = true;
      response->success = true;
      response->message = "Capture triggered - processing...";
      RCLCPP_INFO(this->get_logger(), "Capture triggered via service");
    }
    else if (request->action == "calibrate") {
      if (!calibrator_->has_sufficient_data()) {
        response->success = false;
        response->message = "Insufficient images: " + std::to_string(calibrator_->get_image_count()) +
                            "/" + std::to_string(calibrator_->get_config().min_images);
        return;
      }

      auto result = calibrator_->calibrate();
      response->success = result.success;
      response->message = result.success ? "Calibration successful" : "Calibration failed";
    }
    else if (request->action == "save") {
      if (!calibrator_->is_calibrated()) {
        response->success = false;
        response->message = "Not calibrated yet";
        return;
      }

      std::string filepath = save_path_ + "/" + output_file_;
      if (calibrator_->save_calibration(filepath)) {
        response->success = true;
        response->message = "Calibration saved to: " + filepath;
      } else {
        response->success = false;
        response->message = "Failed to save calibration";
      }
    }
    else {
      response->success = false;
      response->message = "Unknown action: " + request->action;
    }
  }


  void publish_status()
  {
    auto msg = lra_vision::msg::CalibrationStatus();
    msg.header.stamp = this->get_clock()->now();

    msg.images_collected = calibrator_->get_image_count();
    msg.images_required = calibrator_->get_config().min_images;
    msg.images_maximum = calibrator_->get_config().max_images;
    msg.is_ready = calibrator_->has_sufficient_data();
    msg.is_calibrated = calibrator_->is_calibrated();

    if (calibrator_->is_calibrated()) {
      msg.state = "calibrated";
    } else if (msg.is_ready) {
      msg.state = "ready";
    } else {
      msg.state = "collecting";
    }

    msg.progress = std::min(1.0, static_cast<double>(msg.images_collected) / msg.images_required);

    status_pub_->publish(msg);

    auto ready_msg = std_msgs::msg::Bool();
    ready_msg.data = msg.is_ready;
    ready_pub_->publish(ready_msg);
  }
};

}

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);

  auto node = std::make_shared<lra_vision::CameraCalibratorNode>();

  rclcpp::spin(node);

  rclcpp::shutdown();
  return 0;
}