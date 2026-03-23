#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
import numpy as np
from cv_bridge import CvBridge

class ImagePublisher(Node):
    def __init__(self):
        super().__init__('image_publisher')
        self.pub = self.create_publisher(Image, '/camera/image_raw', 10)
        self.bridge = CvBridge()

        # Target dimensions from calibration (width=371, height=526)
        self.target_width = 371
        self.target_height = 526

        # Load all 3 ArUco marker images
        base_path = '/home/asil/Desktop/Clasificaci-n-de-tapones-plasticos-REC-/LRA_ws'
        self.marker_ids = [0, 1, 2]
        self.images = []

        for marker_id in self.marker_ids:
            image_path = f'{base_path}/aruco-marker-ID={marker_id}.png'
            self.get_logger().info(f'Loading marker {marker_id} from: {image_path}')
            img = cv2.imread(image_path)
            if img is None:
                self.get_logger().error(f'Failed to load marker {marker_id} from {image_path}!')
            else:
                # Resize keeping aspect ratio, then pad to target size
                img_processed = self.resize_and_pad(img)
                self.get_logger().info(f'Loaded marker {marker_id}: {img.shape[1]}x{img.shape[0]} -> processed to {self.target_width}x{self.target_height}')
                self.images.append((marker_id, img_processed))

        if not self.images:
            self.get_logger().error('No marker images loaded!')
            return

        self.current_index = 0
        self.switch_interval = 3.0  # Switch every 3 seconds
        self.last_switch = self.get_clock().now()

        # Timer: publish at 10 Hz
        self.timer = self.create_timer(0.1, self.publish_image)

    def resize_and_pad(self, img):
        """Resize image keeping aspect ratio and pad to target size."""
        h, w = img.shape[:2]

        # Calculate scale to fit within target dimensions
        scale = min(self.target_width / w, self.target_height / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        # Resize
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Create padded image (white background)
        padded = np.full((self.target_height, self.target_width, 3), 255, dtype=np.uint8)

        # Center the resized image
        y_offset = (self.target_height - new_h) // 2
        x_offset = (self.target_width - new_w) // 2

        padded[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized

        return padded

    def publish_image(self):
        # Check if it's time to switch markers
        now = self.get_clock().now()
        elapsed = (now - self.last_switch).nanoseconds / 1e9

        if elapsed >= self.switch_interval:
            self.current_index = (self.current_index + 1) % len(self.images)
            self.last_switch = now
            marker_id = self.images[self.current_index][0]
            self.get_logger().info(f'Switched to marker ID={marker_id}')

        # Get current image
        marker_id, img = self.images[self.current_index]

        # Create fresh message with updated timestamp
        msg = self.bridge.cv2_to_imgmsg(img, encoding='bgr8')
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera'
        self.pub.publish(msg)
        self.get_logger().info(f'Published marker ID={marker_id}', throttle_duration_sec=1.0)

def main():
    rclpy.init()
    node = ImagePublisher()
    if not node.images:
        return 1
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
