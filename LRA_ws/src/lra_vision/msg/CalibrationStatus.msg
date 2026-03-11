# =============================================================================
# LRA Vision Package - Calibration Status Message
# Status message for calibration process
# ROS2 Jazzy Jalisco
# =============================================================================

# Header with timestamp
std_msgs/Header header

# Calibration state
string state  # "idle", "collecting", "calibrating", "calibrated", "error"

# Number of images collected
int32 images_collected
int32 images_required
int32 images_maximum

# Calibration quality metrics
float64 current_rms_error
float64 best_rms_error
float64 mean_reprojection_error

# Ready status
bool is_ready  # True when enough images collected
bool is_calibrated  # True when calibration complete

# Error message (if any)
string error_message

# Progress percentage (0-100)
float64 progress