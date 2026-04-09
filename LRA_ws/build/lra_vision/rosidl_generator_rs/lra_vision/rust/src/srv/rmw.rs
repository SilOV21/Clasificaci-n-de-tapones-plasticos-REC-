#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



#[link(name = "lra_vision__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__lra_vision__srv__CalibrateCamera_Request() -> *const std::ffi::c_void;
}

#[link(name = "lra_vision__rosidl_generator_c")]
extern "C" {
    fn lra_vision__srv__CalibrateCamera_Request__init(msg: *mut CalibrateCamera_Request) -> bool;
    fn lra_vision__srv__CalibrateCamera_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<CalibrateCamera_Request>, size: usize) -> bool;
    fn lra_vision__srv__CalibrateCamera_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<CalibrateCamera_Request>);
    fn lra_vision__srv__CalibrateCamera_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<CalibrateCamera_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<CalibrateCamera_Request>) -> bool;
}

// Corresponds to lra_vision__srv__CalibrateCamera_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CalibrateCamera_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub action: rosidl_runtime_rs::String,

}



impl Default for CalibrateCamera_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !lra_vision__srv__CalibrateCamera_Request__init(&mut msg as *mut _) {
        panic!("Call to lra_vision__srv__CalibrateCamera_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for CalibrateCamera_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { lra_vision__srv__CalibrateCamera_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { lra_vision__srv__CalibrateCamera_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { lra_vision__srv__CalibrateCamera_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for CalibrateCamera_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for CalibrateCamera_Request where Self: Sized {
  const TYPE_NAME: &'static str = "lra_vision/srv/CalibrateCamera_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__lra_vision__srv__CalibrateCamera_Request() }
  }
}


#[link(name = "lra_vision__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__lra_vision__srv__CalibrateCamera_Response() -> *const std::ffi::c_void;
}

#[link(name = "lra_vision__rosidl_generator_c")]
extern "C" {
    fn lra_vision__srv__CalibrateCamera_Response__init(msg: *mut CalibrateCamera_Response) -> bool;
    fn lra_vision__srv__CalibrateCamera_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<CalibrateCamera_Response>, size: usize) -> bool;
    fn lra_vision__srv__CalibrateCamera_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<CalibrateCamera_Response>);
    fn lra_vision__srv__CalibrateCamera_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<CalibrateCamera_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<CalibrateCamera_Response>) -> bool;
}

// Corresponds to lra_vision__srv__CalibrateCamera_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CalibrateCamera_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: rosidl_runtime_rs::String,

}



impl Default for CalibrateCamera_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !lra_vision__srv__CalibrateCamera_Response__init(&mut msg as *mut _) {
        panic!("Call to lra_vision__srv__CalibrateCamera_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for CalibrateCamera_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { lra_vision__srv__CalibrateCamera_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { lra_vision__srv__CalibrateCamera_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { lra_vision__srv__CalibrateCamera_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for CalibrateCamera_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for CalibrateCamera_Response where Self: Sized {
  const TYPE_NAME: &'static str = "lra_vision/srv/CalibrateCamera_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__lra_vision__srv__CalibrateCamera_Response() }
  }
}






#[link(name = "lra_vision__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__lra_vision__srv__CalibrateCamera() -> *const std::ffi::c_void;
}

// Corresponds to lra_vision__srv__CalibrateCamera
#[allow(missing_docs, non_camel_case_types)]
pub struct CalibrateCamera;

impl rosidl_runtime_rs::Service for CalibrateCamera {
    type Request = CalibrateCamera_Request;
    type Response = CalibrateCamera_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__lra_vision__srv__CalibrateCamera() }
    }
}


