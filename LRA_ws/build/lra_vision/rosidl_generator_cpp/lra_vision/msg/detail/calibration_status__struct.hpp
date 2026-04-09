// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from lra_vision:msg/CalibrationStatus.idl
// generated code does not contain a copyright notice

#ifndef LRA_VISION__MSG__DETAIL__CALIBRATION_STATUS__STRUCT_HPP_
#define LRA_VISION__MSG__DETAIL__CALIBRATION_STATUS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__lra_vision__msg__CalibrationStatus __attribute__((deprecated))
#else
# define DEPRECATED__lra_vision__msg__CalibrationStatus __declspec(deprecated)
#endif

namespace lra_vision
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct CalibrationStatus_
{
  using Type = CalibrationStatus_<ContainerAllocator>;

  explicit CalibrationStatus_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->state = "";
      this->images_collected = 0l;
      this->images_required = 0l;
      this->images_maximum = 0l;
      this->current_rms_error = 0.0;
      this->best_rms_error = 0.0;
      this->mean_reprojection_error = 0.0;
      this->is_ready = false;
      this->is_calibrated = false;
      this->error_message = "";
      this->progress = 0.0;
    }
  }

  explicit CalibrationStatus_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    state(_alloc),
    error_message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->state = "";
      this->images_collected = 0l;
      this->images_required = 0l;
      this->images_maximum = 0l;
      this->current_rms_error = 0.0;
      this->best_rms_error = 0.0;
      this->mean_reprojection_error = 0.0;
      this->is_ready = false;
      this->is_calibrated = false;
      this->error_message = "";
      this->progress = 0.0;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _state_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _state_type state;
  using _images_collected_type =
    int32_t;
  _images_collected_type images_collected;
  using _images_required_type =
    int32_t;
  _images_required_type images_required;
  using _images_maximum_type =
    int32_t;
  _images_maximum_type images_maximum;
  using _current_rms_error_type =
    double;
  _current_rms_error_type current_rms_error;
  using _best_rms_error_type =
    double;
  _best_rms_error_type best_rms_error;
  using _mean_reprojection_error_type =
    double;
  _mean_reprojection_error_type mean_reprojection_error;
  using _is_ready_type =
    bool;
  _is_ready_type is_ready;
  using _is_calibrated_type =
    bool;
  _is_calibrated_type is_calibrated;
  using _error_message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _error_message_type error_message;
  using _progress_type =
    double;
  _progress_type progress;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__state(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->state = _arg;
    return *this;
  }
  Type & set__images_collected(
    const int32_t & _arg)
  {
    this->images_collected = _arg;
    return *this;
  }
  Type & set__images_required(
    const int32_t & _arg)
  {
    this->images_required = _arg;
    return *this;
  }
  Type & set__images_maximum(
    const int32_t & _arg)
  {
    this->images_maximum = _arg;
    return *this;
  }
  Type & set__current_rms_error(
    const double & _arg)
  {
    this->current_rms_error = _arg;
    return *this;
  }
  Type & set__best_rms_error(
    const double & _arg)
  {
    this->best_rms_error = _arg;
    return *this;
  }
  Type & set__mean_reprojection_error(
    const double & _arg)
  {
    this->mean_reprojection_error = _arg;
    return *this;
  }
  Type & set__is_ready(
    const bool & _arg)
  {
    this->is_ready = _arg;
    return *this;
  }
  Type & set__is_calibrated(
    const bool & _arg)
  {
    this->is_calibrated = _arg;
    return *this;
  }
  Type & set__error_message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->error_message = _arg;
    return *this;
  }
  Type & set__progress(
    const double & _arg)
  {
    this->progress = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    lra_vision::msg::CalibrationStatus_<ContainerAllocator> *;
  using ConstRawPtr =
    const lra_vision::msg::CalibrationStatus_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<lra_vision::msg::CalibrationStatus_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<lra_vision::msg::CalibrationStatus_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      lra_vision::msg::CalibrationStatus_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<lra_vision::msg::CalibrationStatus_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      lra_vision::msg::CalibrationStatus_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<lra_vision::msg::CalibrationStatus_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<lra_vision::msg::CalibrationStatus_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<lra_vision::msg::CalibrationStatus_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__lra_vision__msg__CalibrationStatus
    std::shared_ptr<lra_vision::msg::CalibrationStatus_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__lra_vision__msg__CalibrationStatus
    std::shared_ptr<lra_vision::msg::CalibrationStatus_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CalibrationStatus_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->state != other.state) {
      return false;
    }
    if (this->images_collected != other.images_collected) {
      return false;
    }
    if (this->images_required != other.images_required) {
      return false;
    }
    if (this->images_maximum != other.images_maximum) {
      return false;
    }
    if (this->current_rms_error != other.current_rms_error) {
      return false;
    }
    if (this->best_rms_error != other.best_rms_error) {
      return false;
    }
    if (this->mean_reprojection_error != other.mean_reprojection_error) {
      return false;
    }
    if (this->is_ready != other.is_ready) {
      return false;
    }
    if (this->is_calibrated != other.is_calibrated) {
      return false;
    }
    if (this->error_message != other.error_message) {
      return false;
    }
    if (this->progress != other.progress) {
      return false;
    }
    return true;
  }
  bool operator!=(const CalibrationStatus_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CalibrationStatus_

// alias to use template instance with default allocator
using CalibrationStatus =
  lra_vision::msg::CalibrationStatus_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace lra_vision

#endif  // LRA_VISION__MSG__DETAIL__CALIBRATION_STATUS__STRUCT_HPP_
