// =============================================================================
// LRA Vision Package - ArUco Detector Node
// ArUco marker detection for hand-eye calibration
// ROS2 Jazzy Jalisco - C++17
// =============================================================================

#include <rclcpp/rclcpp.hpp>
#include <image_transport/image_transport.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/msg/camera_info.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/pose_array.hpp>
#include <visualization_msgs/msg/marker_array.hpp>
#include <std_msgs/msg/int32_multi_array.hpp>
#include <cv_bridge/cv_bridge.hpp>
#include <tf2/LinearMath/Matrix3x3.h>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2/convert.h>

#include <opencv2/opencv.hpp>
#include <opencv2/aruco.hpp>

#include "lra_vision/aruco_detector.hpp"

#include <memory>
#include <vector>

namespace lra_vision
{

/**
 * @class ArUcoDetectorNode
 * @brief ROS2 node for ArUco marker detection and pose estimation.
 * 
 * This node provides:
 * - ArUco marker detection from camera images
 * - Marker pose estimation using camera calibration
 * - Visualization of detected markers
 * - Support for multiple marker dictionaries
 */
class ArUcoDetectorNode : public rclcpp::Node
{
public:
  explicit ArUcoDetectorNode(const rclcpp::NodeOptions& options = rclcpp::NodeOptions())
  : Node("aruco_detector", options)
  {
    // Declare parameters
    this->declare_parameter("dictionary", "DICT_4X4_50");
    this->declare_parameter("marker_size", 0.05);
    this->declare_parameter("image_topic", "camera/image_raw");
    this->declare_parameter("camera_info_topic", "camera/camera_info");
    this->declare_parameter("publish_markers", true);
    this->declare_parameter("publish_poses", true);
    this->declare_parameter("publish_image", true);
    this->declare_parameter("calibration_file", "");
    
    // Get parameters
    std::string dictionary_name = this->get_parameter("dictionary").as_string();
    double marker_size = this->get_parameter("marker_size").as_double();
    image_topic_ = this->get_parameter("image_topic").as_string();
    camera_info_topic_ = this->get_parameter("camera_info_topic").as_string();
    publish_markers_ = this->get_parameter("publish_markers").as_bool();
    publish_poses_ = this->get_parameter("publish_poses").as_bool();
    publish_image_ = this->get_parameter("publish_image").as_bool();
    calibration_file_ = this->get_parameter("calibration_file").as_string();
    
    // Parse dictionary
    cv::aruco::PREDEFINED_DICTIONARY_NAME dictionary = parse_dictionary(dictionary_name);
    
    // Initialize detector
    ArucoConfig config = ArucoConfig::default_config();
    config.dictionary = dictionary;
    config.marker_size = marker_size;
    detector_ = std::make_unique<ArucoDetector>(config);
    
    // Load calibration if provided
    if (!calibration_file_.empty()) {
      if (detector_->load_camera_calibration(calibration_file_)) {
        RCLCPP_INFO(this->get_logger(), "Loaded camera calibration from: %s", calibration_file_.c_str());
      } else {
        RCLCPP_WARN(this->get_logger(), "Failed to load calibration from: %s", calibration_file_.c_str());
      }
    }
    
    // Subscribe to image topic
    image_sub_ = image_transport::create_subscription(
      this, image_topic_,
      std::bind(&ArUcoDetectorNode::image_callback, this, std::placeholders::_1),
      "raw");
    
    // Subscribe to camera info
    camera_info_sub_ = this->create_subscription<sensor_msgs::msg::CameraInfo>(
      camera_info_topic_, rclcpp::SensorDataQoS(),
      std::bind(&ArUcoDetectorNode::camera_info_callback, this, std::placeholders::_1));
    
    // Publishers
    if (publish_image_) {
      image_pub_ = image_transport::create_publisher(this, "aruco/detected_image");
    }
    
    if (publish_markers_) {
      marker_pub_ = this->create_publisher<visualization_msgs::msg::MarkerArray>(
        "aruco/markers", 10);
    }
    
    if (publish_poses_) {
      pose_pub_ = this->create_publisher<geometry_msgs::msg::PoseArray>(
        "aruco/poses", 10);
      
      pose_stamped_pub_ = this->create_publisher<geometry_msgs::msg::PoseStamped>(
        "aruco/pose_stamped", 10);
    }
    
    id_pub_ = this->create_publisher<std_msgs::msg::Int32MultiArray>(
      "aruco/marker_ids", 10);
    
    RCLCPP_INFO(this->get_logger(), "ArUco detector initialized");
    RCLCPP_INFO(this->get_logger(), "Dictionary: %s", dictionary_name.c_str());
    RCLCPP_INFO(this->get_logger(), "Marker size: %.3f m", marker_size);
    RCLCPP_INFO(this->get_logger(), "Subscribed to: %s", image_topic_.c_str());
  }

private:
  // Parameters
  std::string image_topic_;
  std::string camera_info_topic_;
  std::string calibration_file_;
  bool publish_markers_;
  bool publish_poses_;
  bool publish_image_;
  
