// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from lra_vision:srv/CalibrateCamera.idl
// generated code does not contain a copyright notice

#ifndef LRA_VISION__SRV__DETAIL__CALIBRATE_CAMERA__STRUCT_H_
#define LRA_VISION__SRV__DETAIL__CALIBRATE_CAMERA__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'action'
#include "rosidl_runtime_c/string.h"

/// Struct defined in srv/CalibrateCamera in the package lra_vision.
typedef struct lra_vision__srv__CalibrateCamera_Request
{
  rosidl_runtime_c__String action;
} lra_vision__srv__CalibrateCamera_Request;

// Struct for a sequence of lra_vision__srv__CalibrateCamera_Request.
typedef struct lra_vision__srv__CalibrateCamera_Request__Sequence
{
  lra_vision__srv__CalibrateCamera_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} lra_vision__srv__CalibrateCamera_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/CalibrateCamera in the package lra_vision.
typedef struct lra_vision__srv__CalibrateCamera_Response
{
  bool success;
  rosidl_runtime_c__String message;
} lra_vision__srv__CalibrateCamera_Response;

// Struct for a sequence of lra_vision__srv__CalibrateCamera_Response.
typedef struct lra_vision__srv__CalibrateCamera_Response__Sequence
{
  lra_vision__srv__CalibrateCamera_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} lra_vision__srv__CalibrateCamera_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // LRA_VISION__SRV__DETAIL__CALIBRATE_CAMERA__STRUCT_H_
