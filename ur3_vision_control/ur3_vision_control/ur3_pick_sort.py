import rclpy
import threading
import math
import time

from rclpy.node import Node
import tf2_ros

from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import Point
from std_msgs.msg import Bool, String
from visualization_msgs.msg import Marker, MarkerArray
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose, PoseStamped
from builtin_interfaces.msg import Duration
from ur_msgs.srv import SetIO
from moveit_msgs.srv import GetPositionIK
from moveit_msgs.msg import RobotState


class UR3PickSort(Node):

    def __init__(self):
        super().__init__('ur3_pick_sort')

        self.declare_parameter('simulate_gripper', True)
        self.simulate_gripper = self.get_parameter('simulate_gripper').value

        self.io_client = None
        if not self.simulate_gripper:
            self.io_client = self.create_client(
                SetIO,
                '/io_and_status_controller/set_io'
            )
            while not self.io_client.wait_for_service(timeout_sec=1.0):
                self.get_logger().info(
                    'Esperando servicio /io_and_status_controller/set_io ...'
                )

        # =========================================================
        # MODO DE PRUEBA
        # =========================================================
        # False = prueba solo HOME -> TARGET -> HOME
        # True  = HOME -> TARGET -> HOME -> PUNTO COLOR -> soltar -> HOME
        self.use_bins = True

        # =========================================================
        # PUBLICADORES
        # =========================================================
        self.traj_pub = self.create_publisher(
            JointTrajectory,
            '/scaled_joint_trajectory_controller/joint_trajectory',
            10
        )

        self.vision_enable_pub = self.create_publisher(
            Bool,
            '/vision_enable',
            10
        )

        self.marker_pub = self.create_publisher(
            MarkerArray,
            '/sorting_markers',
            10
        )

        self.collision_object_pub = self.create_publisher(
            CollisionObject,
            '/collision_object',
            10
        )

        # =========================================================
        # SUSCRIPTORES
        # =========================================================
        self.target_sub = self.create_subscription(
            Point,
            '/vision_target',
            self.target_callback,
            10
        )

        self.color_sub = self.create_subscription(
            String,
            '/vision_color',
            self.color_callback,
            10
        )

        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )

        # =========================================================
        # ESTADO
        # =========================================================
        self.last_target = None
        self.last_color = None
        self.current_target_xyz = None
        self.current_target_color = None

        self.busy = True
        self.current_joints = None

        self.home_check_timer = None
        self.startup_home_timer = None
        self.marker_timer = None
        self.initial_home_last_send_time = None

        self.table_added = False

        # =========================================================
        # TF
        # =========================================================
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.home_tcp_xyz = None


        # =========================================================
        # MOVEIT IK PARA PICK CONTINUO
        # =========================================================
        self.arm_joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint',
        ]

        # En UR MoveIt normalmente el planning group es ur_manipulator.
        # Si en tu setup fuera "manipulator", cambia solo esta línea.
        self.moveit_group_name = 'ur_manipulator'
        self.ik_link_name = 'tool0'
        self.pose_frame = 'base_link'

        # Orientación fija de pick: herramienta hacia abajo
        # Orientaciones candidatas para pick:
        # misma herramienta "hacia abajo", pero con distintos yaw
        # y un pequeño tilt para puntos más cercanos al robot.
        self.pick_orientation_candidates = [
            self.quaternion_from_euler(math.pi, 0.0, 0.0),
            self.quaternion_from_euler(math.pi, 0.0, math.pi / 2.0),
            self.quaternion_from_euler(math.pi, 0.0, -math.pi / 2.0),
            self.quaternion_from_euler(math.pi, 0.0, math.pi),
            self.quaternion_from_euler(math.pi, math.radians(12.0), 0.0),
            self.quaternion_from_euler(math.pi, math.radians(-12.0), 0.0),
        ]

        # Offsets verticales para el pick
        # IMPORTANTE:
        # tool0 en UR no es la punta de los dedos; suele equivaler al tool frame
        # "all-zero" en el centro de la brida. Por eso NO conviene usar z+0.00
        # como contacto si no has definido un TCP real de la pinza.
        self.pick_approach_offset_z = 0.14
        self.pick_contact_offset_z = 0.06
        self.pick_retreat_offset_z = 0.16

        # Candidatos de altura para hacer fallback por etapa
        self.pick_approach_offset_candidates = [0.16, 0.14, 0.12, 0.10]
        self.pick_contact_offset_candidates = [0.08, 0.06, 0.04, 0.02]
        self.pick_retreat_offset_candidates = [0.16, 0.18, 0.20]

        # Tiempo más generoso para IK
        self.ik_timeout_sec = 1.0

        # Si con colisiones activadas no encuentra IK, probamos sin colisiones
        # SOLO como fallback práctico en esta etapa.
        self.allow_ik_collision_fallback = True

        self.compute_ik_client = self.create_client(
            GetPositionIK,
            '/compute_ik'
        )

        while not self.compute_ik_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Esperando servicio /compute_ik ...')


        # =========================================================
        # HOME NUEVO
        # =========================================================
        self.home_position = self.normalize_joint_vector([
            math.radians(0),
            math.radians(-120),
            math.radians(5),
            math.radians(210),
            math.radians(90),
            math.radians(-110),
        ])

        # Rama preferida para los picks sobre mesa
        self.preferred_pick_branch = list(self.home_position)

        # Pesos para penalizar cambios bruscos, sobre todo en hombro/codo/muñeca
        # Pesos para penalizar cambios bruscos, pero sin bloquear tanto
        self.joint_cost_weights = [1.0, 4.0, 3.5, 2.0, 2.0, 1.0]
        self.branch_preference_gain = 0.20

        # Saltos máximos permitidos entre estado actual y candidata IK
        # Más relajados que antes, porque los puntos cercanos al robot
        # necesitan cambios articulares mayores.
        self.max_jump = [2.40, 2.20, 2.40, 2.60, 1.80, 2.80]

        # =========================================================
        # PICKS MULTICELDA CALIBRADOS
        # IMPORTANTE:
        # - por ahora puedes repetir los mismos joints en todas las celdas
        # - luego calibras cada una por separado
        # =========================================================
        self.pick_cells = [
            {
                'name': 'cell_1',
                'xy': (-0.46, 0.25),
                'approach': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
                'pick': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
            },
            {
                'name': 'cell_2',
                'xy': (-0.42, 0.25),
                'approach': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
                'pick': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
            },
            {
                'name': 'cell_3',
                'xy': (-0.38, 0.25),
                'approach': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
                'pick': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
            },
            {
                'name': 'cell_4',
                'xy': (-0.46, 0.20),
                'approach': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
                'pick': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
            },
            {
                'name': 'cell_5',
                'xy': (-0.42, 0.20),
                'approach': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
                'pick': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
            },
            {
                'name': 'cell_6',
                'xy': (-0.38, 0.20),
                'approach': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
                'pick': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
            },
            {
                'name': 'cell_7',
                'xy': (-0.48, 0.28),
                'approach': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
                'pick': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
            },
            {
                'name': 'cell_8',
                'xy': (-0.46, 0.30),
                'approach': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
                'pick': [
                    math.radians(-10),
                    math.radians(-200),
                    math.radians(45),
                    math.radians(230),
                    math.radians(90),
                    math.radians(-120),
                ],
            },
        ]
        
        for cell in self.pick_cells:
            cell['approach'] = self.normalize_joint_vector(cell['approach'])
            cell['pick'] = self.normalize_joint_vector(cell['pick'])
       
        # =========================================================
        # WAYPOINTS DE COLORES
        # Por ahora no entra a la caja:
        # llega al punto del color y suelta ahí
        # =========================================================
        deg = math.radians

        # AMARILLO = foto 1
        amarillo_point = [
            deg(20),
            deg(-25),
            deg(50),
            deg(-130),
            deg(-85),
            deg(-15),
        ]

        # VERDE = foto 2
        verde_point = [
            deg(-145),
            deg(215),
            deg(-60),
            deg(305),
            deg(80),
            deg(-75),
        ]

        # AZUL = foto 3
        azul_point = [
            deg(-155),
            deg(225),
            deg(-80),
            deg(305),
            deg(90),
            deg(-85),
        ]

        # ROJO = foto 4
        rojo_point = [
            deg(-165),
            deg(225),
            deg(-80),
            deg(310),
            deg(90),
            deg(-95),
        ]

        rojo_approach = rojo_point
        rojo_drop = [
            rojo_point[0],
            rojo_point[1] - math.radians(8),
            rojo_point[2] + math.radians(8),
            rojo_point[3],
            rojo_point[4],
            rojo_point[5],
        ]

        azul_approach = azul_point
        azul_drop = [
            azul_point[0],
            azul_point[1] - math.radians(8),
            azul_point[2] + math.radians(8),
            azul_point[3],
            azul_point[4],
            azul_point[5],
        ]

        verde_approach = verde_point
        verde_drop = [
            verde_point[0],
            verde_point[1] - math.radians(8),
            verde_point[2] + math.radians(8),
            verde_point[3],
            verde_point[4],
            verde_point[5],
        ]

        amarillo_approach = amarillo_point
        amarillo_drop = [
            amarillo_point[0],
            amarillo_point[1] - math.radians(8),
            amarillo_point[2] + math.radians(8),
            amarillo_point[3],
            amarillo_point[4],
            amarillo_point[5],
        ]

        self.bin_approach_joints = {
            'rojo': rojo_approach,
            'azul': azul_approach,
            'verde': verde_approach,
            'amarillo': amarillo_approach,
        }

        self.bin_drop_joints = {
            'rojo': rojo_drop,
            'azul': azul_drop,
            'verde': verde_drop,
            'amarillo': amarillo_drop,
        }


        for color in self.bin_approach_joints:
            self.bin_approach_joints[color] = self.normalize_joint_vector(
                self.bin_approach_joints[color]
            )
            self.bin_drop_joints[color] = self.normalize_joint_vector(
                self.bin_drop_joints[color]
            )



        # =========================================================
        # CAJAS EN ZONA POSITIVA, MÁS LEJOS DEL BRAZO
        # =========================================================
        self.bin_drop_xyz = {
            'rojo':     (0.46, 0.00, 0.08),
            'azul':     (0.46, 0.08, 0.08),
            'verde':    (0.46, 0.18, 0.08),
            'amarillo': (0.46, 0.28, 0.08),
        }

        self.bin_marker_xyz = {
            'rojo':     (0.46, 0.00, 0.08),
            'azul':     (0.46, 0.08, 0.08),
            'verde':    (0.46, 0.18, 0.08),
            'amarillo': (0.46, 0.28, 0.08),
        }

        self.home_marker_xyz = (0.15, 0.20, 0.25)

        # =========================================================
        # WORKSPACE
        # =========================================================
        self.workspace_limits = {
            'x_min': -0.60,
            'x_max': 0.80,
            'y_min': -0.05,
            'y_max': 0.55,
            'z_min': 0.02,
            'z_max': 0.30,
        }

        self.get_logger().info(f'simulate_gripper = {self.simulate_gripper}')
        self.get_logger().info(f'use_bins = {self.use_bins}')

        # =========================================================
        # ESTADO INICIAL
        # =========================================================
        self.enable_vision(False)

        self.get_logger().info('Abriendo pinza al iniciar...')
        self.open_gripper()

        self.marker_timer = self.create_timer(0.5, self.publish_markers)
        self.startup_home_timer = self.create_timer(1.0, self.try_send_initial_home)
        self.home_check_timer = self.create_timer(0.2, self.check_home_and_enable_vision)
        self.create_timer(1.0, self.add_table_once)

    # =========================================================
    # UTILIDADES
    # =========================================================
    def now_sec(self):
        return self.get_clock().now().nanoseconds / 1e9

    def angle_distance(self, a, b):
        return abs((a - b + math.pi) % (2.0 * math.pi) - math.pi)


    def normalize_angle(self, q):
        return math.atan2(math.sin(q), math.cos(q))

    def normalize_joint_vector(self, q_vec):
        return [self.normalize_angle(q) for q in q_vec]


    def quaternion_from_euler(self, roll, pitch, yaw):
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)

        qw = cr * cp * cy + sr * sp * sy
        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * sy
        qz = cr * cp * sy - sr * sp * cy

        return {
            'x': qx,
            'y': qy,
            'z': qz,
            'w': qw,
        }



    def is_front_pick_branch(self, q_vec):
        q = self.normalize_joint_vector(q_vec)

        shoulder_lift = q[1]
        wrist_2 = q[4]

        # Filtro más suave:
        # evita ramas claramente "hacia atrás",
        # pero no bloquea soluciones válidas para puntos cercanos.
        return (
            shoulder_lift < 0.35 and
            abs(wrist_2) > 0.20
        )

    def wrap_to_near(self, q_ref, q_target):
        delta = (q_target - q_ref + math.pi) % (2.0 * math.pi) - math.pi
        return q_ref + delta

    def joints_close(self, q_target, tol=0.03):
        if self.current_joints is None:
            return False

        for q_now, q_des in zip(self.current_joints, q_target):
            if self.angle_distance(q_now, q_des) > tol:
                return False
        return True


    def joints_almost_equal(self, q1, q2, tol=0.03):
        if q1 is None or q2 is None:
            return False

        for a, b in zip(q1, q2):
            if self.angle_distance(a, b) > tol:
                return False
        return True



    def is_robot_at_home(self, tol=0.03):
        return self.joints_close(self.home_position, tol=tol)

    def is_target_in_workspace(self, x, y, z):
        limits = self.workspace_limits
        return (
            limits['x_min'] <= x <= limits['x_max'] and
            limits['y_min'] <= y <= limits['y_max'] and
            limits['z_min'] <= z <= limits['z_max']
        )


    def build_pick_pose(self, x, y, z, orientation=None):
        pose_stamped = PoseStamped()
        pose_stamped.header.frame_id = self.pose_frame
        pose_stamped.header.stamp = self.get_clock().now().to_msg()

        pose_stamped.pose.position.x = float(x)
        pose_stamped.pose.position.y = float(y)
        pose_stamped.pose.position.z = float(z)

        if orientation is None:
            orientation = self.pick_orientation_candidates[0]

        pose_stamped.pose.orientation.x = orientation['x']
        pose_stamped.pose.orientation.y = orientation['y']
        pose_stamped.pose.orientation.z = orientation['z']
        pose_stamped.pose.orientation.w = orientation['w']

        return pose_stamped

    def build_robot_state_from_seed(self, seed_joints):
        state = RobotState()
        state.joint_state.name = list(self.arm_joint_names)
        state.joint_state.position = [
            float(q) for q in self.normalize_joint_vector(seed_joints)
        ]
        return state

    def extract_arm_joints_from_solution(self, solution_state):
        joint_map = dict(
            zip(solution_state.joint_state.name, solution_state.joint_state.position)
        )

        try:
            return [joint_map[name] for name in self.arm_joint_names]
        except KeyError as e:
            self.get_logger().error(f'Falta joint en solución IK: {e}')
            return None

    def compute_ik_joints(self, pose_stamped, seed_joints=None, timeout_sec=None, avoid_collisions=True):
        if timeout_sec is None:
            timeout_sec = self.ik_timeout_sec

        if seed_joints is None:
            if self.current_joints is None:
                self.get_logger().error('No hay current_joints para usar como semilla IK.')
                return None
            seed_joints = self.current_joints

        req = GetPositionIK.Request()
        req.ik_request.group_name = self.moveit_group_name
        req.ik_request.robot_state = self.build_robot_state_from_seed(seed_joints)
        req.ik_request.pose_stamped = pose_stamped
        req.ik_request.ik_link_name = self.ik_link_name
        req.ik_request.avoid_collisions = avoid_collisions
        req.ik_request.timeout = Duration(sec=0, nanosec=int(timeout_sec * 1e9))

        future = self.compute_ik_client.call_async(req)

        done_event = threading.Event()
        result_box = {'response': None, 'error': None}

        def done_cb(fut):
            try:
                result_box['response'] = fut.result()
            except Exception as e:
                result_box['error'] = e
            finally:
                done_event.set()

        future.add_done_callback(done_cb)

        ok_wait = done_event.wait(timeout=timeout_sec + 1.0)
        if not ok_wait:
            self.get_logger().error('Timeout esperando respuesta de /compute_ik')
            return None

        if result_box['error'] is not None:
            self.get_logger().error(f'Error llamando /compute_ik: {result_box["error"]}')
            return None

        res = result_box['response']
        if res is None:
            self.get_logger().error('Respuesta IK vacía.')
            return None

        if res.error_code.val != 1:
            self.get_logger().warn(
                f'IK no encontró solución. error_code={res.error_code.val}, '
                f'avoid_collisions={avoid_collisions}'
            )
            return None

        q_sol = self.extract_arm_joints_from_solution(res.solution)
        if q_sol is None:
            return None

        seed_joints = self.normalize_joint_vector(seed_joints)
        q_sol = self.normalize_joint_vector(q_sol)

        # Continuidad respecto a la semilla de esa etapa
        q_sol = [
            self.wrap_to_near(q_seed, q_des)
            for q_seed, q_des in zip(seed_joints, q_sol)
        ]

        # Y volvemos a normalizar para NO acumular vueltas de 2*pi
        q_sol = self.normalize_joint_vector(q_sol)

        return q_sol


    def joint_path_cost(self, q_ref, q_target):
        if q_ref is None or q_target is None:
            return float('inf')

        q_ref = self.normalize_joint_vector(q_ref)
        q_target = self.normalize_joint_vector(q_target)

        motion_cost = sum(
            w * self.angle_distance(a, b)
            for w, a, b in zip(self.joint_cost_weights, q_ref, q_target)
        )

        branch_cost = self.branch_preference_gain * sum(
            w * self.angle_distance(a, b)
            for w, a, b in zip(
                self.joint_cost_weights,
                q_target,
                self.preferred_pick_branch
            )
        )

        return motion_cost + branch_cost

    def build_ik_seed_candidates(self, preferred_seed=None):
        seeds = []
        seen = set()

        def add_seed(q):
            if q is None or len(q) != 6:
                return
            key = tuple(round(float(v), 6) for v in q)
            if key in seen:
                return
            seen.add(key)
            seeds.append([float(v) for v in q])

        # Orden de prioridad
        add_seed(preferred_seed)
        add_seed(self.current_joints)
        add_seed(self.home_position)

        # Reutiliza bins como semillas válidas conocidas
        for q in self.bin_approach_joints.values():
            add_seed(q)
        for q in self.bin_drop_joints.values():
            add_seed(q)

        # Reutiliza pick_cells SOLO como semillas, ya no como objetivo de pick
        for cell in self.pick_cells:
            add_seed(cell.get('approach'))
            add_seed(cell.get('pick'))

        return seeds

    def solve_stage_ik(self, x, y, z_candidates, preferred_seed=None, stage_name='stage'):
        seeds = self.build_ik_seed_candidates(preferred_seed=preferred_seed)

        if preferred_seed is not None:
            q_ref = preferred_seed
        else:
            q_ref = self.current_joints

        q_ref = self.normalize_joint_vector(q_ref)

        found = []

        collision_modes = [True]
        if self.allow_ik_collision_fallback:
            collision_modes.append(False)

        for avoid_collisions in collision_modes:
            for z_goal in z_candidates:
                for orientation in self.pick_orientation_candidates:
                    pose = self.build_pick_pose(x, y, z_goal, orientation=orientation)

                    for seed in seeds:
                        q_sol = self.compute_ik_joints(
                            pose_stamped=pose,
                            seed_joints=seed,
                            timeout_sec=self.ik_timeout_sec,
                            avoid_collisions=avoid_collisions
                        )

                        if q_sol is None:
                            continue

                        q_sol = self.normalize_joint_vector(q_sol)

                        # Filtro de rama, pero suave
                        if stage_name in ('approach', 'pick') and not self.is_front_pick_branch(q_sol):
                            continue

                        # Rechaza solo saltos MUY bruscos
                        too_far = False
                        for i, lim in enumerate(self.max_jump):
                            if self.angle_distance(q_ref[i], q_sol[i]) > lim:
                                too_far = True
                                break

                        if too_far:
                            continue

                        cost = self.joint_path_cost(q_ref, q_sol)

                        found.append({
                            'q': q_sol,
                            'z_goal': z_goal,
                            'cost': cost,
                            'avoid_collisions': avoid_collisions
                        })

            if found:
                break

        if not found:
            self.get_logger().warn(f'No se encontró IK para {stage_name}.')
            return None, None

        best = min(found, key=lambda item: item['cost'])

        self.get_logger().info(
            f'IK OK para {stage_name}: z_goal={best["z_goal"]:.3f}, '
            f'avoid_collisions={best["avoid_collisions"]}, cost={best["cost"]:.3f}'
        )

        return best['q'], best['z_goal']



    def get_nearest_pick_cell(self, x, y):
        best_cell = None
        best_dist = float('inf')

        for cell in self.pick_cells:
            cx, cy = cell['xy']
            d = (x - cx) ** 2 + (y - cy) ** 2

            if d < best_dist:
                best_dist = d
                best_cell = cell

        return best_cell

    # =========================================================
    # MESA
    # =========================================================
    def add_table_once(self):
        if self.table_added:
            return
        self.add_table_collision()
        self.table_added = True

    def add_table_collision(self):
        obj = CollisionObject()
        obj.header.frame_id = 'world'
        obj.id = 'table'

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = [1.40, 0.90, 0.04]

        pose = Pose()
        pose.position.x = 0.10
        pose.position.y = 0.20
        pose.position.z = -0.02
        pose.orientation.w = 1.0

        obj.primitives.append(primitive)
        obj.primitive_poses.append(pose)
        obj.operation = CollisionObject.ADD

        self.collision_object_pub.publish(obj)
        self.get_logger().info('Mesa agregada como objeto de colisión.')

    # =========================================================
    # JOINT STATES
    # =========================================================
    def joint_state_callback(self, msg):
        wanted = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint',
        ]

        joint_map = dict(zip(msg.name, msg.position))

        try:
            self.current_joints = self.normalize_joint_vector(
                [joint_map[name] for name in wanted]
            )
        except KeyError:
            return

    # =========================================================
    # ARRANQUE Y HOME
    # =========================================================
    def try_send_initial_home(self):
        if not self.busy:
            if self.startup_home_timer is not None:
                self.startup_home_timer.cancel()
                self.startup_home_timer = None
            return

        if self.current_joints is None:
            self.get_logger().info('Esperando /joint_states para enviar HOME inicial...')
            return

        if self.is_robot_at_home():
            self.get_logger().info('Robot ya está en HOME al iniciar.')
            if self.startup_home_timer is not None:
                self.startup_home_timer.cancel()
                self.startup_home_timer = None
            return

        now = self.now_sec()

        if self.initial_home_last_send_time is None or (now - self.initial_home_last_send_time) > 4.0:
            self.get_logger().info('Enviando HOME inicial...')
            self.publish_single_point_trajectory(self.home_position, 3)
            self.initial_home_last_send_time = now

    def check_home_and_enable_vision(self):
        if self.current_joints is None:
            return

        if self.is_robot_at_home():
            if self.startup_home_timer is not None:
                self.startup_home_timer.cancel()
                self.startup_home_timer = None

            if self.home_check_timer is not None:
                self.home_check_timer.cancel()
                self.home_check_timer = None

            self.update_home_marker_from_tf()
            self.busy = False
            self.enable_vision(True)
            self.get_logger().info('Robot realmente en HOME. Vision activada.')

    def update_home_marker_from_tf(self):
        try:
            tf_msg = self.tf_buffer.lookup_transform(
                'base_link',
                'tool0',
                rclpy.time.Time()
            )

            self.home_tcp_xyz = (
                tf_msg.transform.translation.x,
                tf_msg.transform.translation.y,
                tf_msg.transform.translation.z
            )
        except Exception as e:
            self.get_logger().warn(f'No se pudo leer TF de HOME: {e}')

    def return_home_and_wait(self, timeout_sec=7.0):
        self.get_logger().info('Retornando a HOME...')
        self.publish_single_point_trajectory(self.home_position, 4)

        start_time = self.now_sec()

        while rclpy.ok():
            if self.is_robot_at_home():
                self.get_logger().info('Robot volvió a HOME.')
                return True

            if self.now_sec() - start_time > timeout_sec:
                self.get_logger().warn('Timeout esperando retorno a HOME.')
                return False

            time.sleep(0.1)

        return False

    # =========================================================
    # VISIÓN
    # =========================================================
    def enable_vision(self, enabled: bool):
        msg = Bool()
        msg.data = enabled
        self.vision_enable_pub.publish(msg)
        self.get_logger().info(f'Vision enabled = {enabled}')

    def target_callback(self, msg):
        if self.busy:
            return

        self.last_target = msg
        self.current_target_xyz = (msg.x, msg.y, msg.z)

        self.get_logger().info(
            f'Target recibido: x={msg.x:.3f}, y={msg.y:.3f}, z={msg.z:.3f}'
        )
        self.try_start_cycle()

    def color_callback(self, msg):
        if self.busy:
            return

        self.last_color = msg.data.strip().lower()
        self.current_target_color = self.last_color
        self.get_logger().info(f'Color recibido: {self.last_color}')
        self.try_start_cycle()

    def try_start_cycle(self):
        if self.busy:
            return

        if self.last_target is None or self.last_color is None:
            return

        if self.last_color not in self.bin_drop_xyz:
            self.get_logger().warn(f'Color no reconocido: {self.last_color}')
            self.last_target = None
            self.last_color = None
            return

        self.busy = True
        self.enable_vision(False)

        target = self.last_target
        color = self.last_color

        self.last_target = None
        self.last_color = None

        worker = threading.Thread(
            target=self.execute_pick_and_place,
            args=(target, color),
            daemon=True
        )
        worker.start()

    # =========================================================
    # MOVIMIENTO ARTICULAR
    # =========================================================
    def publish_single_point_trajectory(self, positions, seconds):
        traj = JointTrajectory()
        traj.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint',
        ]

        q_cmd = self.normalize_joint_vector(list(positions))

        if self.current_joints is not None and len(self.current_joints) == 6:
            q_cmd = [
                self.wrap_to_near(q_now, q_des)
                for q_now, q_des in zip(self.current_joints, q_cmd)
            ]
            q_cmd = self.normalize_joint_vector(q_cmd)

        point = JointTrajectoryPoint()
        point.positions = q_cmd
        point.time_from_start.sec = int(seconds)

        traj.points.append(point)
        self.traj_pub.publish(traj)

        self.get_logger().info(f'Trayectoria enviada: {q_cmd}')

    def move_to_joint_waypoint_blocking(self, q_target, move_time_sec=4, timeout_sec=8.0):
        traj = JointTrajectory()
        traj.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint',
        ]

        q_cmd = self.normalize_joint_vector(list(q_target))

        if self.current_joints is not None and len(self.current_joints) == 6:
            q_cmd = [
                self.wrap_to_near(q_now, q_des)
                for q_now, q_des in zip(self.current_joints, q_cmd)
            ]
            q_cmd = self.normalize_joint_vector(q_cmd)
            
            
            

        # Si ya estamos prácticamente en ese waypoint, no reenviar
        if self.current_joints is not None and self.joints_almost_equal(self.current_joints, q_cmd, tol=0.03):
            self.get_logger().info(f'Waypoint ya alcanzado, se omite reenvío: {q_cmd}')
            return True

        point = JointTrajectoryPoint()
        point.positions = q_cmd
        point.time_from_start.sec = int(move_time_sec)

        traj.points.append(point)
        self.traj_pub.publish(traj)

        self.get_logger().info(f'Moviendo a waypoint articular: {q_cmd}')

        start_time = self.now_sec()

        while rclpy.ok():
            if self.joints_close(q_cmd):
                self.get_logger().info('Waypoint articular alcanzado.')
                return True

            if self.now_sec() - start_time > timeout_sec:
                self.get_logger().warn('Timeout esperando waypoint articular.')
                return False

            time.sleep(0.1)

        return False

    # =========================================================
    # PINZA
    # =========================================================
    def call_set_io(self, pin, state, timeout_sec=2.0):
        if self.simulate_gripper:
            self.get_logger().info(f'[SIM_PINZA] pin={pin}, state={state}')
            return True

        if self.io_client is None:
            self.get_logger().error('IO client no disponible')
            return False

        req = SetIO.Request()
        req.fun = 1
        req.pin = pin
        req.state = float(state)

        done_event = threading.Event()
        result_box = {'ok': False}

        future = self.io_client.call_async(req)

        def io_done_callback(fut):
            try:
                res = fut.result()
                result_box['ok'] = bool(res.success) if res is not None else False
            except Exception as e:
                self.get_logger().error(f'Excepción en SetIO pin={pin}, state={state}: {e}')
                result_box['ok'] = False
            finally:
                done_event.set()

        future.add_done_callback(io_done_callback)

        ok_wait = done_event.wait(timeout=timeout_sec)
        if not ok_wait:
            self.get_logger().error(f'Timeout llamando SetIO en pin={pin}, state={state}')
            return False

        return result_box['ok']

    def open_gripper(self):
        self.call_set_io(17, 0)
        self.call_set_io(16, 1)

    def close_gripper(self):
        self.call_set_io(16, 0)
        self.call_set_io(17, 1)

    # =========================================================
    # CICLO PRINCIPAL
    # =========================================================
    def execute_pick_and_place(self, target, color):
        self.get_logger().info(f'Iniciando ciclo pick-and-place para color: {color}')

        x = float(target.x)
        y = float(target.y)
        z = float(target.z)

        if not self.is_target_in_workspace(x, y, z):
            self.get_logger().warn(
                f'Target fuera de workspace: x={x:.3f}, y={y:.3f}, z={z:.3f}'
            )
            self.busy = False
            self.enable_vision(True)
            return

        if self.current_joints is None:
            self.get_logger().error('No hay joint_states actuales para iniciar el pick.')
            self.busy = False
            self.enable_vision(True)
            return

        self.get_logger().info(
            f'Pick continuo: target=({x:.3f}, {y:.3f}, {z:.3f})'
        )

        # ---------------------------------------------------------
        # 1) APPROACH: probar varias alturas y varias semillas IK
        # ---------------------------------------------------------
        approach_z_candidates = [
            z + dz for dz in self.pick_approach_offset_candidates
        ]

        q_approach, used_approach_z = self.solve_stage_ik(
            x=x,
            y=y,
            z_candidates=approach_z_candidates,
            preferred_seed=self.current_joints,
            stage_name='approach'
        )

        if q_approach is None:
            self.get_logger().warn('No se pudo resolver IK para approach.')
            self.return_home_and_wait(timeout_sec=7.0)
            self.busy = False
            self.enable_vision(True)
            return

        ok = self.move_to_joint_waypoint_blocking(
            q_approach,
            move_time_sec=5,
            timeout_sec=8.0
        )
        if not ok:
            self.return_home_and_wait(timeout_sec=7.0)
            self.busy = False
            self.enable_vision(True)
            return

        # ---------------------------------------------------------
        # 2) PICK: probar varias alturas de contacto
        # IMPORTANTE:
        # como tool0 no es necesariamente la punta de la pinza,
        # NO intentamos ir directo a z+0.00
        # ---------------------------------------------------------
        pick_z_candidates = [
            z + dz for dz in self.pick_contact_offset_candidates
        ]

        q_pick, used_pick_z = self.solve_stage_ik(
            x=x,
            y=y,
            z_candidates=pick_z_candidates,
            preferred_seed=q_approach,
            stage_name='pick'
        )

        if q_pick is None:
            self.get_logger().warn('No se pudo resolver IK para pick.')
            self.return_home_and_wait(timeout_sec=7.0)
            self.busy = False
            self.enable_vision(True)
            return

        ok = self.move_to_joint_waypoint_blocking(
            q_pick,
            move_time_sec=3,
            timeout_sec=6.0
        )
        if not ok:
            self.return_home_and_wait(timeout_sec=7.0)
            self.busy = False
            self.enable_vision(True)
            return

        self.close_gripper()
        time.sleep(0.3)

        # ---------------------------------------------------------
        # 3) RETREAT: subir con varias opciones
        # ---------------------------------------------------------
        retreat_z_candidates = [
            z + dz for dz in self.pick_retreat_offset_candidates
        ]

        q_retreat, used_retreat_z = self.solve_stage_ik(
            x=x,
            y=y,
            z_candidates=retreat_z_candidates,
            preferred_seed=q_pick,
            stage_name='retreat'
        )

        if q_retreat is None:
            self.get_logger().warn('No se pudo resolver IK para retreat.')
            self.return_home_and_wait(timeout_sec=7.0)
            self.busy = False
            self.enable_vision(True)
            return

        ok = self.move_to_joint_waypoint_blocking(
            q_retreat,
            move_time_sec=3,
            timeout_sec=6.0
        )
        if not ok:
            self.return_home_and_wait(timeout_sec=7.0)
            self.busy = False
            self.enable_vision(True)
            return

        # ---------------------------------------------------------
        # 4) Volver a HOME
        # ---------------------------------------------------------
        ok = self.move_to_joint_waypoint_blocking(
            self.home_position,
            move_time_sec=4,
            timeout_sec=7.0
        )
        if not ok:
            self.busy = False
            self.enable_vision(True)
            return

        # ---------------------------------------------------------
        # 5) Ir al bin por color
        # OJO: si nunca entra aquí, el problema NO es la caja,
        # sino que falló antes en approach/pick/retreat
        # ---------------------------------------------------------
        if self.use_bins:
            if self.bin_approach_joints[color] is None or self.bin_drop_joints[color] is None:
                self.get_logger().warn(
                    f'Waypoints de caja para {color} aún no definidos. Se termina en HOME.'
                )
                self.open_gripper()
                self.busy = False
                self.enable_vision(True)
                return

            ok = self.move_to_joint_waypoint_blocking(
                self.bin_approach_joints[color],
                move_time_sec=6,
                timeout_sec=10.0
            )
            if not ok:
                self.get_logger().warn(f'Falló bin_approach para color {color}. Reintentando una vez...')
                ok = self.move_to_joint_waypoint_blocking(
                    self.bin_approach_joints[color],
                    move_time_sec=7,
                    timeout_sec=12.0
                )
                if not ok:
                    self.return_home_and_wait(timeout_sec=7.0)
                    self.busy = False
                    self.enable_vision(True)
                    return

            ok = self.move_to_joint_waypoint_blocking(
                self.bin_drop_joints[color],
                move_time_sec=4,
                timeout_sec=8.0
            )
            if not ok:
                self.get_logger().warn(f'Falló bin_drop para color {color}. Reintentando una vez...')
                ok = self.move_to_joint_waypoint_blocking(
                    self.bin_drop_joints[color],
                    move_time_sec=5,
                    timeout_sec=10.0
                )
                if not ok:
                    self.return_home_and_wait(timeout_sec=7.0)
                    self.busy = False
                    self.enable_vision(True)
                    return

            self.open_gripper()

            if not self.joints_almost_equal(
                self.bin_approach_joints[color],
                self.bin_drop_joints[color],
                tol=0.03
            ):
                self.move_to_joint_waypoint_blocking(
                    self.bin_approach_joints[color],
                    move_time_sec=3,
                    timeout_sec=6.0
                )

            self.move_to_joint_waypoint_blocking(
                self.home_position,
                move_time_sec=4,
                timeout_sec=7.0
            )
        else:
            self.get_logger().info('Modo prueba: cajas desactivadas. Se termina en HOME.')
            self.open_gripper()

        self.busy = False
        self.enable_vision(True)
        self.get_logger().info(
            f'Ciclo terminado. '
            f'approach_z={used_approach_z:.3f}, pick_z={used_pick_z:.3f}, retreat_z={used_retreat_z:.3f}'
        )

    # =========================================================
    # MARKERS
    # =========================================================
    def publish_markers(self):
        marker_array = MarkerArray()
        now = self.get_clock().now().to_msg()

        if self.home_tcp_xyz is not None:
            marker_array.markers.append(
                self.make_sphere_marker(
                    marker_id=0,
                    xyz=self.home_tcp_xyz,
                    rgba=(1.0, 1.0, 1.0, 1.0),
                    scale=0.06,
                    frame_id='base_link',
                    stamp=now,
                    ns='home'
                )
            )

            marker_array.markers.append(
                self.make_text_marker(
                    marker_id=1,
                    xyz=(
                        self.home_tcp_xyz[0],
                        self.home_tcp_xyz[1],
                        self.home_tcp_xyz[2] + 0.08
                    ),
                    text='HOME',
                    rgba=(1.0, 1.0, 1.0, 1.0),
                    frame_id='base_link',
                    stamp=now,
                    ns='home_text'
                )
            )

        bin_colors = {
            'rojo': (1.0, 0.0, 0.0, 0.9),
            'azul': (0.0, 0.2, 1.0, 0.9),
            'verde': (0.0, 1.0, 0.0, 0.9),
            'amarillo': (1.0, 1.0, 0.0, 0.9),
        }

        base_id = 100
        for i, name in enumerate(['rojo', 'azul', 'verde', 'amarillo']):
            xyz = self.bin_marker_xyz[name]
            rgba = bin_colors[name]

            marker_array.markers.append(
                self.make_cube_marker(
                    marker_id=base_id + i * 2,
                    xyz=xyz,
                    rgba=rgba,
                    scale_xyz=(0.06, 0.06, 0.06),
                    frame_id='base_link',
                    stamp=now,
                    ns='bins'
                )
            )

            marker_array.markers.append(
                self.make_text_marker(
                    marker_id=base_id + i * 2 + 1,
                    xyz=(xyz[0], xyz[1], xyz[2] + 0.08),
                    text=name.upper(),
                    rgba=rgba,
                    frame_id='base_link',
                    stamp=now,
                    ns='bins_text'
                )
            )

        if self.current_target_xyz is not None:
            rgba = (1.0, 0.0, 1.0, 1.0)

            marker_array.markers.append(
                self.make_sphere_marker(
                    marker_id=200,
                    xyz=self.current_target_xyz,
                    rgba=rgba,
                    scale=0.05,
                    frame_id='base_link',
                    stamp=now,
                    ns='target'
                )
            )

            label = 'TARGET'
            if self.current_target_color is not None:
                label = f'TARGET {self.current_target_color.upper()}'

            marker_array.markers.append(
                self.make_text_marker(
                    marker_id=201,
                    xyz=(
                        self.current_target_xyz[0],
                        self.current_target_xyz[1],
                        self.current_target_xyz[2] + 0.08
                    ),
                    text=label,
                    rgba=rgba,
                    frame_id='base_link',
                    stamp=now,
                    ns='target_text'
                )
            )

        self.marker_pub.publish(marker_array)

    def make_sphere_marker(self, marker_id, xyz, rgba, scale, frame_id, stamp, ns):
        marker = Marker()
        marker.header.frame_id = frame_id
        marker.header.stamp = stamp
        marker.ns = ns
        marker.id = marker_id
        marker.type = Marker.SPHERE
        marker.action = Marker.ADD
        marker.pose.position.x = float(xyz[0])
        marker.pose.position.y = float(xyz[1])
        marker.pose.position.z = float(xyz[2])
        marker.pose.orientation.w = 1.0
        marker.scale.x = scale
        marker.scale.y = scale
        marker.scale.z = scale
        marker.color.r = rgba[0]
        marker.color.g = rgba[1]
        marker.color.b = rgba[2]
        marker.color.a = rgba[3]
        return marker

    def make_cube_marker(self, marker_id, xyz, rgba, scale_xyz, frame_id, stamp, ns):
        marker = Marker()
        marker.header.frame_id = frame_id
        marker.header.stamp = stamp
        marker.ns = ns
        marker.id = marker_id
        marker.type = Marker.CUBE
        marker.action = Marker.ADD
        marker.pose.position.x = float(xyz[0])
        marker.pose.position.y = float(xyz[1])
        marker.pose.position.z = float(xyz[2])
        marker.pose.orientation.w = 1.0
        marker.scale.x = float(scale_xyz[0])
        marker.scale.y = float(scale_xyz[1])
        marker.scale.z = float(scale_xyz[2])
        marker.color.r = rgba[0]
        marker.color.g = rgba[1]
        marker.color.b = rgba[2]
        marker.color.a = rgba[3]
        return marker

    def make_text_marker(self, marker_id, xyz, text, rgba, frame_id, stamp, ns):
        marker = Marker()
        marker.header.frame_id = frame_id
        marker.header.stamp = stamp
        marker.ns = ns
        marker.id = marker_id
        marker.type = Marker.TEXT_VIEW_FACING
        marker.action = Marker.ADD
        marker.pose.position.x = float(xyz[0])
        marker.pose.position.y = float(xyz[1])
        marker.pose.position.z = float(xyz[2])
        marker.pose.orientation.w = 1.0
        marker.scale.z = 0.05
        marker.color.r = rgba[0]
        marker.color.g = rgba[1]
        marker.color.b = rgba[2]
        marker.color.a = rgba[3]
        marker.text = text
        return marker


def main(args=None):
    rclpy.init(args=args)
    node = UR3PickSort()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
