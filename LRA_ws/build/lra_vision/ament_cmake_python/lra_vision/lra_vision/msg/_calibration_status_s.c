// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from lra_vision:msg/CalibrationStatus.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "lra_vision/msg/detail/calibration_status__struct.h"
#include "lra_vision/msg/detail/calibration_status__functions.h"

#include "rosidl_runtime_c/string.h"
#include "rosidl_runtime_c/string_functions.h"

ROSIDL_GENERATOR_C_IMPORT
bool std_msgs__msg__header__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * std_msgs__msg__header__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool lra_vision__msg__calibration_status__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[53];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("lra_vision.msg._calibration_status.CalibrationStatus", full_classname_dest, 52) == 0);
  }
  lra_vision__msg__CalibrationStatus * ros_message = _ros_message;
  {  // header
    PyObject * field = PyObject_GetAttrString(_pymsg, "header");
    if (!field) {
      return false;
    }
    if (!std_msgs__msg__header__convert_from_py(field, &ros_message->header)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // state
    PyObject * field = PyObject_GetAttrString(_pymsg, "state");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->state, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // images_collected
    PyObject * field = PyObject_GetAttrString(_pymsg, "images_collected");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->images_collected = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // images_required
    PyObject * field = PyObject_GetAttrString(_pymsg, "images_required");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->images_required = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // images_maximum
    PyObject * field = PyObject_GetAttrString(_pymsg, "images_maximum");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->images_maximum = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }
  {  // current_rms_error
    PyObject * field = PyObject_GetAttrString(_pymsg, "current_rms_error");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->current_rms_error = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // best_rms_error
    PyObject * field = PyObject_GetAttrString(_pymsg, "best_rms_error");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->best_rms_error = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // mean_reprojection_error
    PyObject * field = PyObject_GetAttrString(_pymsg, "mean_reprojection_error");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->mean_reprojection_error = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // is_ready
    PyObject * field = PyObject_GetAttrString(_pymsg, "is_ready");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->is_ready = (Py_True == field);
    Py_DECREF(field);
  }
  {  // is_calibrated
    PyObject * field = PyObject_GetAttrString(_pymsg, "is_calibrated");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->is_calibrated = (Py_True == field);
    Py_DECREF(field);
  }
  {  // error_message
    PyObject * field = PyObject_GetAttrString(_pymsg, "error_message");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->error_message, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // progress
    PyObject * field = PyObject_GetAttrString(_pymsg, "progress");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->progress = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * lra_vision__msg__calibration_status__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of CalibrationStatus */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("lra_vision.msg._calibration_status");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "CalibrationStatus");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  lra_vision__msg__CalibrationStatus * ros_message = (lra_vision__msg__CalibrationStatus *)raw_ros_message;
  {  // header
    PyObject * field = NULL;
    field = std_msgs__msg__header__convert_to_py(&ros_message->header);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "header", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // state
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->state.data,
      strlen(ros_message->state.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "state", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // images_collected
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->images_collected);
    {
      int rc = PyObject_SetAttrString(_pymessage, "images_collected", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // images_required
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->images_required);
    {
      int rc = PyObject_SetAttrString(_pymessage, "images_required", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // images_maximum
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->images_maximum);
    {
      int rc = PyObject_SetAttrString(_pymessage, "images_maximum", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // current_rms_error
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->current_rms_error);
    {
      int rc = PyObject_SetAttrString(_pymessage, "current_rms_error", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // best_rms_error
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->best_rms_error);
    {
      int rc = PyObject_SetAttrString(_pymessage, "best_rms_error", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // mean_reprojection_error
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->mean_reprojection_error);
    {
      int rc = PyObject_SetAttrString(_pymessage, "mean_reprojection_error", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // is_ready
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->is_ready ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "is_ready", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // is_calibrated
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->is_calibrated ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "is_calibrated", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // error_message
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->error_message.data,
      strlen(ros_message->error_message.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "error_message", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // progress
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->progress);
    {
      int rc = PyObject_SetAttrString(_pymessage, "progress", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
