#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to lra_vision__msg__CalibrationStatus

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CalibrationStatus {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub state: std::string::String,


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
    pub error_message: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub progress: f64,

}



impl Default for CalibrationStatus {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::CalibrationStatus::default())
  }
}

impl rosidl_runtime_rs::Message for CalibrationStatus {
  type RmwMsg = super::msg::rmw::CalibrationStatus;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        state: msg.state.as_str().into(),
        images_collected: msg.images_collected,
        images_required: msg.images_required,
        images_maximum: msg.images_maximum,
        current_rms_error: msg.current_rms_error,
        best_rms_error: msg.best_rms_error,
        mean_reprojection_error: msg.mean_reprojection_error,
        is_ready: msg.is_ready,
        is_calibrated: msg.is_calibrated,
        error_message: msg.error_message.as_str().into(),
        progress: msg.progress,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        state: msg.state.as_str().into(),
      images_collected: msg.images_collected,
      images_required: msg.images_required,
      images_maximum: msg.images_maximum,
      current_rms_error: msg.current_rms_error,
      best_rms_error: msg.best_rms_error,
      mean_reprojection_error: msg.mean_reprojection_error,
      is_ready: msg.is_ready,
      is_calibrated: msg.is_calibrated,
        error_message: msg.error_message.as_str().into(),
      progress: msg.progress,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      state: msg.state.to_string(),
      images_collected: msg.images_collected,
      images_required: msg.images_required,
      images_maximum: msg.images_maximum,
      current_rms_error: msg.current_rms_error,
      best_rms_error: msg.best_rms_error,
      mean_reprojection_error: msg.mean_reprojection_error,
      is_ready: msg.is_ready,
      is_calibrated: msg.is_calibrated,
      error_message: msg.error_message.to_string(),
      progress: msg.progress,
    }
  }
}