  // Detector
  std::unique_ptr<ArucoDetector> detector_;
  
  // Camera info
  bool has_camera_info_ = false;
  cv::Mat camera_matrix_;
  cv::Mat dist_coeffs_;
  
  // Frame ID
  std::string frame_id_ = "camera_optical_frame";
  
  // ROS2 components
  image_transport::Subscriber image_sub_;
  image_transport::Publisher image_pub_;
  rclcpp::Subscription<sensor_msgs::msg::CameraInfo>::SharedPtr camera_info_sub_;
  
  rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr marker_pub_;
  rclcpp::Publisher<geometry_msgs::msg::PoseArray>::SharedPtr pose_pub_;
  rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr pose_stamped_pub_;
  rclcpp::Publisher<std_msgs::msg::Int32MultiArray>::SharedPtr id_pub_;
  
  /**
   * @brief Parse dictionary name string.
   */
  cv::aruco::PREDEFINED_DICTIONARY_NAME parse_dictionary(const std::string& name)
  {
    if (name == "DICT_4X4_50") return cv::aruco::DICT_4X4_50;
    if (name == "DICT_4X4_100") return cv::aruco::DICT_4X4_100;
    if (name == "DICT_4X4_250") return cv::aruco::DICT_4X4_250;
    if (name == "DICT_4X4_1000") return cv::aruco::DICT_4X4_1000;
    if (name == "DICT_5X5_50") return cv::aruco::DICT_5X5_50;
    if (name == "DICT_5X5_100") return cv::aruco::DICT_5X5_100;
    if (name == "DICT_5X5_250") return cv::aruco::DICT_5X5_250;
    if (name == "DICT_5X5_1000") return cv::aruco::DICT_5X5_1000;
    if (name == "DICT_6X6_50") return cv::aruco::DICT_6X6_50;
    if (name == "DICT_6X6_100") return cv::aruco::DICT_6X6_100;
    if (name == "DICT_6X6_250") return cv::aruco::DICT_6X6_250;
    if (name == "DICT_6X6_1000") return cv::aruco::DICT_6X6_1000;
    if (name == "DICT_7X7_50") return cv::aruco::DICT_7X7_50;
    if (name == "DICT_7X7_100") return cv::aruco::DICT_7X7_100;
    if (name == "DICT_7X7_250") return cv::aruco::DICT_7X7_250;
    if (name == "DICT_7X7_1000") return cv::aruco::DICT_7X7_1000;
    if (name == "DICT_ARUCO_ORIGINAL") return cv::aruco::DICT_ARUCO_ORIGINAL;
    if (name == "DICT_APRILTAG_16h5") return cv::aruco::DICT_APRILTAG_16h5;
    if (name == "DICT_APRILTAG_25h9") return cv::aruco::DICT_APRILTAG_25h9;
    if (name == "DICT_APRILTAG_36h10") return cv::aruco::DICT_APRILTAG_36h10;
    if (name == "DICT_APRILTAG_36h11") return cv::aruco::DICT_APRILTAG_36h11;
    
    RCLCPP_WARN(this->get_logger(), "Unknown dictionary: %s, using DICT_4X4_50", name.c_str());
    return cv::aruco::DICT_4X4_50;
  }
  
