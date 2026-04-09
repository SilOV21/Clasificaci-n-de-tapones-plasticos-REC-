# generated from rosidl_generator_py/resource/_idl.py.em
# with input from lra_vision:msg/CalibrationStatus.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_CalibrationStatus(type):
    """Metaclass of message 'CalibrationStatus'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('lra_vision')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'lra_vision.msg.CalibrationStatus')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__calibration_status
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__calibration_status
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__calibration_status
            cls._TYPE_SUPPORT = module.type_support_msg__msg__calibration_status
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__calibration_status

            from std_msgs.msg import Header
            if Header.__class__._TYPE_SUPPORT is None:
                Header.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class CalibrationStatus(metaclass=Metaclass_CalibrationStatus):
    """Message class 'CalibrationStatus'."""

    __slots__ = [
        '_header',
        '_state',
        '_images_collected',
        '_images_required',
        '_images_maximum',
        '_current_rms_error',
        '_best_rms_error',
        '_mean_reprojection_error',
        '_is_ready',
        '_is_calibrated',
        '_error_message',
        '_progress',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'state': 'string',
        'images_collected': 'int32',
        'images_required': 'int32',
        'images_maximum': 'int32',
        'current_rms_error': 'double',
        'best_rms_error': 'double',
        'mean_reprojection_error': 'double',
        'is_ready': 'boolean',
        'is_calibrated': 'boolean',
        'error_message': 'string',
        'progress': 'double',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        self.state = kwargs.get('state', str())
        self.images_collected = kwargs.get('images_collected', int())
        self.images_required = kwargs.get('images_required', int())
        self.images_maximum = kwargs.get('images_maximum', int())
        self.current_rms_error = kwargs.get('current_rms_error', float())
        self.best_rms_error = kwargs.get('best_rms_error', float())
        self.mean_reprojection_error = kwargs.get('mean_reprojection_error', float())
        self.is_ready = kwargs.get('is_ready', bool())
        self.is_calibrated = kwargs.get('is_calibrated', bool())
        self.error_message = kwargs.get('error_message', str())
        self.progress = kwargs.get('progress', float())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.header != other.header:
            return False
        if self.state != other.state:
            return False
        if self.images_collected != other.images_collected:
            return False
        if self.images_required != other.images_required:
            return False
        if self.images_maximum != other.images_maximum:
            return False
        if self.current_rms_error != other.current_rms_error:
            return False
        if self.best_rms_error != other.best_rms_error:
            return False
        if self.mean_reprojection_error != other.mean_reprojection_error:
            return False
        if self.is_ready != other.is_ready:
            return False
        if self.is_calibrated != other.is_calibrated:
            return False
        if self.error_message != other.error_message:
            return False
        if self.progress != other.progress:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def header(self):
        """Message field 'header'."""
        return self._header

    @header.setter
    def header(self, value):
        if __debug__:
            from std_msgs.msg import Header
            assert \
                isinstance(value, Header), \
                "The 'header' field must be a sub message of type 'Header'"
        self._header = value

    @builtins.property
    def state(self):
        """Message field 'state'."""
        return self._state

    @state.setter
    def state(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'state' field must be of type 'str'"
        self._state = value

    @builtins.property
    def images_collected(self):
        """Message field 'images_collected'."""
        return self._images_collected

    @images_collected.setter
    def images_collected(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'images_collected' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'images_collected' field must be an integer in [-2147483648, 2147483647]"
        self._images_collected = value

    @builtins.property
    def images_required(self):
        """Message field 'images_required'."""
        return self._images_required

    @images_required.setter
    def images_required(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'images_required' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'images_required' field must be an integer in [-2147483648, 2147483647]"
        self._images_required = value

    @builtins.property
    def images_maximum(self):
        """Message field 'images_maximum'."""
        return self._images_maximum

    @images_maximum.setter
    def images_maximum(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'images_maximum' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'images_maximum' field must be an integer in [-2147483648, 2147483647]"
        self._images_maximum = value

    @builtins.property
    def current_rms_error(self):
        """Message field 'current_rms_error'."""
        return self._current_rms_error

    @current_rms_error.setter
    def current_rms_error(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'current_rms_error' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'current_rms_error' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._current_rms_error = value

    @builtins.property
    def best_rms_error(self):
        """Message field 'best_rms_error'."""
        return self._best_rms_error

    @best_rms_error.setter
    def best_rms_error(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'best_rms_error' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'best_rms_error' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._best_rms_error = value

    @builtins.property
    def mean_reprojection_error(self):
        """Message field 'mean_reprojection_error'."""
        return self._mean_reprojection_error

    @mean_reprojection_error.setter
    def mean_reprojection_error(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'mean_reprojection_error' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'mean_reprojection_error' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._mean_reprojection_error = value

    @builtins.property
    def is_ready(self):
        """Message field 'is_ready'."""
        return self._is_ready

    @is_ready.setter
    def is_ready(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'is_ready' field must be of type 'bool'"
        self._is_ready = value

    @builtins.property
    def is_calibrated(self):
        """Message field 'is_calibrated'."""
        return self._is_calibrated

    @is_calibrated.setter
    def is_calibrated(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'is_calibrated' field must be of type 'bool'"
        self._is_calibrated = value

    @builtins.property
    def error_message(self):
        """Message field 'error_message'."""
        return self._error_message

    @error_message.setter
    def error_message(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'error_message' field must be of type 'str'"
        self._error_message = value

    @builtins.property
    def progress(self):
        """Message field 'progress'."""
        return self._progress

    @progress.setter
    def progress(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'progress' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'progress' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._progress = value
