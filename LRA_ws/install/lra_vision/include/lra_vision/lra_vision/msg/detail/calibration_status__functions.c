// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from lra_vision:msg/CalibrationStatus.idl
// generated code does not contain a copyright notice
#include "lra_vision/msg/detail/calibration_status__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `state`
// Member `error_message`
#include "rosidl_runtime_c/string_functions.h"

bool
lra_vision__msg__CalibrationStatus__init(lra_vision__msg__CalibrationStatus * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    lra_vision__msg__CalibrationStatus__fini(msg);
    return false;
  }
  // state
  if (!rosidl_runtime_c__String__init(&msg->state)) {
    lra_vision__msg__CalibrationStatus__fini(msg);
    return false;
  }
  // images_collected
  // images_required
  // images_maximum
  // current_rms_error
  // best_rms_error
  // mean_reprojection_error
  // is_ready
  // is_calibrated
  // error_message
  if (!rosidl_runtime_c__String__init(&msg->error_message)) {
    lra_vision__msg__CalibrationStatus__fini(msg);
    return false;
  }
  // progress
  return true;
}

void
lra_vision__msg__CalibrationStatus__fini(lra_vision__msg__CalibrationStatus * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // state
  rosidl_runtime_c__String__fini(&msg->state);
  // images_collected
  // images_required
  // images_maximum
  // current_rms_error
  // best_rms_error
  // mean_reprojection_error
  // is_ready
  // is_calibrated
  // error_message
  rosidl_runtime_c__String__fini(&msg->error_message);
  // progress
}

bool
lra_vision__msg__CalibrationStatus__are_equal(const lra_vision__msg__CalibrationStatus * lhs, const lra_vision__msg__CalibrationStatus * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // state
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->state), &(rhs->state)))
  {
    return false;
  }
  // images_collected
  if (lhs->images_collected != rhs->images_collected) {
    return false;
  }
  // images_required
  if (lhs->images_required != rhs->images_required) {
    return false;
  }
  // images_maximum
  if (lhs->images_maximum != rhs->images_maximum) {
    return false;
  }
  // current_rms_error
  if (lhs->current_rms_error != rhs->current_rms_error) {
    return false;
  }
  // best_rms_error
  if (lhs->best_rms_error != rhs->best_rms_error) {
    return false;
  }
  // mean_reprojection_error
  if (lhs->mean_reprojection_error != rhs->mean_reprojection_error) {
    return false;
  }
  // is_ready
  if (lhs->is_ready != rhs->is_ready) {
    return false;
  }
  // is_calibrated
  if (lhs->is_calibrated != rhs->is_calibrated) {
    return false;
  }
  // error_message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->error_message), &(rhs->error_message)))
  {
    return false;
  }
  // progress
  if (lhs->progress != rhs->progress) {
    return false;
  }
  return true;
}

bool
lra_vision__msg__CalibrationStatus__copy(
  const lra_vision__msg__CalibrationStatus * input,
  lra_vision__msg__CalibrationStatus * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // state
  if (!rosidl_runtime_c__String__copy(
      &(input->state), &(output->state)))
  {
    return false;
  }
  // images_collected
  output->images_collected = input->images_collected;
  // images_required
  output->images_required = input->images_required;
  // images_maximum
  output->images_maximum = input->images_maximum;
  // current_rms_error
  output->current_rms_error = input->current_rms_error;
  // best_rms_error
  output->best_rms_error = input->best_rms_error;
  // mean_reprojection_error
  output->mean_reprojection_error = input->mean_reprojection_error;
  // is_ready
  output->is_ready = input->is_ready;
  // is_calibrated
  output->is_calibrated = input->is_calibrated;
  // error_message
  if (!rosidl_runtime_c__String__copy(
      &(input->error_message), &(output->error_message)))
  {
    return false;
  }
  // progress
  output->progress = input->progress;
  return true;
}

lra_vision__msg__CalibrationStatus *
lra_vision__msg__CalibrationStatus__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  lra_vision__msg__CalibrationStatus * msg = (lra_vision__msg__CalibrationStatus *)allocator.allocate(sizeof(lra_vision__msg__CalibrationStatus), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(lra_vision__msg__CalibrationStatus));
  bool success = lra_vision__msg__CalibrationStatus__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
lra_vision__msg__CalibrationStatus__destroy(lra_vision__msg__CalibrationStatus * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    lra_vision__msg__CalibrationStatus__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
lra_vision__msg__CalibrationStatus__Sequence__init(lra_vision__msg__CalibrationStatus__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  lra_vision__msg__CalibrationStatus * data = NULL;

  if (size) {
    data = (lra_vision__msg__CalibrationStatus *)allocator.zero_allocate(size, sizeof(lra_vision__msg__CalibrationStatus), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = lra_vision__msg__CalibrationStatus__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        lra_vision__msg__CalibrationStatus__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
lra_vision__msg__CalibrationStatus__Sequence__fini(lra_vision__msg__CalibrationStatus__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      lra_vision__msg__CalibrationStatus__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

lra_vision__msg__CalibrationStatus__Sequence *
lra_vision__msg__CalibrationStatus__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  lra_vision__msg__CalibrationStatus__Sequence * array = (lra_vision__msg__CalibrationStatus__Sequence *)allocator.allocate(sizeof(lra_vision__msg__CalibrationStatus__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = lra_vision__msg__CalibrationStatus__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
lra_vision__msg__CalibrationStatus__Sequence__destroy(lra_vision__msg__CalibrationStatus__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    lra_vision__msg__CalibrationStatus__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
lra_vision__msg__CalibrationStatus__Sequence__are_equal(const lra_vision__msg__CalibrationStatus__Sequence * lhs, const lra_vision__msg__CalibrationStatus__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!lra_vision__msg__CalibrationStatus__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
lra_vision__msg__CalibrationStatus__Sequence__copy(
  const lra_vision__msg__CalibrationStatus__Sequence * input,
  lra_vision__msg__CalibrationStatus__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(lra_vision__msg__CalibrationStatus);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    lra_vision__msg__CalibrationStatus * data =
      (lra_vision__msg__CalibrationStatus *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!lra_vision__msg__CalibrationStatus__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          lra_vision__msg__CalibrationStatus__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!lra_vision__msg__CalibrationStatus__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
