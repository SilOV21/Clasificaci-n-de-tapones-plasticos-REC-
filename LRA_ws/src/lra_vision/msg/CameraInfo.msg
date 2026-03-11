# =============================================================================
# LRA Vision Package - Camera Info Message
# Custom message for camera calibration information
# ROS2 Jazzy Jalisco
# =============================================================================

# Standard camera info message (sensor_msgs/CameraInfo)
# This is an extended version for calibration status

std_msgs/Header header

# Camera identification
string camera_name

# Calibration status
bool is_calibrated
float64 rms_error
float64 reprojection_error
int32 images_used

# Calibration timestamp
builtin_interfaces/Time calibration_time

# Image dimensions
int32 image_width
int32 image_height

# Camera matrix (3x3)
float64[] camera_matrix  # [fx, 0, cx, 0, fy, cy, 0, 0, 1]

# Distortion coefficients
float64[] distortion_coefficients  # [k1, k2, p1, p2, k3]

# Distortion model
string distortion_model  # "plumb_bob", "rational_polynomial", etc.