// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from lra_vision:msg/CalibrationStatus.idl
// generated code does not contain a copyright notice

#ifndef LRA_VISION__MSG__DETAIL__CALIBRATION_STATUS__BUILDER_HPP_
#define LRA_VISION__MSG__DETAIL__CALIBRATION_STATUS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "lra_vision/msg/detail/calibration_status__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace lra_vision
{

namespace msg
{

namespace builder
{

class Init_CalibrationStatus_progress
{
public:
  explicit Init_CalibrationStatus_progress(::lra_vision::msg::CalibrationStatus & msg)
  : msg_(msg)
  {}
  ::lra_vision::msg::CalibrationStatus progress(::lra_vision::msg::CalibrationStatus::_progress_type arg)
  {
    msg_.progress = std::move(arg);
    return std::move(msg_);
  }

private:
  ::lra_vision::msg::CalibrationStatus msg_;
};

class Init_CalibrationStatus_error_message
{
public:
  explicit Init_CalibrationStatus_error_message(::lra_vision::msg::CalibrationStatus & msg)
  : msg_(msg)
  {}
  Init_CalibrationStatus_progress error_message(::lra_vision::msg::CalibrationStatus::_error_message_type arg)
  {
    msg_.error_message = std::move(arg);
    return Init_CalibrationStatus_progress(msg_);
  }

private:
  ::lra_vision::msg::CalibrationStatus msg_;
};

class Init_CalibrationStatus_is_calibrated
{
public:
  explicit Init_CalibrationStatus_is_calibrated(::lra_vision::msg::CalibrationStatus & msg)
  : msg_(msg)
  {}
  Init_CalibrationStatus_error_message is_calibrated(::lra_vision::msg::CalibrationStatus::_is_calibrated_type arg)
  {
    msg_.is_calibrated = std::move(arg);
    return Init_CalibrationStatus_error_message(msg_);
  }

private:
  ::lra_vision::msg::CalibrationStatus msg_;
};

class Init_CalibrationStatus_is_ready
{
public:
  explicit Init_CalibrationStatus_is_ready(::lra_vision::msg::CalibrationStatus & msg)
  : msg_(msg)
  {}
  Init_CalibrationStatus_is_calibrated is_ready(::lra_vision::msg::CalibrationStatus::_is_ready_type arg)
  {
    msg_.is_ready = std::move(arg);
    return Init_CalibrationStatus_is_calibrated(msg_);
  }

private:
  ::lra_vision::msg::CalibrationStatus msg_;
};

class Init_CalibrationStatus_mean_reprojection_error
{
public:
  explicit Init_CalibrationStatus_mean_reprojection_error(::lra_vision::msg::CalibrationStatus & msg)
  : msg_(msg)
  {}
  Init_CalibrationStatus_is_ready mean_reprojection_error(::lra_vision::msg::CalibrationStatus::_mean_reprojection_error_type arg)
  {
    msg_.mean_reprojection_error = std::move(arg);
    return Init_CalibrationStatus_is_ready(msg_);
  }

private:
  ::lra_vision::msg::CalibrationStatus msg_;
};

class Init_CalibrationStatus_best_rms_error
{
public:
  explicit Init_CalibrationStatus_best_rms_error(::lra_vision::msg::CalibrationStatus & msg)
  : msg_(msg)
  {}
  Init_CalibrationStatus_mean_reprojection_error best_rms_error(::lra_vision::msg::CalibrationStatus::_best_rms_error_type arg)
  {
    msg_.best_rms_error = std::move(arg);
    return Init_CalibrationStatus_mean_reprojection_error(msg_);
  }

private:
  ::lra_vision::msg::CalibrationStatus msg_;
};

class Init_CalibrationStatus_current_rms_error
{
public:
  explicit Init_CalibrationStatus_current_rms_error(::lra_vision::msg::CalibrationStatus & msg)
  : msg_(msg)
  {}
  Init_CalibrationStatus_best_rms_error current_rms_error(::lra_vision::msg::CalibrationStatus::_current_rms_error_type arg)
  {
    msg_.current_rms_error = std::move(arg);
    return Init_CalibrationStatus_best_rms_error(msg_);
  }

private:
  ::lra_vision::msg::CalibrationStatus msg_;
};

class Init_CalibrationStatus_images_maximum
{
public:
  explicit Init_CalibrationStatus_images_maximum(::lra_vision::msg::CalibrationStatus & msg)
  : msg_(msg)
  {}
  Init_CalibrationStatus_current_rms_error images_maximum(::lra_vision::msg::CalibrationStatus::_images_maximum_type arg)
  {
    msg_.images_maximum = std::move(arg);
    return Init_CalibrationStatus_current_rms_error(msg_);
  }

private:
  ::lra_vision::msg::CalibrationStatus msg_;
};

class Init_CalibrationStatus_images_required
{
public:
  explicit Init_CalibrationStatus_images_required(::lra_vision::msg::CalibrationStatus & msg)
  : msg_(msg)
  {}
  Init_CalibrationStatus_images_maximum images_required(::lra_vision::msg::CalibrationStatus::_images_required_type arg)
  {
    msg_.images_required = std::move(arg);
    return Init_CalibrationStatus_images_maximum(msg_);
  }

private:
  ::lra_vision::msg::CalibrationStatus msg_;
};

class Init_CalibrationStatus_images_collected
{
public:
  explicit Init_CalibrationStatus_images_collected(::lra_vision::msg::CalibrationStatus & msg)
  : msg_(msg)
  {}
  Init_CalibrationStatus_images_required images_collected(::lra_vision::msg::CalibrationStatus::_images_collected_type arg)
  {
    msg_.images_collected = std::move(arg);
    return Init_CalibrationStatus_images_required(msg_);
  }

private:
  ::lra_vision::msg::CalibrationStatus msg_;
};

class Init_CalibrationStatus_state
{
public:
  explicit Init_CalibrationStatus_state(::lra_vision::msg::CalibrationStatus & msg)
  : msg_(msg)
  {}
  Init_CalibrationStatus_images_collected state(::lra_vision::msg::CalibrationStatus::_state_type arg)
  {
    msg_.state = std::move(arg);
    return Init_CalibrationStatus_images_collected(msg_);
  }

private:
  ::lra_vision::msg::CalibrationStatus msg_;
};

class Init_CalibrationStatus_header
{
public:
  Init_CalibrationStatus_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_CalibrationStatus_state header(::lra_vision::msg::CalibrationStatus::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_CalibrationStatus_state(msg_);
  }

private:
  ::lra_vision::msg::CalibrationStatus msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::lra_vision::msg::CalibrationStatus>()
{
  return lra_vision::msg::builder::Init_CalibrationStatus_header();
}

}  // namespace lra_vision

#endif  // LRA_VISION__MSG__DETAIL__CALIBRATION_STATUS__BUILDER_HPP_
