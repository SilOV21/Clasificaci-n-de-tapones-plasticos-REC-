// =============================================================================
// LRA Vision Package - Camera Detector
// Auto-detection of V4L2 camera devices
// ROS2 Jazzy Jalisco - C++17
// =============================================================================
/**
 * @file camera_detector.hpp
 * @brief Auto-detection of V4L2 camera devices for the LRA Vision package.
 * 
 * This module provides functionality to automatically detect and identify
 * V4L2 camera devices connected to the system. It scans /dev/video* devices
 * and queries their capabilities using v4l2 API.
 * 
 * @author Dr. Asil
 * @date March 2026
 * @copyright MIT License
 */

#ifndef LRA_VISION__CAMERA_DETECTOR_HPP_
#define LRA_VISION__CAMERA_DETECTOR_HPP_

#include <string>
#include <vector>
#include <optional>
#include <memory>

// Linux V4L2 headers
#include <linux/videodev2.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <dirent.h>

namespace lra_vision
{

/**
 * @struct CameraCapabilities
 * @brief Describes the capabilities of a detected camera device.
 */
struct CameraCapabilities
{
  std::string device_path;          ///< Device path (e.g., /dev/video0)
  std::string driver;               ///< Driver name
  std::string card;                 ///< Card/device name
  std::string bus_info;             ///< Bus information
  uint32_t version;                 ///< Driver version
  std::vector<std::string> formats; ///< Supported pixel formats
  std::vector<std::pair<int, int>> resolutions; ///< Supported resolutions
  bool is_capture_device;           ///< True if device supports video capture
  bool is_output_device;            ///< True if device supports video output
};

/**
 * @struct CameraInfo
 * @brief Complete information about a detected camera.
 */
struct CameraInfo
{
  std::string device_path;
  std::string camera_name;
  CameraCapabilities capabilities;
  bool is_streamcam;                ///< True if this is a Logitech StreamCam
};

/**
 * @class CameraDetector
 * @brief Automatically detects V4L2 camera devices on the system.
 * 
 * This class provides static methods to scan the system for connected
 * V4L2 camera devices and query their capabilities. It can specifically
 * identify Logitech StreamCam devices for the REC project.
 * 
 * @example
 * @code
 * auto cameras = CameraDetector::detect_all_cameras();
 * for (const auto& cam : cameras) {
 *   std::cout << cam.device_path << ": " << cam.camera_name << std::endl;
 * }
 * 
 * auto streamcam = CameraDetector::find_streamcam();
 * if (streamcam) {
 *   std::cout << "StreamCam found at: " << streamcam->device_path << std::endl;
 * }
 * @endcode
 */
class CameraDetector
{
public:
  /**
   * @brief Detect all V4L2 camera devices connected to the system.
   * @return Vector of CameraInfo structures for each detected camera.
   */
  static std::vector<CameraInfo> detect_all_cameras();

  /**
   * @brief Find a specific camera by device name pattern.
   * @param name_pattern Pattern to match against camera name (case-insensitive).
   * @return Optional CameraInfo if found.
   */
  static std::optional<CameraInfo> find_camera_by_name(const std::string& name_pattern);

  /**
   * @brief Find the Logitech StreamCam device.
   * @return Optional CameraInfo if StreamCam is found.
   */
  static std::optional<CameraInfo> find_streamcam();

  /**
   * @brief Find camera by device path.
   * @param device_path Device path to check (e.g., /dev/video2).
   * @return Optional CameraInfo if device exists and is a valid camera.
   */
  static std::optional<CameraInfo> get_camera_info(const std::string& device_path);

  /**
   * @brief Check if a device path exists and is a valid V4L2 device.
   * @param device_path Device path to check.
   * @return True if the device is a valid V4L2 capture device.
   */
  static bool is_valid_camera_device(const std::string& device_path);

  /**
   * @brief Get the first available capture device.
   * @return Optional CameraInfo of the first available capture device.
   */
  static std::optional<CameraInfo> get_first_capture_device();

  /**
   * @brief Get all available capture devices.
   * @return Vector of CameraInfo for all capture-capable devices.
   */
  static std::vector<CameraInfo> get_capture_devices();

private:
  /**
   * @brief Query V4L2 capabilities for a device.
   * @param device_path Device path to query.
   * @return Optional CameraCapabilities if successful.
   */
  static std::optional<CameraCapabilities> query_capabilities(const std::string& device_path);

  /**
   * @brief Enumerate supported pixel formats for a device.
   * @param fd File descriptor of the open device.
   * @return Vector of format names (e.g., "YUYV", "MJPG", "RGB3").
   */
  static std::vector<std::string> enumerate_formats(int fd);

  /**
   * @brief Enumerate supported resolutions for a device.
   * @param fd File descriptor of the open device.
   * @return Vector of (width, height) pairs.
   */
  static std::vector<std::pair<int, int>> enumerate_resolutions(int fd);

  /**
   * @brief Scan /dev for video devices.
   * @return Vector of device paths found.
   */
  static std::vector<std::string> scan_video_devices();
};

}  // namespace lra_vision

#endif  // LRA_VISION__CAMERA_DETECTOR_HPP_