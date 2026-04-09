// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from lra_vision:srv/CalibrateCamera.idl
// generated code does not contain a copyright notice

#ifndef LRA_VISION__SRV__DETAIL__CALIBRATE_CAMERA__TRAITS_HPP_
#define LRA_VISION__SRV__DETAIL__CALIBRATE_CAMERA__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "lra_vision/srv/detail/calibrate_camera__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace lra_vision
{

namespace srv
{

inline void to_flow_style_yaml(
  const CalibrateCamera_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: action
  {
    out << "action: ";
    rosidl_generator_traits::value_to_yaml(msg.action, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const CalibrateCamera_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: action
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "action: ";
    rosidl_generator_traits::value_to_yaml(msg.action, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const CalibrateCamera_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace lra_vision

namespace rosidl_generator_traits
{

[[deprecated("use lra_vision::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const lra_vision::srv::CalibrateCamera_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  lra_vision::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use lra_vision::srv::to_yaml() instead")]]
inline std::string to_yaml(const lra_vision::srv::CalibrateCamera_Request & msg)
{
  return lra_vision::srv::to_yaml(msg);
}

template<>
inline const char * data_type<lra_vision::srv::CalibrateCamera_Request>()
{
  return "lra_vision::srv::CalibrateCamera_Request";
}

template<>
inline const char * name<lra_vision::srv::CalibrateCamera_Request>()
{
  return "lra_vision/srv/CalibrateCamera_Request";
}

template<>
struct has_fixed_size<lra_vision::srv::CalibrateCamera_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<lra_vision::srv::CalibrateCamera_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<lra_vision::srv::CalibrateCamera_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace lra_vision
{

namespace srv
{

inline void to_flow_style_yaml(
  const CalibrateCamera_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: message
  {
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const CalibrateCamera_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << "\n";
  }

  // member: message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const CalibrateCamera_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace lra_vision

namespace rosidl_generator_traits
{

[[deprecated("use lra_vision::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const lra_vision::srv::CalibrateCamera_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  lra_vision::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use lra_vision::srv::to_yaml() instead")]]
inline std::string to_yaml(const lra_vision::srv::CalibrateCamera_Response & msg)
{
  return lra_vision::srv::to_yaml(msg);
}

template<>
inline const char * data_type<lra_vision::srv::CalibrateCamera_Response>()
{
  return "lra_vision::srv::CalibrateCamera_Response";
}

template<>
inline const char * name<lra_vision::srv::CalibrateCamera_Response>()
{
  return "lra_vision/srv/CalibrateCamera_Response";
}

template<>
struct has_fixed_size<lra_vision::srv::CalibrateCamera_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<lra_vision::srv::CalibrateCamera_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<lra_vision::srv::CalibrateCamera_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<lra_vision::srv::CalibrateCamera>()
{
  return "lra_vision::srv::CalibrateCamera";
}

template<>
inline const char * name<lra_vision::srv::CalibrateCamera>()
{
  return "lra_vision/srv/CalibrateCamera";
}

template<>
struct has_fixed_size<lra_vision::srv::CalibrateCamera>
  : std::integral_constant<
    bool,
    has_fixed_size<lra_vision::srv::CalibrateCamera_Request>::value &&
    has_fixed_size<lra_vision::srv::CalibrateCamera_Response>::value
  >
{
};

template<>
struct has_bounded_size<lra_vision::srv::CalibrateCamera>
  : std::integral_constant<
    bool,
    has_bounded_size<lra_vision::srv::CalibrateCamera_Request>::value &&
    has_bounded_size<lra_vision::srv::CalibrateCamera_Response>::value
  >
{
};

template<>
struct is_service<lra_vision::srv::CalibrateCamera>
  : std::true_type
{
};

template<>
struct is_service_request<lra_vision::srv::CalibrateCamera_Request>
  : std::true_type
{
};

template<>
struct is_service_response<lra_vision::srv::CalibrateCamera_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // LRA_VISION__SRV__DETAIL__CALIBRATE_CAMERA__TRAITS_HPP_
