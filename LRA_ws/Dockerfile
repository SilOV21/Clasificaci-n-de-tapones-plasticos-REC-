FROM ros:humble

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-CE
ENV LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y \
    ros-humble-v4l2-camera \
    ros-humble-camera-calibration-parsers \
    ros-humble-camera-info-manager \
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    ros-humble-tf2 \
    ros-humble-tf2-ros \
    ros-humble-tf2-geometry-msgs \
    ros-humble-vision-opencv \
    ros-humble-camera-calibration \
    ros-humble-rviz2 \
    ros-humble-tf2-tools \
    ros-humble-ur-msgs \
    ros-humble-ur-robot-driver \
    ros-humble-ur-calibration \
    ros-humble-ur-controllers \
    ros-humble-ur-moveit-config \
    ros-humble-robot-state-publisher \
    ros-humble-visualization-msgs \
    ros-humble-std-srvs \
    ros-humble-moveit-msgs \
    ros-humble-trajectory-msgs \
    ros-humble-shape-msgs \
    ros-humble-rosidl-default-generators \
    ros-humble-rosidl-default-runtime \
    ros-humble-rqt-image-view \
    ros-humble-builtin-interfaces \
    ros-humble-joint-state-publisher-gui \
    python3-opencv \
    python3-numpy \
    python3-pip \
    python3-tk \
    python3-yaml \
    libyaml-cpp-dev \
    libopencv-dev \
    libopencv-contrib-dev \
    git \
    xvfb \
    iputils-ping \
    net-tools \
    iproute2 \
    dnsutils \
    curl \
    tcpdump \
    nmap \
    netcat-openbsd \
    ros-humble-joint-state-publisher \
    ros-humble-xacro \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install mcap-ros2-support

ENV LOCAL_IP=169.254.12.10
EXPOSE 50002

WORKDIR /root/lra_ws

COPY src/ src/
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

# Add ROS and workspace sourcing to .bashrc for interactive shells
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo "if [ -f /root/lra_ws/install/setup.bash ]; then source /root/lra_ws/install/setup.bash; fi" >> /root/.bashrc

ENTRYPOINT ["/entrypoint.sh"]

CMD ["bash"]
