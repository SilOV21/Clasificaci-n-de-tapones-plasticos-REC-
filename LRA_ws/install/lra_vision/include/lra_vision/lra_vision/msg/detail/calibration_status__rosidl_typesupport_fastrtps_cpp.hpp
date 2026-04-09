// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__rosidl_typesupport_fastrtps_cpp.hpp.em
// with input from lra_vision:msg/CalibrationStatus.idl
// generated code does not contain a copyright notice

#ifndef LRA_VISION__MSG__DETAIL__CALIBRATION_STATUS__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
#define LRA_VISION__MSG__DETAIL__CALIBRATION_STATUS__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_

#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "lra_vision/msg/rosidl_typesupport_fastrtps_cpp__visibility_control.h"
#include "lra_vision/msg/detail/calibration_status__struct.hpp"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

#include "fastcdr/Cdr.h"

namespace lra_vision
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_lra_vision
cdr_serialize(
  const lra_vision::msg::CalibrationStatus & ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_lra_vision
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  lra_vision::msg::CalibrationStatus & ros_message);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_lra_vision
get_serialized_size(
  const lra_vision::msg::CalibrationStatus & ros_message,
  size_t current_alignment);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_lra_vision
max_serialized_size_CalibrationStatus(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace lra_vision

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_lra_vision
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, lra_vision, msg, CalibrationStatus)();

#ifdef __cplusplus
}
#endif

#endif  // LRA_VISION__MSG__DETAIL__CALIBRATION_STATUS__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
