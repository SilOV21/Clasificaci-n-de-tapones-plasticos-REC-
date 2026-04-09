// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from lra_vision:srv/CalibrateCamera.idl
// generated code does not contain a copyright notice

#ifndef LRA_VISION__SRV__DETAIL__CALIBRATE_CAMERA__FUNCTIONS_H_
#define LRA_VISION__SRV__DETAIL__CALIBRATE_CAMERA__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "lra_vision/msg/rosidl_generator_c__visibility_control.h"

#include "lra_vision/srv/detail/calibrate_camera__struct.h"

/// Initialize srv/CalibrateCamera message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * lra_vision__srv__CalibrateCamera_Request
 * )) before or use
 * lra_vision__srv__CalibrateCamera_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
bool
lra_vision__srv__CalibrateCamera_Request__init(lra_vision__srv__CalibrateCamera_Request * msg);

/// Finalize srv/CalibrateCamera message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
void
lra_vision__srv__CalibrateCamera_Request__fini(lra_vision__srv__CalibrateCamera_Request * msg);

/// Create srv/CalibrateCamera message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * lra_vision__srv__CalibrateCamera_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
lra_vision__srv__CalibrateCamera_Request *
lra_vision__srv__CalibrateCamera_Request__create();

/// Destroy srv/CalibrateCamera message.
/**
 * It calls
 * lra_vision__srv__CalibrateCamera_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
void
lra_vision__srv__CalibrateCamera_Request__destroy(lra_vision__srv__CalibrateCamera_Request * msg);

/// Check for srv/CalibrateCamera message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
bool
lra_vision__srv__CalibrateCamera_Request__are_equal(const lra_vision__srv__CalibrateCamera_Request * lhs, const lra_vision__srv__CalibrateCamera_Request * rhs);

/// Copy a srv/CalibrateCamera message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
bool
lra_vision__srv__CalibrateCamera_Request__copy(
  const lra_vision__srv__CalibrateCamera_Request * input,
  lra_vision__srv__CalibrateCamera_Request * output);

/// Initialize array of srv/CalibrateCamera messages.
/**
 * It allocates the memory for the number of elements and calls
 * lra_vision__srv__CalibrateCamera_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
bool
lra_vision__srv__CalibrateCamera_Request__Sequence__init(lra_vision__srv__CalibrateCamera_Request__Sequence * array, size_t size);

/// Finalize array of srv/CalibrateCamera messages.
/**
 * It calls
 * lra_vision__srv__CalibrateCamera_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
void
lra_vision__srv__CalibrateCamera_Request__Sequence__fini(lra_vision__srv__CalibrateCamera_Request__Sequence * array);

/// Create array of srv/CalibrateCamera messages.
/**
 * It allocates the memory for the array and calls
 * lra_vision__srv__CalibrateCamera_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
lra_vision__srv__CalibrateCamera_Request__Sequence *
lra_vision__srv__CalibrateCamera_Request__Sequence__create(size_t size);

/// Destroy array of srv/CalibrateCamera messages.
/**
 * It calls
 * lra_vision__srv__CalibrateCamera_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
void
lra_vision__srv__CalibrateCamera_Request__Sequence__destroy(lra_vision__srv__CalibrateCamera_Request__Sequence * array);

/// Check for srv/CalibrateCamera message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
bool
lra_vision__srv__CalibrateCamera_Request__Sequence__are_equal(const lra_vision__srv__CalibrateCamera_Request__Sequence * lhs, const lra_vision__srv__CalibrateCamera_Request__Sequence * rhs);

/// Copy an array of srv/CalibrateCamera messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
bool
lra_vision__srv__CalibrateCamera_Request__Sequence__copy(
  const lra_vision__srv__CalibrateCamera_Request__Sequence * input,
  lra_vision__srv__CalibrateCamera_Request__Sequence * output);

/// Initialize srv/CalibrateCamera message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * lra_vision__srv__CalibrateCamera_Response
 * )) before or use
 * lra_vision__srv__CalibrateCamera_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
bool
lra_vision__srv__CalibrateCamera_Response__init(lra_vision__srv__CalibrateCamera_Response * msg);

/// Finalize srv/CalibrateCamera message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
void
lra_vision__srv__CalibrateCamera_Response__fini(lra_vision__srv__CalibrateCamera_Response * msg);

/// Create srv/CalibrateCamera message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * lra_vision__srv__CalibrateCamera_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
lra_vision__srv__CalibrateCamera_Response *
lra_vision__srv__CalibrateCamera_Response__create();

/// Destroy srv/CalibrateCamera message.
/**
 * It calls
 * lra_vision__srv__CalibrateCamera_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
void
lra_vision__srv__CalibrateCamera_Response__destroy(lra_vision__srv__CalibrateCamera_Response * msg);

/// Check for srv/CalibrateCamera message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
bool
lra_vision__srv__CalibrateCamera_Response__are_equal(const lra_vision__srv__CalibrateCamera_Response * lhs, const lra_vision__srv__CalibrateCamera_Response * rhs);

/// Copy a srv/CalibrateCamera message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
bool
lra_vision__srv__CalibrateCamera_Response__copy(
  const lra_vision__srv__CalibrateCamera_Response * input,
  lra_vision__srv__CalibrateCamera_Response * output);

/// Initialize array of srv/CalibrateCamera messages.
/**
 * It allocates the memory for the number of elements and calls
 * lra_vision__srv__CalibrateCamera_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
bool
lra_vision__srv__CalibrateCamera_Response__Sequence__init(lra_vision__srv__CalibrateCamera_Response__Sequence * array, size_t size);

/// Finalize array of srv/CalibrateCamera messages.
/**
 * It calls
 * lra_vision__srv__CalibrateCamera_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
void
lra_vision__srv__CalibrateCamera_Response__Sequence__fini(lra_vision__srv__CalibrateCamera_Response__Sequence * array);

/// Create array of srv/CalibrateCamera messages.
/**
 * It allocates the memory for the array and calls
 * lra_vision__srv__CalibrateCamera_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
lra_vision__srv__CalibrateCamera_Response__Sequence *
lra_vision__srv__CalibrateCamera_Response__Sequence__create(size_t size);

/// Destroy array of srv/CalibrateCamera messages.
/**
 * It calls
 * lra_vision__srv__CalibrateCamera_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
void
lra_vision__srv__CalibrateCamera_Response__Sequence__destroy(lra_vision__srv__CalibrateCamera_Response__Sequence * array);

/// Check for srv/CalibrateCamera message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
bool
lra_vision__srv__CalibrateCamera_Response__Sequence__are_equal(const lra_vision__srv__CalibrateCamera_Response__Sequence * lhs, const lra_vision__srv__CalibrateCamera_Response__Sequence * rhs);

/// Copy an array of srv/CalibrateCamera messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_lra_vision
bool
lra_vision__srv__CalibrateCamera_Response__Sequence__copy(
  const lra_vision__srv__CalibrateCamera_Response__Sequence * input,
  lra_vision__srv__CalibrateCamera_Response__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // LRA_VISION__SRV__DETAIL__CALIBRATE_CAMERA__FUNCTIONS_H_
