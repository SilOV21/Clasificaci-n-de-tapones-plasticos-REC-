import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import Point
from std_msgs.msg import Bool
from ur_msgs.srv import SetIO  
import time

class UR3RealControl(Node):
    def __init__(self):
        super().__init__('ur3_controller')

      
        self.trajectory_pub = self.create_publisher(
            JointTrajectory,
            '/scaled_joint_trajectory_controller/joint_trajectory',
            10
        )

    
        self.io_client = self.create_client(SetIO, '/io_and_status_controller/set_io')
        while not self.io_client.wait_for_service(timeout_sec=1.0):
           self.get_logger().info('Esperando al servicio de I/O del robot...')


        self.subscription = self.create_subscription(
            Point, 
            '/vision_target', 
            self.vision_callback, 
            10
        )
        

        self.vision_control_pub = self.create_publisher(Bool, '/vision_enable', 10)

    
        self.joint_names = [
            "shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint",
            "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"
        ]
        self.home_position = [0.0, -1.57, 1.57, -1.57, -1.57, 0.0]

    def control_zimmer(self, action: str):
        """ Controla la pinza Zimmer mediante salidas digitales """
        req = SetIO.Request()
        req.fun = 1 
        req.pin = 0  
        
        if action == "CLOSE":
            req.state = 1.0  
        else:
            req.state = 0.0  
            
        self.io_client.call_async(req)
        self.get_logger().info(f"Pinza Zimmer: {action}")

    def send_movement(self, positions, duration):
       
        msg = JointTrajectory()
        msg.joint_names = self.joint_names
        
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start.sec = duration
        
        msg.points = [point]
        self.trajectory_pub.publish(msg)

    def vision_callback(self, msg):
        
        #bloquear la visión mientraas se va a mover
        self.vision_control_pub.publish(Bool(data=False))
        self.get_logger().info("Iniciando secuencia real de Pick & Place")

        
        pan = msg.x * 2.0
        elbow = 1.1 + msg.y
        target = [pan, -1.0, elbow, -1.5, -1.5, 0.2]
        
        self.send_movement(target, 5) 
        time.sleep(5.5) #esperar a que termine el movimiento

        
        self.control_zimmer("CLOSE")
        time.sleep(1.0) 

        #volver a home_position
        self.send_movement(self.home_position, 4)
        time.sleep(4.5)

        self.control_zimmer("OPEN")
        time.sleep(1.0)

        # cuando se acaba el movimiento se vuelve a activar la vision
        self.vision_control_pub.publish(Bool(data=True))
        self.get_logger().info("Secuencia terminada. Esperando nuevo objeto...")

def main(args=None):
    rclpy.init(args=args)
    node = UR3RealControl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
