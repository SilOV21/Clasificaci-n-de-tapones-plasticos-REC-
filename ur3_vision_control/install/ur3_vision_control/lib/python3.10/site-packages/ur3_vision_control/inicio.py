import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
import math

class UR3SimpleMove(Node):

    def __init__(self):
        super().__init__('ur3_simple_move')
        
        # Publicador al controlador de trayectoria del UR3
        self.traj_pub = self.create_publisher(
            JointTrajectory,
            '/scaled_joint_trajectory_controller/joint_trajectory',
            10
        )

        # Definir los nombres de las articulaciones (orden estándar UR)
        self.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint',
        ]

        # ESPERAR A QUE HAYA SUSCRIPTORES
        self.get_logger().info('Esperando al controlador...')
        while self.traj_pub.get_subscription_count() == 0:
            rclpy.spin_once(self, timeout_sec=0.1)

        # EJECUTAR MOVIMIENTO
        self.move_robot()

    def move_robot(self):
        # ---------------------------------------------------------
        # CONFIGURA AQUÍ TUS ÁNGULOS (en radianes)
        # ---------------------------------------------------------
        target_joints = [
            math.radians(-88), # Base
            math.radians(-99),# Shoulder
            math.radians(-60),  # Elbow
            math.radians(-109), # Wrist 1
            math.radians(90),  # Wrist 2
            math.radians(330)    # Wrist 3
        ]
        
        tiempo_de_movimiento = 5.0 # Segundos que tardará en llegar

        # Crear el mensaje de trayectoria
        msg = JointTrajectory()
        msg.joint_names = self.joint_names

        point = JointTrajectoryPoint()
        point.positions = target_joints
        point.time_from_start.sec = int(tiempo_de_movimiento)
        point.time_from_start.nanosec = int((tiempo_de_movimiento % 1) * 1e9)

        msg.points.append(point)

        self.get_logger().info(f'Enviando robot a: {target_joints}')
        self.traj_pub.publish(msg)
        self.get_logger().info('Movimiento enviado. Cerrando nodo...')

def main(args=None):
    rclpy.init(args=args)
    node = UR3SimpleMove()
    # Le damos un pequeño tiempo para asegurar que el mensaje sale por la red
    rclpy.spin_once(node, timeout_sec=1.0)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