  /**
   * @brief Camera info callback.
   */
  void camera_info_callback(const sensor_msgs::msg::CameraInfo::SharedPtr msg)
  {
    if (has_camera_info_) {
      return;  // Already have camera info
    }
    
    frame_id_ = msg->header.frame_id;
    
    // Extract camera matrix
    camera_matrix_ = cv::Mat(3, 3, CV_64F);
    for (int i = 0; i < 9; ++i) {
      camera_matrix_.at<double>(i / 3, i % 3) = msg->k[i];
    }
    
    // Extract distortion coefficients
    dist_coeffs_ = cv::Mat(msg->d.size(), 1, CV_64F);
    for (size_t i = 0; i < msg->d.size(); ++i) {
      dist_coeffs_.at<double>(i, 0) = msg->d[i];
    }
    
    detector_->set_camera_matrix(camera_matrix_, dist_coeffs_);
    has_camera_info_ = true;
    
    RCLCPP_INFO(this->get_logger(), "Received camera info");
  }
  
  /**
   * @brief Image callback.
   */
  void image_callback(const sensor_msgs::msg::Image::ConstSharedPtr& msg)
  {
    try {
      // Convert to OpenCV
      cv_bridge::CvImagePtr cv_ptr = cv_bridge::toCvCopy(msg, sensor_msgs::image_encodings::BGR8);
      cv::Mat image = cv_ptr->image;
      
      // Detect markers
      std::vector<ArucoMarker> markers;
      
      if (has_camera_info_ || detector_->has_camera_calibration()) {
        markers = detector_->detect_with_pose(image);
      } else {
        markers = detector_->detect(image);
      }
      
      // Publish detected image
      if (publish_image_ && image_pub_.getNumSubscribers() > 0) {
        cv::Mat detected_image = image.clone();
        detector_->draw_markers(detected_image, markers, true, true);
        
        auto detected_msg = cv_bridge::CvImage(msg->header, "bgr8", detected_image).toImageMsg();
        image_pub_.publish(detected_msg);
      }
      
      // Publish markers
      if (publish_markers_ && marker_pub_->get_subscription_count() > 0) {
        publish_marker_array(msg->header, markers);
      }
      
      // Publish poses
      if (publish_poses_ && pose_pub_->get_subscription_count() > 0) {
        publish_pose_array(msg->header, markers);
      }
      
      // Publish IDs
      if (id_pub_->get_subscription_count() > 0) {
        publish_marker_ids(msg->header, markers);
      }
      
    } catch (const cv_bridge::Exception& e) {
      RCLCPP_ERROR(this->get_logger(), "CV Bridge error: %s", e.what());
    } catch (const std::exception& e) {
      RCLCPP_ERROR(this->get_logger(), "Error processing image: %s", e.what());
    }
  }
  
