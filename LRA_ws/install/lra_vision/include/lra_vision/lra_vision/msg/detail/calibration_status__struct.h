// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from lra_vision:msg/CalibrationStatus.idl
// generated code does not contain a copyright notice

#ifndef LRA_VISION__MSG__DETAIL__CALIBRATION_STATUS__STRUCT_H_
#define LRA_VISION__MSG__DETAIL__CALIBRATION_STATUS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'state'
// Member 'error_message'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/CalibrationStatus in the package lra_vision.
typedef struct lra_vision__msg__CalibrationStatus
{
  std_msgs__msg__Header header;
  rosidl_runtime_c__String state;
  int32_t images_collected;
  int32_t images_required;
  int32_t images_maximum;
  double current_rms_error;
  double best_rms_error;
  double mean_reprojection_error;
  bool is_ready;
  bool is_calibrated;
  rosidl_runtime_c__String error_message;
  double progress;
} lra_vision__msg__CalibrationStatus;

// Struct for a sequence of lra_vision__msg__CalibrationStatus.
typedef struct lra_vision__msg__CalibrationStatus__Sequence
{
  lra_vision__msg__CalibrationStatus * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} lra_vision__msg__CalibrationStatus__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // LRA_VISION__MSG__DETAIL__CALIBRATION_STATUS__STRUCT_H_
