# =============================================================================
# LRA Vision Package - CMakeLists.txt
# Vision subsystem for REC Project (Plastic Cap Classification)
# ROS2 Jazzy Jalisco - C++17
# =============================================================================
cmake_minimum_required(VERSION 3.16)
project(lra_vision LANGUAGES C CXX)

# =============================================================================
# COMPILER SETTINGS
# =============================================================================
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic -Wno-unused-parameter)
endif()

# C++17 standard required
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# =============================================================================
# FIND DEPENDENCIES
# =============================================================================
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(image_transport REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(camera_info_manager REQUIRED)
find_package(camera_calibration_parsers REQUIRED)
find_package(rclcpp_components REQUIRED)

# OpenCV
find_package(OpenCV REQUIRED COMPONENTS
  core
  imgproc
  imgcodecs
  highgui
  calib3d
  videoio
)

# YAML-CPP for configuration files
find_package(yaml-cpp REQUIRED)

# =============================================================================
# INTERFACES (Custom Messages and Services)
# =============================================================================
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  msg/CameraInfo.msg
  msg/CalibrationStatus.msg
  srv/GetCameraDevice.srv
  srv/CalibrateCamera.srv
  DEPENDENCIES std_msgs sensor_msgs geometry_msgs builtin_interfaces
)

ament_export_dependencies(rosidl_default_runtime)

# =============================================================================
# INCLUDE DIRECTORIES
# =============================================================================
include_directories(
  include
  ${OpenCV_INCLUDE_DIRS}
)

# =============================================================================
# LIBRARIES
# =============================================================================

# Camera Utilities Library
add_library(lra_camera_utils SHARED
  src/utils/camera_detector.cpp
  src/utils/camera_calibration.cpp
  src/utils/image_processor.cpp
  src/utils/aruco_detector.cpp
)

target_include_directories(lra_camera_utils PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

ament_target_dependencies(lra_camera_utils
  rclcpp
  sensor_msgs
  image_transport
  cv_bridge
  tf2
  tf2_ros
)

target_link_libraries(lra_camera_utils
  ${OpenCV_LIBS}
  yaml-cpp
)

# TF Utilities Library
add_library(lra_tf_utils SHARED
  src/tf/camera_tf_broadcaster.cpp
  src/tf/ur3_camera_transform.cpp
)

target_include_directories(lra_tf_utils PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

target_link_libraries(lra_tf_utils
  ${OpenCV_LIBS}
  yaml-cpp
  tf2::tf2
  tf2_ros::tf2_ros
  tf2_geometry_msgs::tf2_geometry_msgs
)

ament_target_dependencies(lra_tf_utils
  rclcpp
  geometry_msgs
  tf2
  tf2_ros
  tf2_geometry_msgs
)

# =============================================================================
# NODES
# =============================================================================

# Camera Publisher Node - Publishes camera images from v4l2 device
add_executable(camera_publisher_node
  src/nodes/camera_publisher_node.cpp
)

target_link_libraries(camera_publisher_node
  lra_camera_utils
  ${OpenCV_LIBS}
)

ament_target_dependencies(camera_publisher_node
  rclcpp
  sensor_msgs
  image_transport
  camera_info_manager
  rclcpp_components
  std_srvs
)

# Camera Calibrator Node - Performs camera calibration using OpenCV
add_executable(camera_calibrator_node
  src/nodes/camera_calibrator_node.cpp
)

target_link_libraries(camera_calibrator_node
  lra_camera_utils
  ${OpenCV_LIBS}
  yaml-cpp
)

ament_target_dependencies(camera_calibrator_node
  rclcpp
  sensor_msgs
  image_transport
  cv_bridge
  camera_calibration_parsers
  std_srvs
)

# Camera TF Broadcaster Node - Publishes TF for camera-UR3 relationship
add_executable(camera_tf_broadcaster_node
  src/nodes/camera_tf_broadcaster_node.cpp
)

target_link_libraries(camera_tf_broadcaster_node
  lra_tf_utils
)

ament_target_dependencies(camera_tf_broadcaster_node
  rclcpp
  geometry_msgs
  tf2
  tf2_ros
  std_srvs
)

# ArUco Detector Node - Detects ArUco markers for hand-eye calibration
add_executable(aruco_detector_node
  src/nodes/aruco_detector_node.cpp
)

target_link_libraries(aruco_detector_node
  lra_camera_utils
  ${OpenCV_LIBS}
)

ament_target_dependencies(aruco_detector_node
  rclcpp
  sensor_msgs
  cv_bridge
  geometry_msgs
  visualization_msgs
)

# =============================================================================
# INSTALL TARGETS
# =============================================================================
install(TARGETS
  lra_camera_utils
  lra_tf_utils
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

install(TARGETS
  camera_publisher_node
  camera_calibrator_node
  camera_tf_broadcaster_node
  aruco_detector_node
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  include/
  DESTINATION include
)

install(DIRECTORY
  launch
  config
  urdf
  rviz
  DESTINATION share/${PROJECT_NAME}
)

install(FILES
  package.xml
  DESTINATION share/${PROJECT_NAME}
)

# =============================================================================
# TESTS (GTest/Boost)
# =============================================================================
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
  
  find_package(ament_cmake_gtest REQUIRED)
  
  # Test Camera Device Detector
  ament_add_gtest(test_camera_detector
    test/test_camera_detector.cpp
  )
  target_link_libraries(test_camera_detector
    lra_camera_utils
    ${OpenCV_LIBS}
  )
  
  # Test Camera Calibration
  ament_add_gtest(test_camera_calibration
    test/test_camera_calibration.cpp
  )
  target_link_libraries(test_camera_calibration
    lra_camera_utils
    ${OpenCV_LIBS}
  )
  
  # Test TF Broadcaster
  ament_add_gtest(test_tf_broadcaster
    test/test_tf_broadcaster.cpp
  )
  target_link_libraries(test_tf_broadcaster
    lra_tf_utils
  )
  ament_target_dependencies(test_tf_broadcaster
    tf2
    tf2_ros
    tf2_geometry_msgs
  )
  
  # Test Image Processor
  ament_add_gtest(test_image_processor
    test/test_image_processor.cpp
  )
  target_link_libraries(test_image_processor
    lra_camera_utils
    ${OpenCV_LIBS}
  )
  
endif()

# =============================================================================
# AMENT PACKAGE
# =============================================================================
ament_package()