#!/usr/bin/env python3
"""
detector_tapones.py  —  NODO 2
Se ejecuta con cada tapón a clasificar.
Detecta y estabiliza la posición del tapón, se suscribe a los centros HSV
publicados por el Nodo 1 (color_calibrator_node) y asigna el número de caja
según el color del tapón. Publica la posición y la caja al robot.
NO calcula el diámetro (recogida por ventosa).
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import Point
from std_msgs.msg import Int32, Float32MultiArray
from cv_bridge import CvBridge
from collections import deque
import cv2
import numpy as np
import tf2_ros
from rclpy.duration import Duration


class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')

        # --- PARÁMETROS ---
        self.declare_parameter('min_radius', 33)
        self.declare_parameter('max_radius', 54)
        self.declare_parameter('min_dist', 75)
        self.declare_parameter('hough_param1', 21) #30
        self.declare_parameter('hough_param2', 27)
        self.declare_parameter('show_debug', True)
        self.declare_parameter('image_topic', '/image_raw')
        self.declare_parameter('target_frame', 'base_link')
        self.declare_parameter('camera_frame', 'camera_optical_frame')
        self.declare_parameter('camera_info_yaml', '')

        # --- PARÁMETROS DE ESTABILIDAD ---
        self.declare_parameter('frames_muestreo', 30)

        # --- CONFIGURACIÓN PNP / GEOMETRÍA ---
        yaml_path = self.get_parameter('camera_info_yaml').value
        if not yaml_path:
           self.get_logger().error('No se ha proporcionado camera_info_yaml. Deteniendo nodo.')
           raise RuntimeError('Parametro camera_info_yaml obligatorio')
        self.camera_matrix, self.dist_coeffs = self.cargar_calibracion(yaml_path)

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

        # --- CENTROS HSV del Nodo 1 (None hasta que lleguen) ---
        self.centros_hsv = None
        self.num_cajas = None

        self.bridge = CvBridge()

        # --- SUSCRIPCIONES ---
        self.sub_info = self.create_subscription(
            CameraInfo, '/camera/camera_info', self.info_callback, 10)
        self.subscription = self.create_subscription(
            Image, self.get_parameter('image_topic').value, self.image_callback, 10)

        # QoS latched: recibe el último mensaje aunque el Nodo 1 ya lo publicó antes
        qos_latched = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE
        )
        self.sub_centros = self.create_subscription(
            Float32MultiArray, '/clasificador/centros_hsv', self.centros_callback, qos_latched)
        self.sub_num_cajas = self.create_subscription(
            Int32, '/clasificador/num_cajas', self.num_cajas_callback, qos_latched)
            
                
        # --- PUBLICADORES ---
        self.pub_robot_pos = self.create_publisher(Point, '/ur3/target_point', 10)
        self.pub_count = self.create_publisher(Int32, '/tapones/cantidad', 10)
        self.pub_caja = self.create_publisher(Int32, '/tapones/caja_asignada', 10)
        self.pub_debug_img = self.create_publisher(Image, '/tapones/imagen_debug', 10)

        self.get_logger().info('Nodo detector iniciado: esperando calibracion de color...')
       
    # --- Leer el .YAML ---
    def cargar_calibracion(self, yaml_path):
     import yaml
     try:
         with open(yaml_path, 'r') as f:
             data = yaml.safe_load(f)
         camera_matrix = np.array(
             data['camera_matrix']['data'], dtype=np.float32).reshape((3, 3))
         dist_coeffs = np.array(
             data['distortion_coefficients']['data'], dtype=np.float32).reshape((-1, 1))
         self.get_logger().info(f'Calibracion cargada desde: {yaml_path}')
         return camera_matrix, dist_coeffs
     except Exception as e:
         self.get_logger().error(f'Error cargando YAML de calibracion: {e}')
         raise
    
    
    
    # --- CALLBACKS DE SUSCRIPCION ---

    def info_callback(self, msg):
        self.camera_matrix = np.array(msg.k).reshape((3, 3))
        self.dist_coeffs = np.array(msg.d)

    def centros_callback(self, msg):
        """ Recibe los centros HSV del Nodo 1 y los guarda """
        k = self.num_cajas if self.num_cajas else len(msg.data) // 3
        self.centros_hsv = np.array(msg.data, dtype=np.float32).reshape((k, 3))
        self.get_logger().info(f'Centros HSV recibidos: {k} cajas listas para clasificar')

    def num_cajas_callback(self, msg):
        self.num_cajas = msg.data

    # --- LOGICA PRINCIPAL ---

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # 1. Tu deteccion original con ROI y Caja
        circles, debug_img = self.detectar_tapones(frame)

        # 2. Estabilizar cantidad
        self.cantidad_historial.append(len(circles))
        cantidad_estable = int(np.median(list(self.cantidad_historial)))
        self.pub_count.publish(Int32(data=cantidad_estable))

        # Aviso si el Nodo 1 aun no ha calibrado
        if self.centros_hsv is None:
            cv2.putText(debug_img, "Esperando calibracion de color (Nodo 1)...",
                        (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # 3. Logica de "Pausa y Eleccion"
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
            u, v, r, robot_p, caja = self.objetivo_fijado
            cv2.circle(debug_img, (int(u), int(v)), int(r), (0, 255, 0), 3)
            cv2.putText(debug_img, "OBJETIVO FIJADO (EL MAS ESTABLE)", (int(u)+20, int(v)-30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(debug_img, f"X:{robot_p.x:.3f} Y:{robot_p.y:.3f}", (int(u)+20, int(v)-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            cv2.putText(debug_img, f"CAJA: {caja}", (int(u)+20, int(v)+10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)

        self.pub_debug_img.publish(self.bridge.cv2_to_imgmsg(debug_img, encoding='bgr8'))
        if self.get_parameter('show_debug').value:
            cv2.imshow('UR3 Vision Dinamica', debug_img)
            cv2.waitKey(1)

    def procesar_estabilidad_final(self):
        """ Filtra entre todos los frames acumulados para dar UNA sola posicion estable """
        self.buscando_objetivo = False
        self.get_logger().info(f"Procesando {len(self.acumulador_muestreo)} frames...")
        if not self.acumulador_muestreo:
            self.contador_muestreo = 0
            self.buscando_objetivo = True
            return

        # Unimos todas las detecciones de la pausa
        todas = [c for frame in self.acumulador_muestreo for c in frame]

        # Agrupamos por proximidad para ver cual es el tapon que mas aparece
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

        # El ganador es el cluster con mas detecciones (mas estable en el tiempo)
        ganador = max(clusters, key=len)
        self.get_logger().info(f"Ganador encontrado con {len(ganador)} apariciones")

        # Posicion media del ganador (x, y, r — primeros 3 valores)
        avg_u, avg_v, avg_r = np.mean(ganador, axis=0)[:3]

        # --- CLASIFICACION POR COLOR ---
        # Comparamos el color del ganador con los centros HSV del Nodo 1
        if self.centros_hsv is not None:
            color_ganador = np.array(np.mean(ganador, axis=0)[3:6], dtype=np.float32)
            distancias = np.linalg.norm(self.centros_hsv - color_ganador, axis=1)
            # +1 porque las cajas van de 1 a N (no de 0 a N-1)
            caja_asignada = int(np.argmin(distancias)) + 1
            self.get_logger().info(f'Tapon clasificado -> Caja {caja_asignada}')
        else:
            # Si el Nodo 1 aun no calibro, enviamos -1 como aviso al robot
            caja_asignada = -1
            self.get_logger().warn('Clasificacion de color no disponible (Nodo 1 no calibrado)')

        # Transformacion a coordenadas del robot
        robot_point = self.transformar_pixel_dinamico(avg_u, avg_v)

        if robot_point is None:
            self.get_logger().error("Robot point es None. No se puede publicar.")
            return

        # Guardamos para el dibujo y publicamos
        self.objetivo_fijado = (avg_u, avg_v, avg_r, robot_point, caja_asignada)
        self.pub_robot_pos.publish(robot_point)
        self.pub_caja.publish(Int32(data=caja_asignada))
        self.get_logger().info(f'Publicado: pos=({robot_point.x:.3f}, {robot_point.y:.3f}) -> Caja {caja_asignada}')

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
            return p
        except Exception as e:
            self.get_logger().error(f"ERROR EN TF: {e}") # <--- ESTO ES CLAVE
            return None

    # --- DETECCION ---

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
                # Extraemos el color medio en HSV dentro del circulo detectado
                mascara = np.zeros(roi.shape[:2], dtype=np.uint8)
                cv2.circle(mascara, (int(cx), int(cy)), int(r)-2, 255, -1)
                hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                color_medio = cv2.mean(hsv_roi, mask=mascara)[:3]  # H, S, V
                res.append([cx + x, cy + y, r, color_medio[0], color_medio[1], color_medio[2]])
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
