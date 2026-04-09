// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from lra_vision:srv/CalibrateCamera.idl
// generated code does not contain a copyright notice

#ifndef LRA_VISION__SRV__DETAIL__CALIBRATE_CAMERA__STRUCT_HPP_
#define LRA_VISION__SRV__DETAIL__CALIBRATE_CAMERA__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__lra_vision__srv__CalibrateCamera_Request __attribute__((deprecated))
#else
# define DEPRECATED__lra_vision__srv__CalibrateCamera_Request __declspec(deprecated)
#endif

namespace lra_vision
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct CalibrateCamera_Request_
{
  using Type = CalibrateCamera_Request_<ContainerAllocator>;

  explicit CalibrateCamera_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->action = "";
    }
  }

  explicit CalibrateCamera_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : action(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->action = "";
    }
  }

  // field types and members
  using _action_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _action_type action;

  // setters for named parameter idiom
  Type & set__action(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->action = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    lra_vision::srv::CalibrateCamera_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const lra_vision::srv::CalibrateCamera_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<lra_vision::srv::CalibrateCamera_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<lra_vision::srv::CalibrateCamera_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      lra_vision::srv::CalibrateCamera_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<lra_vision::srv::CalibrateCamera_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      lra_vision::srv::CalibrateCamera_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<lra_vision::srv::CalibrateCamera_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<lra_vision::srv::CalibrateCamera_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<lra_vision::srv::CalibrateCamera_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__lra_vision__srv__CalibrateCamera_Request
    std::shared_ptr<lra_vision::srv::CalibrateCamera_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__lra_vision__srv__CalibrateCamera_Request
    std::shared_ptr<lra_vision::srv::CalibrateCamera_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CalibrateCamera_Request_ & other) const
  {
    if (this->action != other.action) {
      return false;
    }
    return true;
  }
  bool operator!=(const CalibrateCamera_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CalibrateCamera_Request_

// alias to use template instance with default allocator
using CalibrateCamera_Request =
  lra_vision::srv::CalibrateCamera_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace lra_vision


#ifndef _WIN32
# define DEPRECATED__lra_vision__srv__CalibrateCamera_Response __attribute__((deprecated))
#else
# define DEPRECATED__lra_vision__srv__CalibrateCamera_Response __declspec(deprecated)
#endif

namespace lra_vision
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct CalibrateCamera_Response_
{
  using Type = CalibrateCamera_Response_<ContainerAllocator>;

  explicit CalibrateCamera_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  explicit CalibrateCamera_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }
  Type & set__message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->message = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    lra_vision::srv::CalibrateCamera_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const lra_vision::srv::CalibrateCamera_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<lra_vision::srv::CalibrateCamera_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<lra_vision::srv::CalibrateCamera_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      lra_vision::srv::CalibrateCamera_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<lra_vision::srv::CalibrateCamera_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      lra_vision::srv::CalibrateCamera_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<lra_vision::srv::CalibrateCamera_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<lra_vision::srv::CalibrateCamera_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<lra_vision::srv::CalibrateCamera_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__lra_vision__srv__CalibrateCamera_Response
    std::shared_ptr<lra_vision::srv::CalibrateCamera_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__lra_vision__srv__CalibrateCamera_Response
    std::shared_ptr<lra_vision::srv::CalibrateCamera_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CalibrateCamera_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const CalibrateCamera_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CalibrateCamera_Response_

// alias to use template instance with default allocator
using CalibrateCamera_Response =
  lra_vision::srv::CalibrateCamera_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace lra_vision

namespace lra_vision
{

namespace srv
{

struct CalibrateCamera
{
  using Request = lra_vision::srv::CalibrateCamera_Request;
  using Response = lra_vision::srv::CalibrateCamera_Response;
};

}  // namespace srv

}  // namespace lra_vision

#endif  // LRA_VISION__SRV__DETAIL__CALIBRATE_CAMERA__STRUCT_HPP_
