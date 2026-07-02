#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "turtlebot4_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__turtlebot4_msgs__msg__UserLed() -> *const std::ffi::c_void;
}

#[link(name = "turtlebot4_msgs__rosidl_generator_c")]
extern "C" {
    fn turtlebot4_msgs__msg__UserLed__init(msg: *mut UserLed) -> bool;
    fn turtlebot4_msgs__msg__UserLed__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<UserLed>, size: usize) -> bool;
    fn turtlebot4_msgs__msg__UserLed__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<UserLed>);
    fn turtlebot4_msgs__msg__UserLed__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<UserLed>, out_seq: *mut rosidl_runtime_rs::Sequence<UserLed>) -> bool;
}

// Corresponds to turtlebot4_msgs__msg__UserLed
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// This message sets the state of the user LEDs
/// Blink period is the time in milliseconds during which the ON/OFF cycle occurs
/// The duty cycle represents the percentage of the blink period that the LED is ON
/// A duty cycle of 1.0 would set the LED to always be ON, whereas a duty cycle of 0.0 is always OFF
/// A blink period of 1000ms with a duty cycle of 0.6 will have the LED turn ON for 600ms, 
/// then OFF for 400ms

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct UserLed {
    /// Which available LED to use
    pub led: u8,

    /// Which color to set the LED to
    pub color: u8,

    /// Blink period in ms
    pub blink_period: u32,

    /// Duty cycle (0.0 to 1.0)
    pub duty_cycle: f64,

}

impl UserLed {
    /// Available LEDs
    pub const USER_LED_1: u8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const USER_LED_2: u8 = 1;

    /// Available colors
    pub const COLOR_OFF: u8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const COLOR_GREEN: u8 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const COLOR_RED: u8 = 2;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const COLOR_YELLOW: u8 = 3;

}


impl Default for UserLed {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !turtlebot4_msgs__msg__UserLed__init(&mut msg as *mut _) {
        panic!("Call to turtlebot4_msgs__msg__UserLed__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for UserLed {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { turtlebot4_msgs__msg__UserLed__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { turtlebot4_msgs__msg__UserLed__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { turtlebot4_msgs__msg__UserLed__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for UserLed {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for UserLed where Self: Sized {
  const TYPE_NAME: &'static str = "turtlebot4_msgs/msg/UserLed";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__turtlebot4_msgs__msg__UserLed() }
  }
}


#[link(name = "turtlebot4_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__turtlebot4_msgs__msg__UserButton() -> *const std::ffi::c_void;
}

#[link(name = "turtlebot4_msgs__rosidl_generator_c")]
extern "C" {
    fn turtlebot4_msgs__msg__UserButton__init(msg: *mut UserButton) -> bool;
    fn turtlebot4_msgs__msg__UserButton__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<UserButton>, size: usize) -> bool;
    fn turtlebot4_msgs__msg__UserButton__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<UserButton>);
    fn turtlebot4_msgs__msg__UserButton__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<UserButton>, out_seq: *mut rosidl_runtime_rs::Sequence<UserButton>) -> bool;
}

// Corresponds to turtlebot4_msgs__msg__UserButton
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// This message relays the state of the user buttons
/// Each button is represented with a boolean, were True indicates the button is pressed

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct UserButton {

    // This member is not documented.
    #[allow(missing_docs)]
    pub button: [bool; 4],

}



impl Default for UserButton {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !turtlebot4_msgs__msg__UserButton__init(&mut msg as *mut _) {
        panic!("Call to turtlebot4_msgs__msg__UserButton__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for UserButton {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { turtlebot4_msgs__msg__UserButton__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { turtlebot4_msgs__msg__UserButton__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { turtlebot4_msgs__msg__UserButton__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for UserButton {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for UserButton where Self: Sized {
  const TYPE_NAME: &'static str = "turtlebot4_msgs/msg/UserButton";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__turtlebot4_msgs__msg__UserButton() }
  }
}


#[link(name = "turtlebot4_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__turtlebot4_msgs__msg__UserDisplay() -> *const std::ffi::c_void;
}

#[link(name = "turtlebot4_msgs__rosidl_generator_c")]
extern "C" {
    fn turtlebot4_msgs__msg__UserDisplay__init(msg: *mut UserDisplay) -> bool;
    fn turtlebot4_msgs__msg__UserDisplay__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<UserDisplay>, size: usize) -> bool;
    fn turtlebot4_msgs__msg__UserDisplay__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<UserDisplay>);
    fn turtlebot4_msgs__msg__UserDisplay__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<UserDisplay>, out_seq: *mut rosidl_runtime_rs::Sequence<UserDisplay>) -> bool;
}

// Corresponds to turtlebot4_msgs__msg__UserDisplay
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// This message represents the header and 5 entries 
/// that are displayed on the Turtlebot4 display
/// selected_entry indicates which menu entry is currently selected

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct UserDisplay {

    // This member is not documented.
    #[allow(missing_docs)]
    pub ip: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub battery: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub entries: [rosidl_runtime_rs::String; 5],


    // This member is not documented.
    #[allow(missing_docs)]
    pub selected_entry: i32,

}



impl Default for UserDisplay {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !turtlebot4_msgs__msg__UserDisplay__init(&mut msg as *mut _) {
        panic!("Call to turtlebot4_msgs__msg__UserDisplay__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for UserDisplay {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { turtlebot4_msgs__msg__UserDisplay__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { turtlebot4_msgs__msg__UserDisplay__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { turtlebot4_msgs__msg__UserDisplay__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for UserDisplay {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for UserDisplay where Self: Sized {
  const TYPE_NAME: &'static str = "turtlebot4_msgs/msg/UserDisplay";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__turtlebot4_msgs__msg__UserDisplay() }
  }
}


