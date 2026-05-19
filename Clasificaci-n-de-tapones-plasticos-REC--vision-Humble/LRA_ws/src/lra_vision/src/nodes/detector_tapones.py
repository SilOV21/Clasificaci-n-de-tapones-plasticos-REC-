#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import Point
from std_msgs.msg import Int32, Float32
from cv_bridge import CvBridge
from collections import deque
import cv2
import numpy as np
import tf2_ros
from rclpy.duration import Duration

class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')

        # --- PARÁMETROS CONFIGURABLES ORIGINALES ---
        self.declare_parameter('min_radius', 18)
        self.declare_parameter('max_radius', 27)
        self.declare_parameter('min_dist', 40)
        self.declare_parameter('hough_param1', 30)
        self.declare_parameter('hough_param2', 27)
        self.declare_parameter('show_debug', True)
        self.declare_parameter('image_topic', '/image_raw')
        self.declare_parameter('target_frame', 'base_link')
        self.declare_parameter('camera_frame', 'camera_optical_frame')
        
        # --- NUEVOS PARÁMETROS DE ESTABILIDAD ---
        self.declare_parameter('frames_muestreo', 30) 

        # --- CONFIGURACIÓN PNP / GEOMETRÍA ---
        self.camera_matrix = np.array([[1000.0, 0.0, 320.0], [0.0, 1000.0, 240.0], [0.0, 0.0, 1.0]], dtype=np.float32)
        self.dist_coeffs = np.zeros((5, 1))

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Historiales y Estados
        self.pos_history = deque(maxlen=10)
        self.cantidad_historial = deque(maxlen=5)
        self.acumulador_muestreo = [] 
        self.contador_muestreo = 0
        self.buscando_objetivo = True
        self.objetivo_fijado = None

        self.bridge = CvBridge()
        self.sub_info = self.create_subscription(CameraInfo, '/camera/camera_info', self.info_callback, 10)
        self.subscription = self.create_subscription(Image, self.get_parameter('image_topic').value, self.image_callback, 10)

        self.pub_robot_pos = self.create_publisher(Point, '/ur3/target_point', 10)
        self.pub_target_diameter = self.create_publisher(Float32, '/ur3/target_diameter', 10)
        self.pub_count = self.create_publisher(Int32, '/tapones/cantidad', 10)
        self.pub_debug_img = self.create_publisher(Image, '/tapones/imagen_debug', 10)

        self.get_logger().info('Nodo UR3 iniciado: Analizando estabilidad de tapones...')

    def info_callback(self, msg):
        self.camera_matrix = np.array(msg.k).reshape((3, 3))
        self.dist_coeffs = np.array(msg.d)

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        
        # 1. Tu detección original con ROI y Caja
        circles, debug_img = self.detectar_tapones(frame)

        # 2. Estabilizar cantidad
        self.cantidad_historial.append(len(circles))
        cantidad_estable = int(np.median(list(self.cantidad_historial)))
        self.pub_count.publish(Int32(data=cantidad_estable))

        # 3. Lógica de "Pausa y Elección"
        if self.buscando_objetivo:
            self.get_logger().info(f"DEBUG: He encontrado {len(circles)} circulos") # Añade esta línea
            if circles:
                self.acumulador_muestreo.append(circles)
                self.contador_muestreo += 1
                self.get_logger().info(f"Contador subiendo: {self.contador_muestreo}") # Y esta
            
            cv2.putText(debug_img, f"MUESTREO: {self.contador_muestreo}/{self.get_parameter('frames_muestreo').value}", 
                        (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            if self.contador_muestreo >= self.get_parameter('frames_muestreo').value:
                self.procesar_estabilidad_final()
        
        # 4. Si ya elegimos el mejor, dibujamos el resultado persistente
        if self.objetivo_fijado:
            u, v, r, robot_p, diam_m = self.objetivo_fijado
            cv2.circle(debug_img, (int(u), int(v)), int(r), (0, 255, 0), 3)
            cv2.putText(debug_img, "OBJETIVO FIJADO (EL MAS ESTABLE)", (int(u)+20, int(v)-30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(debug_img, f"D: {diam_m*1000:.1f}mm | X: {robot_p.x:.3f}", (int(u)+20, int(v)-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        self.pub_debug_img.publish(self.bridge.cv2_to_imgmsg(debug_img, encoding='bgr8'))
        if self.get_parameter('show_debug').value:
            cv2.imshow('UR3 Vision Dinamica', debug_img)
            cv2.waitKey(1)

    def procesar_estabilidad_final(self):
        """ Filtra entre todos los frames acumulados para dar UNA sola posición estable """
        self.buscando_objetivo = False
        self.get_logger().info(f"Procesando {len(self.acumulador_muestreo)} frames...")
        if not self.acumulador_muestreo:
            self.contador_muestreo = 0
            self.buscando_objetivo = True
            return

        # Unimos todas las detecciones de la pausa
        todas = [c for frame in self.acumulador_muestreo for c in frame]
        
        # Agrupamos por proximidad para ver cuál es el tapón que más aparece
        clusters = []
        for det in todas:
            encontrado = False
            for cluster in clusters:
                if np.linalg.norm(det[:2] - np.mean(cluster, axis=0)[:2]) < 10.0:
                    cluster.append(det)
                    encontrado = True
                    break
            if not encontrado: clusters.append([det])

        if len(clusters) == 0:
            self.get_logger().error("No se han podido agrupar los tapones")
            return
            
        # El ganador es el cluster con más detecciones (más estable en el tiempo)
        ganador = max(clusters, key=len)
        self.get_logger().info(f"Ganador encontrado con {len(ganador)} apariciones")
        avg_u, avg_v, avg_r = np.mean(ganador, axis=0)

        # 4. Tu Transformación Dinámica PnP
        robot_point, dist_z = self.transformar_pixel_dinamico(avg_u, avg_v)
        
        if robot_point is None:
            self.get_logger().error("Robot point es None. No se puede publicar.")
            return

        if robot_point:
            focal_avg = (self.camera_matrix[0,0] + self.camera_matrix[1,1]) / 2.0
            diametro_metros = (2 * avg_r * dist_z) / focal_avg

            # Guardamos para el dibujo y publicamos una sola vez
            self.objetivo_fijado = (avg_u, avg_v, avg_r, robot_point, diametro_metros)
            self.pub_robot_pos.publish(robot_point)
            self.pub_target_diameter.publish(Float32(data=float(diametro_metros)))
            self.get_logger().info(f'Objetivo estabilizado fijado: {diametro_metros*1000:.1f}mm')

    def transformar_pixel_dinamico(self, u, v):
        try:
            t = self.tf_buffer.lookup_transform(
                self.get_parameter('target_frame').value,
                self.get_parameter('camera_frame').value,
                rclpy.time.Time(), timeout=Duration(seconds=0.1)
            )
            cx, cy = self.camera_matrix[0, 2], self.camera_matrix[1, 2]
            fx, fy = self.camera_matrix[0, 0], self.camera_matrix[1, 1]

            vx = (u - cx) / fx
            vy = (v - cy) / fy

            cam_z = t.transform.translation.z
            cam_x = t.transform.translation.x
            cam_y = t.transform.translation.y

            z_tapon_mundo = 0.02 
            distancia_z = cam_z - z_tapon_mundo

            real_x = cam_x - (vy * distancia_z) 
            real_y = cam_y - (vx * distancia_z)
            
            p = Point()
            p.x = real_x
            p.y = real_y
            p.z = z_tapon_mundo
            return p, distancia_z
        except Exception as e:
            self.get_logger().error(f"ERROR EN TF: {e}") # <--- ESTO ES CLAVE
            return None, None

    def detectar_caja(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([5, 40, 40]), np.array([25, 255, 200]))
        contornos, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contornos: return 0, 0, frame.shape[1], frame.shape[0]
        mayor = max(contornos, key=cv2.contourArea)
        if cv2.contourArea(mayor) < 5000: return 0, 0, frame.shape[1], frame.shape[0]
        return cv2.boundingRect(mayor)

    def detectar_tapones(self, frame):
        debug_img = frame.copy()
        x, y, w, h = self.detectar_caja(frame)
        roi = frame[y:y+h, x:x+w]
        
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)

        circles = cv2.HoughCircles(
            blurred, cv2.HOUGH_GRADIENT, dp=1.2, 
            minDist=self.get_parameter('min_dist').value,
            param1=self.get_parameter('hough_param1').value,
            param2=self.get_parameter('hough_param2').value,
            minRadius=self.get_parameter('min_radius').value,
            maxRadius=self.get_parameter('max_radius').value
        )

        res = []
        if circles is not None:
            for cx, cy, r in circles[0]:
                res.append([cx + x, cy + y, r])
                # Dibujamos todos en Cian (escaneando)
                cv2.circle(debug_img, (int(cx+x), int(cy+y)), int(r), (255, 255, 0), 1)
        return res, debug_img

def main(args=None):
    rclpy.init(args=args)
    node = VisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
