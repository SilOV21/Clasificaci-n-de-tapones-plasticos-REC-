// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from lra_vision:msg/CalibrationStatus.idl
// generated code does not contain a copyright notice

#ifndef LRA_VISION__MSG__DETAIL__CALIBRATION_STATUS__TRAITS_HPP_
#define LRA_VISION__MSG__DETAIL__CALIBRATION_STATUS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "lra_vision/msg/detail/calibration_status__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace lra_vision
{

namespace msg
{

inline void to_flow_style_yaml(
  const CalibrationStatus & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: state
  {
    out << "state: ";
    rosidl_generator_traits::value_to_yaml(msg.state, out);
    out << ", ";
  }

  // member: images_collected
  {
    out << "images_collected: ";
    rosidl_generator_traits::value_to_yaml(msg.images_collected, out);
    out << ", ";
  }

  // member: images_required
  {
    out << "images_required: ";
    rosidl_generator_traits::value_to_yaml(msg.images_required, out);
    out << ", ";
  }

  // member: images_maximum
  {
    out << "images_maximum: ";
    rosidl_generator_traits::value_to_yaml(msg.images_maximum, out);
    out << ", ";
  }

  // member: current_rms_error
  {
    out << "current_rms_error: ";
    rosidl_generator_traits::value_to_yaml(msg.current_rms_error, out);
    out << ", ";
  }

  // member: best_rms_error
  {
    out << "best_rms_error: ";
    rosidl_generator_traits::value_to_yaml(msg.best_rms_error, out);
    out << ", ";
  }

  // member: mean_reprojection_error
  {
    out << "mean_reprojection_error: ";
    rosidl_generator_traits::value_to_yaml(msg.mean_reprojection_error, out);
    out << ", ";
  }

  // member: is_ready
  {
    out << "is_ready: ";
    rosidl_generator_traits::value_to_yaml(msg.is_ready, out);
    out << ", ";
  }

  // member: is_calibrated
  {
    out << "is_calibrated: ";
    rosidl_generator_traits::value_to_yaml(msg.is_calibrated, out);
    out << ", ";
  }

  // member: error_message
  {
    out << "error_message: ";
    rosidl_generator_traits::value_to_yaml(msg.error_message, out);
    out << ", ";
  }

  // member: progress
  {
    out << "progress: ";
    rosidl_generator_traits::value_to_yaml(msg.progress, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const CalibrationStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: state
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "state: ";
    rosidl_generator_traits::value_to_yaml(msg.state, out);
    out << "\n";
  }

  // member: images_collected
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "images_collected: ";
    rosidl_generator_traits::value_to_yaml(msg.images_collected, out);
    out << "\n";
  }

  // member: images_required
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "images_required: ";
    rosidl_generator_traits::value_to_yaml(msg.images_required, out);
    out << "\n";
  }

  // member: images_maximum
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "images_maximum: ";
    rosidl_generator_traits::value_to_yaml(msg.images_maximum, out);
    out << "\n";
  }

  // member: current_rms_error
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "current_rms_error: ";
    rosidl_generator_traits::value_to_yaml(msg.current_rms_error, out);
    out << "\n";
  }

  // member: best_rms_error
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "best_rms_error: ";
    rosidl_generator_traits::value_to_yaml(msg.best_rms_error, out);
    out << "\n";
  }

  // member: mean_reprojection_error
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mean_reprojection_error: ";
    rosidl_generator_traits::value_to_yaml(msg.mean_reprojection_error, out);
    out << "\n";
  }

  // member: is_ready
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "is_ready: ";
    rosidl_generator_traits::value_to_yaml(msg.is_ready, out);
    out << "\n";
  }

  // member: is_calibrated
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "is_calibrated: ";
    rosidl_generator_traits::value_to_yaml(msg.is_calibrated, out);
    out << "\n";
  }

  // member: error_message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "error_message: ";
    rosidl_generator_traits::value_to_yaml(msg.error_message, out);
    out << "\n";
  }

  // member: progress
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "progress: ";
    rosidl_generator_traits::value_to_yaml(msg.progress, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const CalibrationStatus & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace lra_vision

namespace rosidl_generator_traits
{

[[deprecated("use lra_vision::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const lra_vision::msg::CalibrationStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  lra_vision::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use lra_vision::msg::to_yaml() instead")]]
inline std::string to_yaml(const lra_vision::msg::CalibrationStatus & msg)
{
  return lra_vision::msg::to_yaml(msg);
}

template<>
inline const char * data_type<lra_vision::msg::CalibrationStatus>()
{
  return "lra_vision::msg::CalibrationStatus";
}

template<>
inline const char * name<lra_vision::msg::CalibrationStatus>()
{
  return "lra_vision/msg/CalibrationStatus";
}

template<>
struct has_fixed_size<lra_vision::msg::CalibrationStatus>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<lra_vision::msg::CalibrationStatus>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<lra_vision::msg::CalibrationStatus>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // LRA_VISION__MSG__DETAIL__CALIBRATION_STATUS__TRAITS_HPP_
