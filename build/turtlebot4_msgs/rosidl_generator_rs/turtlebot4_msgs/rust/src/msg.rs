#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to turtlebot4_msgs__msg__UserLed
/// This message sets the state of the user LEDs
/// Blink period is the time in milliseconds during which the ON/OFF cycle occurs
/// The duty cycle represents the percentage of the blink period that the LED is ON
/// A duty cycle of 1.0 would set the LED to always be ON, whereas a duty cycle of 0.0 is always OFF
/// A blink period of 1000ms with a duty cycle of 0.6 will have the LED turn ON for 600ms, 
/// then OFF for 400ms

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::UserLed::default())
  }
}

impl rosidl_runtime_rs::Message for UserLed {
  type RmwMsg = super::msg::rmw::UserLed;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        led: msg.led,
        color: msg.color,
        blink_period: msg.blink_period,
        duty_cycle: msg.duty_cycle,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      led: msg.led,
      color: msg.color,
      blink_period: msg.blink_period,
      duty_cycle: msg.duty_cycle,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      led: msg.led,
      color: msg.color,
      blink_period: msg.blink_period,
      duty_cycle: msg.duty_cycle,
    }
  }
}


// Corresponds to turtlebot4_msgs__msg__UserButton
/// This message relays the state of the user buttons
/// Each button is represented with a boolean, were True indicates the button is pressed

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct UserButton {

    // This member is not documented.
    #[allow(missing_docs)]
    pub button: [bool; 4],

}



impl Default for UserButton {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::UserButton::default())
  }
}

impl rosidl_runtime_rs::Message for UserButton {
  type RmwMsg = super::msg::rmw::UserButton;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        button: msg.button,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        button: msg.button,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      button: msg.button,
    }
  }
}


// Corresponds to turtlebot4_msgs__msg__UserDisplay
/// This message represents the header and 5 entries 
/// that are displayed on the Turtlebot4 display
/// selected_entry indicates which menu entry is currently selected

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct UserDisplay {

    // This member is not documented.
    #[allow(missing_docs)]
    pub ip: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub battery: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub entries: [std::string::String; 5],


    // This member is not documented.
    #[allow(missing_docs)]
    pub selected_entry: i32,

}



impl Default for UserDisplay {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::UserDisplay::default())
  }
}

impl rosidl_runtime_rs::Message for UserDisplay {
  type RmwMsg = super::msg::rmw::UserDisplay;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        ip: msg.ip.as_str().into(),
        battery: msg.battery.as_str().into(),
        entries: msg.entries
          .map(|elem| elem.as_str().into()),
        selected_entry: msg.selected_entry,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        ip: msg.ip.as_str().into(),
        battery: msg.battery.as_str().into(),
        entries: msg.entries
          .iter()
          .map(|elem| elem.as_str().into())
          .collect::<Vec<_>>()
          .try_into()
          .unwrap(),
      selected_entry: msg.selected_entry,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      ip: msg.ip.to_string(),
      battery: msg.battery.to_string(),
      entries: msg.entries
        .map(|elem| elem.to_string()),
      selected_entry: msg.selected_entry,
    }
  }
}


