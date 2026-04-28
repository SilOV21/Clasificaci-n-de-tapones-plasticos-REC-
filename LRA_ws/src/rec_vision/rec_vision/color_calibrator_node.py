#!/usr/bin/env python3
"""
color_calibrator_node.py  —  NODO 1
Se ejecuta UNA SOLA VEZ al inicio del sistema.
Hace un barrido de todos los tapones visibles, aplica K-Means
y publica los centros HSV de cada grupo (= cada caja) de forma
persistente (latched) para que el Nodo 2 los consuma en cualquier momento.
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from sensor_msgs.msg import Image, CameraInfo
from std_msgs.msg import Int32, Float32MultiArray, MultiArrayDimension
from cv_bridge import CvBridge
import cv2
import numpy as np


class ColorCalibratorNode(Node):
    def __init__(self):
        super().__init__('color_calibrator_node')

        # --- PARÁMETROS ---
        self.declare_parameter('num_cajas', 3)          # N cajas (1-6)
        self.declare_parameter('frames_muestreo', 30)   # frames a acumular
        self.declare_parameter('min_radius', 33)
        self.declare_parameter('max_radius', 54)
        self.declare_parameter('min_dist', 75)
        self.declare_parameter('hough_param1', 21) #30
        self.declare_parameter('hough_param2', 27)
        self.declare_parameter('show_debug', True)
        self.declare_parameter('image_topic', '/image_raw')
        self.declare_parameter('camera_info_yaml', '')

        # --- CONFIGURACIÓN PNP / GEOMETRÍA ---
        yaml_path = self.get_parameter('camera_info_yaml').value
        if not yaml_path:
            self.get_logger().error('No se ha proporcionado camera_info_yaml. Deteniendo nodo.')
            raise RuntimeError('Parametro camera_info_yaml obligatorio')
        self.camera_matrix, self.dist_coeffs = self.cargar_calibracion(yaml_path)

        # --- ESTADO INTERNO ---
        self.acumulador_muestreo = []
        self.contador_muestreo = 0
        self.calibracion_hecha = False  # Una vez hecha, no se repite

        self.bridge = CvBridge()

        # --- SUSCRIPCIONES ---
        self.sub_info = self.create_subscription(
            CameraInfo, '/camera/camera_info', self.info_callback, 10)
        self.subscription = self.create_subscription(
            Image, self.get_parameter('image_topic').value, self.image_callback, 10)

        # --- PUBLICADORES ---
        # QoS latched: el mensaje persiste y cualquier suscriptor nuevo lo recibe
        # aunque se haya publicado antes de que él arrancase
        qos_latched = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE
        )
        # Publica los centros HSV como array plano [H0,S0,V0, H1,S1,V1, ...]
        self.pub_centros = self.create_publisher(
            Float32MultiArray, '/clasificador/centros_hsv', qos_latched)
        # Publica cuántas cajas se han definido
        self.pub_num_cajas = self.create_publisher(
            Int32, '/clasificador/num_cajas', qos_latched)
        # Debug visual
        self.pub_debug_img = self.create_publisher(Image, '/clasificador/imagen_debug', 10)

        self.get_logger().info('Nodo calibrador iniciado: esperando tapones...')

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
            self.get_logger().error(f'No se encuentra el YAML de calibracion: {e}')
            raise
    
    def info_callback(self, msg):
        self.camera_matrix = np.array(msg.k).reshape((3, 3))

    def image_callback(self, msg):
        # Una vez calibrado, este nodo no hace nada más
        if self.calibracion_hecha:
            return

        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        circles, debug_img = self.detectar_tapones(frame)

        if circles:
            self.acumulador_muestreo.append(circles)
            self.contador_muestreo += 1

        cv2.putText(debug_img,
                    f"CALIBRANDO: {self.contador_muestreo}/{self.get_parameter('frames_muestreo').value}",
                    (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

        self.pub_debug_img.publish(self.bridge.cv2_to_imgmsg(debug_img, encoding='bgr8'))

        if self.get_parameter('show_debug').value:
            cv2.imshow('Calibrador de Color', debug_img)
            cv2.waitKey(1)

        if self.contador_muestreo >= self.get_parameter('frames_muestreo').value:
            self.ejecutar_kmeans()

    def ejecutar_kmeans(self):
        """ Aplica K-Means sobre todos los colores acumulados y publica los centros. """
        self.get_logger().info(f"Iniciando K-Means con {len(self.acumulador_muestreo)} frames...")

        if not self.acumulador_muestreo:
            self.get_logger().error("No hay datos para calibrar. Reintentando...")
            self.contador_muestreo = 0
            return

        # Unimos todas las detecciones y extraemos solo H, S, V (índices 3, 4, 5)
        todas = [c for frame in self.acumulador_muestreo for c in frame]
        colores = np.array([[c[3], c[4], c[5]] for c in todas], dtype=np.float32)

        n = self.get_parameter('num_cajas').value
        k = min(n, len(colores))  # K no puede superar el nº de tapones vistos

        _, _, centros = cv2.kmeans(
            colores, k, None,
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0),
            10, cv2.KMEANS_RANDOM_CENTERS
        )

        # --- Publicamos los centros como Float32MultiArray plano ---
        # Formato: [H_caja1, S_caja1, V_caja1,  H_caja2, S_caja2, V_caja2, ...]
        # La caja asignada a cada centro es su índice + 1 (caja 1..N)
        msg_centros = Float32MultiArray()
        msg_centros.layout.dim.append(MultiArrayDimension(
            label='centros', size=k, stride=k * 3))
        msg_centros.data = centros.flatten().tolist()
        self.pub_centros.publish(msg_centros)

        msg_k = Int32(data=k)
        self.pub_num_cajas.publish(msg_k)

        # Log informativo: qué color HSV corresponde a cada caja
        for i, centro in enumerate(centros):
            self.get_logger().info(
                f"  Caja {i+1} → H:{centro[0]:.1f}  S:{centro[1]:.1f}  V:{centro[2]:.1f}")

        self.calibracion_hecha = True
        self.get_logger().info(f'Calibración completada: {k} cajas definidas. Nodo en espera.')

    # ─── DETECCIÓN (igual que en detector_tapones) ────────────────────────────

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
                # Extraemos el color medio en HSV dentro del círculo detectado
                mascara = np.zeros(roi.shape[:2], dtype=np.uint8)
                cv2.circle(mascara, (int(cx), int(cy)), int(r)-2, 255, -1)
                hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                color_medio = cv2.mean(hsv_roi, mask=mascara)[:3]  # H, S, V
                res.append([cx + x, cy + y, r, color_medio[0], color_medio[1], color_medio[2]])
                # Dibujamos todos en Naranja (calibrando)
                cv2.circle(debug_img, (int(cx+x), int(cy+y)), int(r), (0, 165, 255), 1)
        return res, debug_img


def main(args=None):
    rclpy.init(args=args)
    node = ColorCalibratorNode()
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
