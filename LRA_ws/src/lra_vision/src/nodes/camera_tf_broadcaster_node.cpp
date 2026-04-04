

#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <std_msgs/msg/string.hpp>
#include <std_srvs/srv/trigger.hpp>
#include <tf2_ros/transform_broadcaster.h>
#include <tf2_ros/static_transform_broadcaster.h>

#include "lra_vision/camera_tf_broadcaster.hpp"

#include <memory>
#include <functional>

namespace lra_vision
{

class CameraTfBroadcasterNode : public rclcpp::Node
{
public:
  explicit CameraTfBroadcasterNode(const rclcpp::NodeOptions& options = rclcpp::NodeOptions())
  : Node("camera_tf_broadcaster", options)
  {

    this->declare_parameter("translation_x", 0.0);
    this->declare_parameter("translation_y", 0.0);
    this->declare_parameter("translation_z", 0.05);
    this->declare_parameter("roll", 0.0);
    this->declare_parameter("pitch", 3.14159);
    this->declare_parameter("yaw", 0.0);
    this->declare_parameter("parent_frame", "tool0");
    this->declare_parameter("camera_frame", "camera_link");
    this->declare_parameter("optical_frame", "camera_optical_frame");
    this->declare_parameter("publish_rate", 30.0);
    this->declare_parameter("static_transform", true);
    this->declare_parameter("config_file", "");


    CameraMountConfig config;
    config.translation_x = this->get_parameter("translation_x").as_double();
    config.translation_y = this->get_parameter("translation_y").as_double();
    config.translation_z = this->get_parameter("translation_z").as_double();
    config.roll = this->get_parameter("roll").as_double();
    config.pitch = this->get_parameter("pitch").as_double();
    config.yaw = this->get_parameter("yaw").as_double();
    config.parent_frame = this->get_parameter("parent_frame").as_string();
    config.camera_frame = this->get_parameter("camera_frame").as_string();
    config.optical_frame = this->get_parameter("optical_frame").as_string();

    double publish_rate = this->get_parameter("publish_rate").as_double();
    bool static_transform = this->get_parameter("static_transform").as_bool();
    std::string config_file = this->get_parameter("config_file").as_string();


    if (!config_file.empty()) {
      try {
        config = CameraMountConfig::from_yaml(config_file);
        RCLCPP_INFO(this->get_logger(), "Loaded config from: %s", config_file.c_str());
      } catch (const std::exception& e) {
        RCLCPP_WARN(this->get_logger(), "Could not load config file: %s, using parameters", e.what());
      }
    }


    config_ = config;
    static_transform_ = static_transform;
    publish_rate_ = publish_rate;

    RCLCPP_INFO(this->get_logger(), "Camera TF broadcaster configured");
    RCLCPP_INFO(this->get_logger(), "Transform: %s -> %s -> %s",
                config.parent_frame.c_str(),
                config.camera_frame.c_str(),
                config.optical_frame.c_str());
    RCLCPP_INFO(this->get_logger(), "Translation: (%.3f, %.3f, %.3f) m",
                config.translation_x, config.translation_y, config.translation_z);
    RCLCPP_INFO(this->get_logger(), "Rotation (RPY): (%.3f, %.3f, %.3f) rad",
                config.roll, config.pitch, config.yaw);
  }


  void init()
  {

    tf_broadcaster_ = std::make_unique<CameraTfBroadcaster>(shared_from_this(), config_);


    status_pub_ = this->create_publisher<std_msgs::msg::String>("~/status", 10);


    update_srv_ = this->create_service<std_srvs::srv::Trigger>(
      "~/update",
      std::bind(&CameraTfBroadcasterNode::handle_update, this,
                std::placeholders::_1, std::placeholders::_2));


    tf_broadcaster_->initialize();


    if (!static_transform_) {
      timer_ = this->create_wall_timer(
        std::chrono::milliseconds(static_cast<int>(1000.0 / publish_rate_)),
        std::bind(&CameraTfBroadcasterNode::publish_transforms, this));
    }


    status_timer_ = this->create_wall_timer(
      std::chrono::seconds(5),
      std::bind(&CameraTfBroadcasterNode::publish_status, this));

    RCLCPP_INFO(this->get_logger(), "Camera TF broadcaster initialized");
  }

private:
  CameraMountConfig config_;
  bool static_transform_;
  double publish_rate_;
  std::unique_ptr<CameraTfBroadcaster> tf_broadcaster_;

  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr status_pub_;
  rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr update_srv_;
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::TimerBase::SharedPtr status_timer_;


  void publish_transforms()
  {
    tf_broadcaster_->update();
  }


  void handle_update(
    const std::shared_ptr<std_srvs::srv::Trigger::Request> request,
    std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    (void)request;


    config_.translation_x = this->get_parameter("translation_x").as_double();
    config_.translation_y = this->get_parameter("translation_y").as_double();
    config_.translation_z = this->get_parameter("translation_z").as_double();
    config_.roll = this->get_parameter("roll").as_double();
    config_.pitch = this->get_parameter("pitch").as_double();
    config_.yaw = this->get_parameter("yaw").as_double();
    config_.parent_frame = this->get_parameter("parent_frame").as_string();
    config_.camera_frame = this->get_parameter("camera_frame").as_string();
    config_.optical_frame = this->get_parameter("optical_frame").as_string();

    tf_broadcaster_->update_config(config_);

    response->success = true;
    response->message = "TF configuration updated";

    RCLCPP_INFO(this->get_logger(), "TF configuration updated");
    RCLCPP_INFO(this->get_logger(), "Transform: %s -> %s -> %s",
                config_.parent_frame.c_str(),
                config_.camera_frame.c_str(),
                config_.optical_frame.c_str());
  }


  void publish_status()
  {
    auto msg = std_msgs::msg::String();

    std::ostringstream ss;
    ss << "{";
    ss << "\"parent_frame\": \"" << config_.parent_frame << "\", ";
    ss << "\"camera_frame\": \"" << config_.camera_frame << "\", ";
    ss << "\"optical_frame\": \"" << config_.optical_frame << "\", ";
    ss << "\"translation\": ["
       << config_.translation_x << ", "
       << config_.translation_y << ", "
       << config_.translation_z << "], ";
    ss << "\"rotation_rpy\": ["
       << config_.roll << ", "
       << config_.pitch << ", "
       << config_.yaw << "]";
    ss << "}";

    msg.data = ss.str();
    status_pub_->publish(msg);
  }
};

}

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);

  auto node = std::make_shared<lra_vision::CameraTfBroadcasterNode>();


  node->init();

  rclcpp::spin(node);

  rclcpp::shutdown();
  return 0;
}