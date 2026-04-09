// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from lra_vision:srv/CalibrateCamera.idl
// generated code does not contain a copyright notice

#ifndef LRA_VISION__SRV__DETAIL__CALIBRATE_CAMERA__BUILDER_HPP_
#define LRA_VISION__SRV__DETAIL__CALIBRATE_CAMERA__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "lra_vision/srv/detail/calibrate_camera__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace lra_vision
{

namespace srv
{

namespace builder
{

class Init_CalibrateCamera_Request_action
{
public:
  Init_CalibrateCamera_Request_action()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::lra_vision::srv::CalibrateCamera_Request action(::lra_vision::srv::CalibrateCamera_Request::_action_type arg)
  {
    msg_.action = std::move(arg);
    return std::move(msg_);
  }

private:
  ::lra_vision::srv::CalibrateCamera_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::lra_vision::srv::CalibrateCamera_Request>()
{
  return lra_vision::srv::builder::Init_CalibrateCamera_Request_action();
}

}  // namespace lra_vision


namespace lra_vision
{

namespace srv
{

namespace builder
{

class Init_CalibrateCamera_Response_message
{
public:
  explicit Init_CalibrateCamera_Response_message(::lra_vision::srv::CalibrateCamera_Response & msg)
  : msg_(msg)
  {}
  ::lra_vision::srv::CalibrateCamera_Response message(::lra_vision::srv::CalibrateCamera_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::lra_vision::srv::CalibrateCamera_Response msg_;
};

class Init_CalibrateCamera_Response_success
{
public:
  Init_CalibrateCamera_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_CalibrateCamera_Response_message success(::lra_vision::srv::CalibrateCamera_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_CalibrateCamera_Response_message(msg_);
  }

private:
  ::lra_vision::srv::CalibrateCamera_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::lra_vision::srv::CalibrateCamera_Response>()
{
  return lra_vision::srv::builder::Init_CalibrateCamera_Response_success();
}

}  // namespace lra_vision

#endif  // LRA_VISION__SRV__DETAIL__CALIBRATE_CAMERA__BUILDER_HPP_