  /**
   * @brief Publish marker visualization.
   */
  void publish_marker_array(
    const std_msgs::msg::Header& header,
    const std::vector<ArucoMarker>& markers)
  {
    visualization_msgs::msg::MarkerArray marker_array;
    
    for (size_t i = 0; i < markers.size(); ++i) {
      const auto& marker = markers[i];
      
      // Marker cube
      visualization_msgs::msg::Marker cube;
      cube.header = header;
      cube.ns = "aruco_markers";
      cube.id = marker.id;
      cube.type = visualization_msgs::msg::Marker::CUBE;
      cube.action = visualization_msgs::msg::Marker::ADD;
      cube.pose.position.x = marker.tvec[0];
      cube.pose.position.y = marker.tvec[1];
      cube.pose.position.z = marker.tvec[2];
      
      cv::Mat R;
      cv::Rodrigues(marker.rvec, R);
      tf2::Matrix3x3 tf_R(
        R.at<double>(0, 0), R.at<double>(0, 1), R.at<double>(0, 2),
        R.at<double>(1, 0), R.at<double>(1, 1), R.at<double>(1, 2),
        R.at<double>(2, 0), R.at<double>(2, 1), R.at<double>(2, 2)
      );
      tf2::Quaternion q;
      tf_R.getRotation(q);
      
      cube.pose.orientation.x = q.x();
      cube.pose.orientation.y = q.y();
      cube.pose.orientation.z = q.z();
      cube.pose.orientation.w = q.w();
      
      double marker_size = detector_->get_config().marker_size;
      cube.scale.x = marker_size;
      cube.scale.y = marker_size;
      cube.scale.z = marker_size * 0.1;  // Thin cube
      
      cube.color.r = 0.0f;
      cube.color.g = 1.0f;
      cube.color.b = 0.0f;
      cube.color.a = 0.8f;
      
      marker_array.markers.push_back(cube);
      
      // Text label
      visualization_msgs::msg::Marker text;
      text.header = header;
      text.ns = "aruco_labels";
      text.id = marker.id + 10000;
      text.type = visualization_msgs::msg::Marker::TEXT_VIEW_FACING;
      text.action = visualization_msgs::msg::Marker::ADD;
      text.pose.position.x = marker.tvec[0];
      text.pose.position.y = marker.tvec[1];
      text.pose.position.z = marker.tvec[2] + marker_size;
      text.pose.orientation.w = 1.0;
      text.scale.z = marker_size * 0.5;
      text.color.r = 1.0f;
      text.color.g = 1.0f;
      text.color.b = 1.0f;
      text.color.a = 1.0f;
      text.text = std::to_string(marker.id);
      
      marker_array.markers.push_back(text);
    }
    
    marker_pub_->publish(marker_array);
  }
  
  /**
   * @brief Publish pose array.
   */
  void publish_pose_array(
    const std_msgs::msg::Header& header,
    const std::vector<ArucoMarker>& markers)
  {
    geometry_msgs::msg::PoseArray pose_array;
    pose_array.header = header;
    
    for (const auto& marker : markers) {
      geometry_msgs::msg::Pose pose;
      pose.position.x = marker.tvec[0];
      pose.position.y = marker.tvec[1];
      pose.position.z = marker.tvec[2];
      
      cv::Mat R;
      cv::Rodrigues(marker.rvec, R);
      tf2::Matrix3x3 tf_R(
        R.at<double>(0, 0), R.at<double>(0, 1), R.at<double>(0, 2),
        R.at<double>(1, 0), R.at<double>(1, 1), R.at<double>(1, 2),
        R.at<double>(2, 0), R.at<double>(2, 1), R.at<double>(2, 2)
      );
      tf2::Quaternion q;
      tf_R.getRotation(q);
      
      pose.orientation.x = q.x();
      pose.orientation.y = q.y();
      pose.orientation.z = q.z();
      pose.orientation.w = q.w();
      
      pose_array.poses.push_back(pose);
    }
    
    pose_pub_->publish(pose_array);
  }
  
  /**
   * @brief Publish marker IDs.
   */
  void publish_marker_ids(
    const std_msgs::msg::Header& header,
    const std::vector<ArucoMarker>& markers)
  {
    std_msgs::msg::Int32MultiArray ids_msg;
    ids_msg.layout.dim.push_back(std_msgs::msg::MultiArrayDimension());
    ids_msg.layout.dim[0].label = "marker_ids";
    ids_msg.layout.dim[0].size = markers.size();
    ids_msg.layout.dim[0].stride = markers.size();
    
    for (const auto& marker : markers) {
      ids_msg.data.push_back(marker.id);
    }
    
    id_pub_->publish(ids_msg);
  }
};

}  // namespace lra_vision

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  
  auto node = std::make_shared<lra_vision::ArUcoDetectorNode>();
  
  rclcpp::spin(node);
  
  rclcpp::shutdown();
  return 0;
}