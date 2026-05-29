#!/usr/bin/env python3
"""
detector_tapones.py  —  NODO 2
Se ejecuta con cada tapón a clasificar.
Detecta y estabiliza la posición del tapón, se suscribe a los centros HSV
publicados por el Nodo 1 (color_calibrator_node) y asigna el número de caja
según el color del tapón. Publica la posición y la caja al robot.
"""
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import Point
from std_msgs.msg import Int32, Float32MultiArray, Bool
from cv_bridge import CvBridge
from collections import deque
import cv2
import numpy as np
import math
import tf2_ros
from rclpy.duration import Duration


class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')

        # Semilla fija de OpenCV: detección/clustering reproducibles entre arranques.
        cv2.setRNGSeed(0)

        # --- PARÁMETROS ---
        self.declare_parameter('min_radius', 33)
        self.declare_parameter('max_radius', 54)
        self.declare_parameter('min_dist', 75)
        self.declare_parameter('hough_param1', 21) 
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
        # El YAML es la fuente autoritativa de intrínsecos; no se sobrescriben con
        # camera_info en vivo cada frame (evita deriva de coordenadas entre arranques).
        self._intrinsics_applied = True


        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Historiales y Estados
        self.pos_history = deque(maxlen=10)
        self.cantidad_historial = deque(maxlen=5)
        self.acumulador_muestreo = []
        self.contador_muestreo = 0
        self.buscando_objetivo = True
        self.objetivo_fijado = None

        # Gating por /vision_enable: ur3_pick_sort lo pone a True cuando está
        # libre y a False mientras hace pick-and-place. Arranca deshabilitado;
        # cada flanco de subida produce UNA detección nueva.
        self.vision_enabled = False

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

        # /vision_enable lo publica ur3_pick_sort de forma "latched", por eso
        # usamos el mismo QoS: un detector que arranca después igualmente recibe
        # el último estado.
        self.sub_vision_enable = self.create_subscription(
            Bool, '/vision_enable', self.vision_enable_callback, qos_latched)

        # --- PUBLICADORES ---
        self.pub_robot_pos = self.create_publisher(Point, '/ur3/target_point', 10)
        self.pub_count = self.create_publisher(Int32, '/tapones/cantidad', 10)
        self.pub_caja = self.create_publisher(Int32, '/tapones/caja_asignada', 10)
        self.pub_debug_img = self.create_publisher(Image, '/tapones/imagen_debug', 10)

        self.get_logger().info('Nodo detector iniciado: esperando calibracion de color...')
       
    # EXTRACCIÓN ROBUSTA DE COLOR 
    def extraer_color_hsv(self, hsv_roi, cx, cy, r):
        """
        Devuelve [H, S, V] representativo del tapón, robusto a:
          - reflejos especulares (brillo blanco central)
          - borde del tapón / sombras
          - circularidad de H (matiz)
        Usa un anillo interior (0.25r..0.75r), descarta reflejos,
        mediana de S y V, y media CIRCULAR de H.
        """
        h_img, w_img = hsv_roi.shape[:2]
        r = int(r)

        mask = np.zeros((h_img, w_img), dtype=np.uint8)
        cv2.circle(mask, (int(cx), int(cy)), max(int(r * 0.75), 2), 255, -1)
        cv2.circle(mask, (int(cx), int(cy)), int(r * 0.25), 0, -1)

        ys, xs = np.where(mask == 255)
        if len(xs) == 0:
            cv2.circle(mask, (int(cx), int(cy)), max(r - 2, 1), 255, -1)
            ys, xs = np.where(mask == 255)
            if len(xs) == 0:
                return [0.0, 0.0, 0.0]

        pix = hsv_roi[ys, xs].astype(np.float32)
        H = pix[:, 0]; S = pix[:, 1]; V = pix[:, 2]

        valid = (V < 245) & (V > 25) & ~((V > 220) & (S < 40))
        if np.count_nonzero(valid) > 10:
            H, S, V = H[valid], S[valid], V[valid]

        S_med = float(np.median(S))
        V_med = float(np.median(V))

        ang = H * (2.0 * np.pi / 180.0)
        sin_m = float(np.mean(np.sin(ang)))
        cos_m = float(np.mean(np.cos(ang)))
        H_med = (math.atan2(sin_m, cos_m) * 180.0 / (2.0 * np.pi)) % 180.0

        return [H_med, S_med, V_med]

    def distancia_color(self, c1, c2):
        """
        Distancia entre dos colores HSV teniendo en cuenta:
          - circularidad de H (0 y 180 son el mismo matiz)
          - que en colores poco saturados (negro/blanco/gris) el H es ruido,
            así que se pondera H por la saturación.
        c1, c2: [H, S, V]  (H en 0..180, S/V en 0..255)
        """
        h1, s1, v1 = float(c1[0]), float(c1[1]), float(c1[2])
        h2, s2, v2 = float(c2[0]), float(c2[1]), float(c2[2])

        # Diferencia circular de H -> 0..90 (en escala OpenCV)
        dh = abs(h1 - h2)
        dh = min(dh, 180.0 - dh)
        # Normalizar dh a 0..1 (90 = opuesto)
        dh_n = dh / 90.0

        ds_n = abs(s1 - s2) / 255.0
        dv_n = abs(v1 - v2) / 255.0

        # Peso de H proporcional a cuán saturados son ambos colores:
        # si alguno es casi gris, el matiz no es fiable.
        sat_factor = min(s1, s2) / 255.0   # 0..1

        w_h = 2.0 * sat_factor   # H pesa más cuanto más saturado
        w_s = 1.0
        w_v = 1.0

        return math.sqrt((w_h * dh_n) ** 2 + (w_s * ds_n) ** 2 + (w_v * dv_n) ** 2)

    # --- LEER EL .YAML ---
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
        # Los intrínsecos se fijan UNA vez (YAML al arrancar). camera_info en vivo
        # solo se usa como respaldo si aún no hubiera intrínsecos válidos.
        if self._intrinsics_applied:
            return
        k = np.array(msg.k).reshape((3, 3))
        if k[0, 0] > 0 and k[1, 1] > 0:
            self.camera_matrix = k
            self.dist_coeffs = np.array(msg.d)
            self._intrinsics_applied = True

    def centros_callback(self, msg):
        """ Recibe los centros HSV del Nodo 1 y los guarda """
        k = self.num_cajas if self.num_cajas else len(msg.data) // 3
        self.centros_hsv = np.array(msg.data, dtype=np.float32).reshape((k, 3))
        self.get_logger().info(f'Centros HSV recibidos: {k} cajas listas para clasificar')

    def num_cajas_callback(self, msg):
        self.num_cajas = msg.data

    def vision_enable_callback(self, msg):
        """Habilita/inhabilita el muestreo. Cada flanco de subida reinicia el
        estado para producir una única detección nueva."""
        enabled = bool(msg.data)
        if enabled and not self.vision_enabled:
            self.buscando_objetivo = True
            self.contador_muestreo = 0
            self.acumulador_muestreo = []
            self.objetivo_fijado = None
            self.get_logger().info('Visión habilitada: reiniciando muestreo.')
        elif not enabled and self.vision_enabled:
            self.buscando_objetivo = False
            self.get_logger().info('Visión deshabilitada: muestreo detenido.')
        self.vision_enabled = enabled

    # LOGICA PRINCIPAL

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Detección de ROI 
        circles, debug_img = self.detectar_tapones(frame)

        #  Estabilizar cantidad
        self.cantidad_historial.append(len(circles))
        cantidad_estable = int(np.median(list(self.cantidad_historial)))
        self.pub_count.publish(Int32(data=cantidad_estable))

        # Aviso si el Nodo 1 aun no ha calibrado
        if self.centros_hsv is None:
            cv2.putText(debug_img, "Esperando calibracion de color (Nodo 1)...",
                        (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # 3. Logica de "Pausa y Eleccion" (solo si la visión está habilitada)
        if self.vision_enabled and self.buscando_objetivo:
            self.get_logger().info(f"DEBUG: He encontrado {len(circles)} circulos") 
            if circles:
                self.acumulador_muestreo.append(circles)
                self.contador_muestreo += 1
                self.get_logger().info(f"Contador subiendo: {self.contador_muestreo}") 

            cv2.putText(debug_img, f"MUESTREO: {self.contador_muestreo}/{self.get_parameter('frames_muestreo').value}",
                        (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            if self.contador_muestreo >= self.get_parameter('frames_muestreo').value:
                self.procesar_estabilidad_final()

        # Si ya elegimos el mejor, dibujamos el resultado persistente
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
            # Promedio del color del ganador entre frames:
            # S y V con mediana, H con media circular (no lineal)
            ganador_arr = np.array(ganador, dtype=np.float32)
            H_vals = ganador_arr[:, 3]
            S_med = float(np.median(ganador_arr[:, 4]))
            V_med = float(np.median(ganador_arr[:, 5]))
            ang = H_vals * (2.0 * np.pi / 180.0)
            H_med = (math.atan2(float(np.mean(np.sin(ang))),
                                float(np.mean(np.cos(ang)))) * 180.0 / (2.0 * np.pi)) % 180.0
            color_ganador = np.array([H_med, S_med, V_med], dtype=np.float32)

            # Distancia que respeta la circularidad de H y pondera por saturación
            distancias = [
                self.distancia_color(color_ganador, centro)
                for centro in self.centros_hsv
            ]
            # +1 porque las cajas van de 1 a N (no de 0 a N-1)
            caja_asignada = int(np.argmin(distancias)) + 1
            self.get_logger().info(
                f'Tapon clasificado -> Caja {caja_asignada} '
                f'(HSV={color_ganador[0]:.0f},{color_ganador[1]:.0f},{color_ganador[2]:.0f} '
                f'| dists={[round(d,3) for d in distancias]})'
            )
        else:
            # Si el Nodo 1 aun no calibro, enviamos -1 como aviso al robot
            caja_asignada = -1
            self.get_logger().warn('Clasificacion de color no disponible (Nodo 1 no calibrado)')

        # Transformacion a coordenadas del robot
        robot_point = self.transformar_pixel_dinamico(avg_u, avg_v)

        if robot_point is None:
            # Suele ser TF aún no disponible: re-armamos el muestreo para reintentar
            # en vez de quedarnos bloqueados sin volver a publicar.
            self.get_logger().error("Robot point es None (¿TF no lista?). Reintentando muestreo.")
            self.buscando_objetivo = True
            self.contador_muestreo = 0
            self.acumulador_muestreo = []
            return

        # Guardamos para el dibujo y publicamos
        self.objetivo_fijado = (avg_u, avg_v, avg_r, robot_point, caja_asignada)
        self.pub_robot_pos.publish(robot_point)
        self.pub_caja.publish(Int32(data=caja_asignada))
        self.get_logger().info(f'Publicado: pos=({robot_point.x:.3f}, {robot_point.y:.3f}, {robot_point.z:.3f}) -> Caja {caja_asignada}')

    def transformar_pixel_dinamico(self, u, v):
        try:
            t = self.tf_buffer.lookup_transform(
                self.get_parameter('target_frame').value,
                self.get_parameter('camera_frame').value,
                rclpy.time.Time(), timeout=Duration(seconds=0.5)
            )

            # Píxel -> rayo normalizado, corrigiendo distorsión
            pts = np.array([[[u, v]]], dtype=np.float32)
            undist = cv2.undistortPoints(pts, self.camera_matrix, self.dist_coeffs)
            vx, vy = undist[0, 0]
            ray_cam = np.array([vx, vy, 1.0])   # frame óptico: x derecha, y abajo, z hacia escena

            # Rotación de la TF (cuaternión -> matriz)
            q = t.transform.rotation
            x, y, z, w = q.x, q.y, q.z, q.w
            R = np.array([
                [1-2*(y*y+z*z),   2*(x*y-z*w),   2*(x*z+y*w)],
                [2*(x*y+z*w),   1-2*(x*x+z*z),   2*(y*z-x*w)],
                [2*(x*z-y*w),     2*(y*z+x*w), 1-2*(x*x+y*y)],
            ])
            T = np.array([t.transform.translation.x,
                          t.transform.translation.y,
                          t.transform.translation.z])

            # Rayo en base_link e intersección con el plano z = z_tapon
            ray_base = R @ ray_cam
            z_tapon = 0.002
            if abs(ray_base[2]) < 1e-6:
                self.get_logger().error("Rayo paralelo al plano")
                return None
            s = (z_tapon - T[2]) / ray_base[2]
            P = T + s * ray_base

            p = Point()
            p.x, p.y, p.z = float(P[0]) + 0.048, float(P[1]) + 0.027, 0.002 #float(P[2])
            return p
        except Exception as e:
            self.get_logger().error(f"ERROR EN TF: {e}")
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
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            for cx, cy, r in circles[0]:
                # Color robusto (anillo interior, sin reflejos, H circular)
                H, S, V = self.extraer_color_hsv(hsv_roi, cx, cy, r)
                res.append([cx + x, cy + y, r, H, S, V])
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
