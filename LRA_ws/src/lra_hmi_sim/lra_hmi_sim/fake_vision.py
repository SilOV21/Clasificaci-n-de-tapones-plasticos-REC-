"""Fake vision pipeline: publishes counters, colors, and synthetic images."""
from __future__ import annotations

import random
import time

import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy, QoSHistoryPolicy, QoSProfile, QoSReliabilityPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import Int32, String

from .image_factory import make_cap_frame, make_debug_frame


COLOR_TO_BOX = {
    1: "rojo",
    2: "azul",
    3: "amarillo",
    4: "blanco",
}


class FakeVision(Node):

    def __init__(self):
        super().__init__("fake_vision")
        self.declare_parameter("num_boxes", 4)
        self.declare_parameter("detection_period_s", 2.0)
        self.declare_parameter("image_rate_hz", 10.0)

        self._num_boxes = int(self.get_parameter("num_boxes").value)
        det_period = float(self.get_parameter("detection_period_s").value)
        img_rate = float(self.get_parameter("image_rate_hz").value)

        self._bridge = CvBridge()
        self._total = 0
        self._last_box = 1
        self._last_color = "rojo"
        self._t0 = time.time()
        random.seed(0)

        latched = QoSProfile(
            depth=1,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
            history=QoSHistoryPolicy.KEEP_LAST,
        )
        sensor = QoSProfile(
            depth=5,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
            history=QoSHistoryPolicy.KEEP_LAST,
        )

        self._pub_num_boxes = self.create_publisher(
            Int32, "/clasificador/num_cajas", latched
        )
        self._pub_total = self.create_publisher(Int32, "/tapones/cantidad", 10)
        self._pub_box = self.create_publisher(Int32, "/tapones/caja_asignada", 10)
        self._pub_color = self.create_publisher(String, "/vision_color", 10)
        self._pub_raw = self.create_publisher(Image, "/image_raw", sensor)
        self._pub_debug = self.create_publisher(Image, "/tapones/imagen_debug", sensor)

        num_msg = Int32()
        num_msg.data = self._num_boxes
        self._pub_num_boxes.publish(num_msg)

        self._detect_timer = self.create_timer(det_period, self._on_detect)
        self._image_timer = self.create_timer(1.0 / max(img_rate, 1.0), self._on_image)
        self.get_logger().info(
            f"fake_vision online: num_boxes={self._num_boxes}, "
            f"detection every {det_period}s, images at {img_rate} Hz"
        )

    def _on_detect(self) -> None:
        self._last_box = random.randint(1, self._num_boxes)
        self._last_color = COLOR_TO_BOX.get(self._last_box, "blanco")
        self._total += 1

        msg_box = Int32()
        msg_box.data = self._last_box
        self._pub_box.publish(msg_box)

        msg_total = Int32()
        msg_total.data = self._total
        self._pub_total.publish(msg_total)

        msg_color = String()
        msg_color.data = self._last_color
        self._pub_color.publish(msg_color)

    def _on_image(self) -> None:
        phase = (time.time() - self._t0) * 1.2
        raw = make_cap_frame(self._last_color, phase)
        dbg = make_debug_frame(self._last_color, self._last_box, phase)
        try:
            raw_msg = self._bridge.cv2_to_imgmsg(raw, encoding="bgr8")
            raw_msg.header.stamp = self.get_clock().now().to_msg()
            self._pub_raw.publish(raw_msg)
            dbg_msg = self._bridge.cv2_to_imgmsg(dbg, encoding="bgr8")
            dbg_msg.header.stamp = raw_msg.header.stamp
            self._pub_debug.publish(dbg_msg)
        except Exception as exc:
            self.get_logger().warn(f"image publish failed: {exc}")


def main(args=None):
    rclpy.init(args=args)
    node = FakeVision()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
