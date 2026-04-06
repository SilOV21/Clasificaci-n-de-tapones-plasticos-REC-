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
    python3-opencv \
    python3-numpy \
    python3-pip \
    libyaml-cpp-dev \
    libopencv-dev \
    git \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/lra_ws

COPY src/ src/
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

RUN bash -c "source /opt/ros/humble/setup.bash"

RUN chmod +x /entrypoint.sh

CMD ["bash"]
