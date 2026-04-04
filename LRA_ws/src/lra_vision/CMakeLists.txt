cmake_minimum_required(VERSION 3.16)
project(lra_vision LANGUAGES C CXX)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic -Wno-unused-parameter)
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

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

find_package(OpenCV REQUIRED COMPONENTS
  core
  imgproc
  imgcodecs
  highgui
  calib3d
  videoio
)

find_package(yaml-cpp REQUIRED)

find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  msg/CameraInfo.msg
  msg/CalibrationStatus.msg
  srv/CalibrateCamera.srv
  DEPENDENCIES std_msgs sensor_msgs geometry_msgs builtin_interfaces
)

ament_export_dependencies(rosidl_default_runtime)

include_directories(
  include
  ${OpenCV_INCLUDE_DIRS}
)

add_library(lra_camera_utils SHARED
  src/utils/camera_detector.cpp
  src/utils/camera_calibration.cpp
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
)

ament_target_dependencies(lra_tf_utils
  rclcpp
  geometry_msgs
  tf2
  tf2_ros
  tf2_geometry_msgs
)

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

rosidl_target_interfaces(camera_calibrator_node ${PROJECT_NAME} "rosidl_typesupport_cpp")

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

add_executable(camera_manager_node
  src/nodes/camera_manager_node.cpp
)

target_link_libraries(camera_manager_node
  lra_camera_utils
)

ament_target_dependencies(camera_manager_node
  rclcpp
  sensor_msgs
  std_srvs
)

install(TARGETS
  lra_camera_utils
  lra_tf_utils
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

install(TARGETS
  camera_calibrator_node
  camera_tf_broadcaster_node
  aruco_detector_node
  camera_manager_node
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
  DESTINATION share/${PROJECT_NAME}
)

install(FILES
  package.xml
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/camera_info_publisher.py
  scripts/aruco_test_publisher.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()

  find_package(ament_cmake_gtest REQUIRED)

  ament_add_gtest(test_camera_detector
    test/test_camera_detector.cpp
  )
  target_link_libraries(test_camera_detector
    lra_camera_utils
    ${OpenCV_LIBS}
  )

  ament_add_gtest(test_camera_calibration
    test/test_camera_calibration.cpp
  )
  target_link_libraries(test_camera_calibration
    lra_camera_utils
    ${OpenCV_LIBS}
  )

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
endif()

ament_package()
