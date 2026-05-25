FROM ros:humble

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    QT_X11_NO_MITSHM=1 \
    LOCAL_IP=169.254.12.10

RUN apt-get update && apt-get install -y --no-install-recommends \
        ros-humble-ur-robot-driver \
        ros-humble-ur-moveit-config \
        ros-humble-v4l2-camera \
        ros-humble-robot-state-publisher \
        ros-humble-cv-bridge \
        ros-humble-tf2-ros \
        ros-humble-xacro \
        ros-humble-image-transport \
        ros-humble-camera-info-manager \
        ros-humble-camera-calibration-parsers \
        ros-humble-tf2 \
        ros-humble-tf2-geometry-msgs \
        ros-humble-vision-opencv \
        ros-humble-joint-state-publisher \
        ros-humble-visualization-msgs \
        libopencv-dev \
        libopencv-contrib-dev \
        libyaml-cpp-dev \
        python3-pyqt5 \
        python3-opencv \
        python3-numpy \
        python3-yaml \
        iputils-ping \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/lra_ws

COPY src/        ./src/
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo "[ -f /root/lra_ws/install/setup.bash ] && source /root/lra_ws/install/setup.bash" >> /root/.bashrc

EXPOSE 50002

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["ros2", "run", "lra_hmi", "lra_hmi"]
