

#ifndef LRA_VISION__CAMERA_DETECTOR_HPP_
#define LRA_VISION__CAMERA_DETECTOR_HPP_

#include <string>
#include <vector>
#include <optional>
#include <memory>

#include <linux/videodev2.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <dirent.h>

namespace lra_vision
{

struct CameraCapabilities
{
  std::string device_path;
  std::string driver;
  std::string card;
  std::string bus_info;
  uint32_t version;
  std::vector<std::string> formats;
  std::vector<std::pair<int, int>> resolutions;
  bool is_capture_device;
  bool is_output_device;
};

struct CameraInfo
{
  std::string device_path;
  std::string camera_name;
  CameraCapabilities capabilities;
  bool is_streamcam;
};

class CameraDetector
{
public:

  static std::vector<CameraInfo> detect_all_cameras();


  static std::optional<CameraInfo> find_camera_by_name(const std::string& name_pattern);


  static std::optional<CameraInfo> find_streamcam();


  static std::optional<CameraInfo> get_camera_info(const std::string& device_path);


  static bool is_valid_camera_device(const std::string& device_path);


  static std::optional<CameraInfo> get_first_capture_device();


  static std::vector<CameraInfo> get_capture_devices();

private:

  static std::optional<CameraCapabilities> query_capabilities(const std::string& device_path);


  static std::vector<std::string> enumerate_formats(int fd);


  static std::vector<std::pair<int, int>> enumerate_resolutions(int fd);


  static std::vector<std::string> scan_video_devices();
};

}

#endif