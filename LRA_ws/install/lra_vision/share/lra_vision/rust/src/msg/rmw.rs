#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "lra_vision__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__lra_vision__msg__CalibrationStatus() -> *const std::ffi::c_void;
}

#[link(name = "lra_vision__rosidl_generator_c")]
extern "C" {
    fn lra_vision__msg__CalibrationStatus__init(msg: *mut CalibrationStatus) -> bool;
    fn lra_vision__msg__CalibrationStatus__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<CalibrationStatus>, size: usize) -> bool;
    fn lra_vision__msg__CalibrationStatus__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<CalibrationStatus>);
    fn lra_vision__msg__CalibrationStatus__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<CalibrationStatus>, out_seq: *mut rosidl_runtime_rs::Sequence<CalibrationStatus>) -> bool;
}

// Corresponds to lra_vision__msg__CalibrationStatus
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CalibrationStatus {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub state: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub images_collected: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub images_required: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub images_maximum: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub current_rms_error: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub best_rms_error: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mean_reprojection_error: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub is_ready: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub is_calibrated: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub error_message: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub progress: f64,

}



impl Default for CalibrationStatus {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !lra_vision__msg__CalibrationStatus__init(&mut msg as *mut _) {
        panic!("Call to lra_vision__msg__CalibrationStatus__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for CalibrationStatus {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { lra_vision__msg__CalibrationStatus__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { lra_vision__msg__CalibrationStatus__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { lra_vision__msg__CalibrationStatus__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for CalibrationStatus {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for CalibrationStatus where Self: Sized {
  const TYPE_NAME: &'static str = "lra_vision/msg/CalibrationStatus";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__lra_vision__msg__CalibrationStatus() }
  }
}


