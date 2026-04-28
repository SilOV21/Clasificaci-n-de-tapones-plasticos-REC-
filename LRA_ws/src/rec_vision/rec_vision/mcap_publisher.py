#!/usr/bin/env python3
"""
mcap_publisher.py
Publica las imagenes del bag tapones_nuevo.mcap como topic /image_raw
Uso: python3 mcap_publisher.py
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from mcap_ros2.reader import read_ros2_messages
import time

BAG_PATH = '/home/delia/Documents/MUAR/ProyectoREC/rec_ws/tapones/tapones_nuevo.mcap/tapones_nuevo.mcap_0.mcap'
TOPIC    = '/image_raw'
FPS      = 30.0

class McapPublisher(Node):
    def __init__(self):
        super().__init__('mcap_publisher')
        self.pub = self.create_publisher(Image, TOPIC, 10)
        self.get_logger().info(f'Leyendo bag: {BAG_PATH}')
        self.get_logger().info(f'Publicando en: {TOPIC} a {FPS} fps')
        self.publicar()

    def convertir_imagen(self, msg_dinamico):
        """Convierte el mensaje dinamico de mcap al tipo ROS2 nativo."""
        img = Image()
        img.header.stamp.sec     = msg_dinamico.header.stamp.sec
        img.header.stamp.nanosec = msg_dinamico.header.stamp.nanosec
        img.header.frame_id      = msg_dinamico.header.frame_id
        img.height               = msg_dinamico.height
        img.width                = msg_dinamico.width
        img.encoding             = msg_dinamico.encoding
        img.is_bigendian         = msg_dinamico.is_bigendian
        img.step                 = msg_dinamico.step
        img.data                 = bytes(msg_dinamico.data)
        return img

    def publicar(self):
        delay = 1.0 / FPS
        while rclpy.ok():
            count = 0
            for msg_obj in read_ros2_messages(BAG_PATH, topics=[TOPIC]):
                if not rclpy.ok():
                    break
                img_ros = self.convertir_imagen(msg_obj.ros_msg)
                self.pub.publish(img_ros)
                count += 1
                rclpy.spin_once(self, timeout_sec=0)
                time.sleep(delay)
            self.get_logger().info(
                f'Vuelta completada ({count} frames). Reiniciando...')

def main(args=None):
    rclpy.init(args=args)
    node = McapPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
