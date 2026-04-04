

#include "lra_vision/camera_detector.hpp"

#include <iostream>
#include <fstream>
#include <algorithm>
#include <regex>
#include <cstring>

namespace lra_vision
{

std::vector<std::string> CameraDetector::scan_video_devices()
{
  std::vector<std::string> devices;

  DIR* dir = opendir("/dev");
  if (!dir) {
    return devices;
  }

  struct dirent* entry;
  while ((entry = readdir(dir)) != nullptr) {
    std::string name(entry->d_name);


    if (name.substr(0, 5) == "video" && name.length() > 5) {

      bool is_numeric = std::all_of(name.begin() + 5, name.end(), ::isdigit);

      if (is_numeric) {
        devices.push_back("/dev/" + name);
      }
    }
  }
  closedir(dir);


  std::sort(devices.begin(), devices.end(), [](const std::string& a, const std::string& b) {

    int num_a = std::stoi(a.substr(10));
    int num_b = std::stoi(b.substr(10));
    return num_a < num_b;
  });

  return devices;
}

std::optional<CameraCapabilities> CameraDetector::query_capabilities(const std::string& device_path)
{
  int fd = open(device_path.c_str(), O_RDWR);
  if (fd < 0) {
    return std::nullopt;
  }

  CameraCapabilities caps;
  caps.device_path = device_path;


  struct v4l2_capability cap;
  if (ioctl(fd, VIDIOC_QUERYCAP, &cap) < 0) {
    close(fd);
    return std::nullopt;
  }

  caps.driver = reinterpret_cast<const char*>(cap.driver);
  caps.card = reinterpret_cast<const char*>(cap.card);
  caps.bus_info = reinterpret_cast<const char*>(cap.bus_info);
  caps.version = cap.version;


  caps.is_capture_device = (cap.capabilities & V4L2_CAP_VIDEO_CAPTURE) != 0;
  caps.is_output_device = (cap.capabilities & V4L2_CAP_VIDEO_OUTPUT) != 0;


  caps.formats = enumerate_formats(fd);
  caps.resolutions = enumerate_resolutions(fd);

  close(fd);
  return caps;
}

std::vector<std::string> CameraDetector::enumerate_formats(int fd)
{
  std::vector<std::string> formats;

  struct v4l2_fmtdesc fmtdesc;
  memset(&fmtdesc, 0, sizeof(fmtdesc));
  fmtdesc.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

  while (ioctl(fd, VIDIOC_ENUM_FMT, &fmtdesc) == 0) {
    formats.push_back(reinterpret_cast<const char*>(fmtdesc.description));
    fmtdesc.index++;
  }

  return formats;
}

std::vector<std::pair<int, int>> CameraDetector::enumerate_resolutions(int fd)
{
  std::vector<std::pair<int, int>> resolutions;

  struct v4l2_fmtdesc fmtdesc;
  memset(&fmtdesc, 0, sizeof(fmtdesc));
  fmtdesc.type = V4L2_BUF_TYPE_VIDEO_CAPTURE;

  while (ioctl(fd, VIDIOC_ENUM_FMT, &fmtdesc) == 0) {
    struct v4l2_frmsizeenum fsize;
    memset(&fsize, 0, sizeof(fsize));
    fsize.pixel_format = fmtdesc.pixelformat;

    while (ioctl(fd, VIDIOC_ENUM_FRAMESIZES, &fsize) == 0) {
      if (fsize.type == V4L2_FRMSIZE_TYPE_DISCRETE) {
        resolutions.emplace_back(fsize.discrete.width, fsize.discrete.height);
      }
      fsize.index++;
    }

    fmtdesc.index++;
  }


  std::sort(resolutions.begin(), resolutions.end());
  resolutions.erase(std::unique(resolutions.begin(), resolutions.end()), resolutions.end());

  return resolutions;
}

std::vector<CameraInfo> CameraDetector::detect_all_cameras()
{
  std::vector<CameraInfo> cameras;

  auto device_paths = scan_video_devices();
  for (const auto& path : device_paths) {
    auto caps = query_capabilities(path);
    if (caps && caps->is_capture_device) {
      CameraInfo info;
      info.device_path = path;
      info.camera_name = caps->card;
      info.capabilities = *caps;
      info.is_streamcam = (caps->card.find("StreamCam") != std::string::npos ||
                           caps->card.find("Logitech") != std::string::npos);
      cameras.push_back(info);
    }
  }

  return cameras;
}

std::optional<CameraInfo> CameraDetector::find_camera_by_name(const std::string& name_pattern)
{
  auto cameras = detect_all_cameras();

  std::string pattern_lower = name_pattern;
  std::transform(pattern_lower.begin(), pattern_lower.end(), pattern_lower.begin(), ::tolower);

  for (const auto& cam : cameras) {
    std::string name_lower = cam.camera_name;
    std::transform(name_lower.begin(), name_lower.end(), name_lower.begin(), ::tolower);

    if (name_lower.find(pattern_lower) != std::string::npos) {
      return cam;
    }
  }

  return std::nullopt;
}

std::optional<CameraInfo> CameraDetector::find_streamcam()
{

  auto streamcam = find_camera_by_name("Logitech");
  if (streamcam) {
    return streamcam;
  }

  return std::nullopt;
}

std::optional<CameraInfo> CameraDetector::get_camera_info(const std::string& device_path)
{
  auto caps = query_capabilities(device_path);
  if (!caps) {
    return std::nullopt;
  }

  CameraInfo info;
  info.device_path = device_path;
  info.camera_name = caps->card;
  info.capabilities = *caps;
  info.is_streamcam = (caps->card.find("StreamCam") != std::string::npos ||
                       caps->card.find("Logitech") != std::string::npos);

  return info;
}

bool CameraDetector::is_valid_camera_device(const std::string& device_path)
{
  auto caps = query_capabilities(device_path);
  return caps.has_value() && caps->is_capture_device;
}

std::optional<CameraInfo> CameraDetector::get_first_capture_device()
{
  auto cameras = get_capture_devices();
  if (cameras.empty()) {
    return std::nullopt;
  }
  return cameras[0];
}

std::vector<CameraInfo> CameraDetector::get_capture_devices()
{
  std::vector<CameraInfo> capture_devices;

  auto cameras = detect_all_cameras();
  for (const auto& cam : cameras) {
    if (cam.capabilities.is_capture_device) {
      capture_devices.push_back(cam);
    }
  }

  return capture_devices;
}

}