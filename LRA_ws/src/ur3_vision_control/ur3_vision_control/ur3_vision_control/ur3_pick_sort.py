import rclpy
import threading
import math
import time

from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
import tf2_ros

from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import Point
from std_msgs.msg import Bool, Int32
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

        self.current_joints_raw = None

        self.declare_parameter('simulate_gripper', True)
        self.declare_parameter('offset_x', 0.0)
        self.declare_parameter('offset_y', 0.0)

        self.simulate_gripper = bool(self.get_parameter('simulate_gripper').value)
        self.offset_x = float(self.get_parameter('offset_x').value)
        self.offset_y = float(self.get_parameter('offset_y').value)

        self.get_logger().info(f'simulate_gripper = {self.simulate_gripper}')
        self.get_logger().info(f'offset_x = {self.offset_x}')
        self.get_logger().info(f'offset_y = {self.offset_y}')

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
        self.use_bins = True

        # =========================================================
        # PUBLICADORES
        # =========================================================
        self.traj_pub = self.create_publisher(
            JointTrajectory,
            '/scaled_joint_trajectory_controller/joint_trajectory',
            10
        )

        # Latched: un detector que arranca DESPUÉS de este nodo recibe igualmente
        # el último estado de /vision_enable al suscribirse.
        vision_enable_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.vision_enable_pub = self.create_publisher(
            Bool,
            '/vision_enable',
            vision_enable_qos
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
        # IMPORTANTE: queue=1 para target/caja para que NO se acumulen
        # mensajes viejos de ciclos anteriores. Solo nos interesa el ÚLTIMO.
        self.target_sub = self.create_subscription(
            Point,
            '/ur3/target_point',
            self.target_callback,
            1
        )

        self.caja_sub_int = self.create_subscription(
            Int32,
            '/tapones/caja_asignada',
            self.caja_int_callback,
            1
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
        # MOVEIT IK
        # =========================================================
        self.arm_joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint',
        ]

        self.moveit_group_name = 'ur_manipulator'
        self.ik_link_name = 'tool0'
        self.pose_frame = 'base_link'

        self.pick_orientation_candidates = [
            self.quaternion_from_euler(math.pi, 0.0, 0.0),
            self.quaternion_from_euler(math.pi, 0.0, math.pi / 2.0),
            self.quaternion_from_euler(math.pi, 0.0, -math.pi / 2.0),
            self.quaternion_from_euler(math.pi, 0.0, math.pi),
        ]

        # =========================================================
        # CONFIGURACIÓN DE PINZA Y TFS (23 cm total)
        # =========================================================
        self.distancia_gripper = 0.137
        self.distancia_ventosa = 0.093
        self.longitud_total_tcp = self.distancia_gripper + self.distancia_ventosa

        self.compression_offset = 0.005

        self.pick_contact_offset_z = self.longitud_total_tcp - self.compression_offset
        self.pick_approach_offset_z = self.longitud_total_tcp + 0.08
        self.pick_retreat_offset_z = self.longitud_total_tcp + 0.12

        self.pick_approach_offset_candidates = [
            self.pick_approach_offset_z,
            self.pick_approach_offset_z - 0.02,
            self.pick_approach_offset_z + 0.02
        ]

        self.pick_contact_offset_candidates = [
            self.pick_contact_offset_z,
            self.pick_contact_offset_z - 0.005,
            self.pick_contact_offset_z + 0.005
        ]

        self.pick_retreat_offset_candidates = [
            self.pick_retreat_offset_z,
            self.pick_retreat_offset_z + 0.02,
            self.pick_retreat_offset_z + 0.04
        ]

        self.ik_timeout_sec = 2.0
        self.allow_ik_collision_fallback = True

        self.compute_ik_client = self.create_client(
            GetPositionIK,
            '/compute_ik'
        )

        while not self.compute_ik_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Esperando servicio /compute_ik ...')

        # =========================================================
        # HOME
        # =========================================================
        self.home_position = self.normalize_joint_vector([
            math.radians(-88),
            math.radians(-99),
            math.radians(-60),
            math.radians(-109),
            math.radians(90),
            math.radians(330)
        ])

        self.preferred_pick_branch = list(self.home_position)
        self.joint_cost_weights = [1.0, 4.0, 3.5, 2.0, 2.0, 1.0]
        self.branch_preference_gain = 0.20
        self.max_jump = [2.40, 2.20, 2.40, 2.60, 1.80, 2.80]

        # =========================================================
        # PICKS MULTICELDA
        # =========================================================
        self.pick_cells = [
            {
                'name': 'cell_1',
                'xy': (-0.46, 0.25),
                'approach': [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
                'pick':     [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
            },
            {
                'name': 'cell_2',
                'xy': (-0.42, 0.25),
                'approach': [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
                'pick':     [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
            },
            {
                'name': 'cell_3',
                'xy': (-0.38, 0.25),
                'approach': [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
                'pick':     [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
            },
            {
                'name': 'cell_4',
                'xy': (-0.46, 0.20),
                'approach': [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
                'pick':     [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
            },
            {
                'name': 'cell_5',
                'xy': (-0.42, 0.20),
                'approach': [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
                'pick':     [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
            },
            {
                'name': 'cell_6',
                'xy': (-0.38, 0.20),
                'approach': [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
                'pick':     [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
            },
            {
                'name': 'cell_7',
                'xy': (-0.48, 0.28),
                'approach': [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
                'pick':     [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
            },
            {
                'name': 'cell_8',
                'xy': (-0.46, 0.30),
                'approach': [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
                'pick':     [math.radians(-10), math.radians(-200), math.radians(45), math.radians(230), math.radians(90), math.radians(-120)],
            },
        ]

        for cell in self.pick_cells:
            cell['approach'] = self.normalize_joint_vector(cell['approach'])
            cell['pick'] = self.normalize_joint_vector(cell['pick'])

        # =========================================================
        # WAYPOINTS DE COLORES
        # =========================================================
        deg = math.radians

        negro_point    = [deg(-216), deg(-80),  deg(-98),  deg(-94),  deg(90), deg(-30)]
        blanco_point   = [deg(-204), deg(-97),  deg(-77),  deg(-94),  deg(90), deg(-30)]
        amarillo_point = [deg(-241), deg(-70),  deg(-104), deg(-96),  deg(88), deg(-30)]
        verde_point    = [deg(-223), deg(-139), deg(-14),  deg(-118), deg(90), deg(-35)]
        azul_point     = [deg(-236), deg(-114), deg(-56),  deg(-99),  deg(90), deg(-50)]
        rojo_point     = [deg(-252), deg(-108), deg(-68),  deg(-96),  deg(87), deg(-60)]

        negro_approach    = negro_point
        negro_drop        = [negro_point[0], negro_point[1]-deg(1), negro_point[2]-deg(15), negro_point[3]+deg(18), negro_point[4], negro_point[5]]

        blanco_approach   = blanco_point
        blanco_drop       = [blanco_point[0], blanco_point[1]-deg(2), blanco_point[2]-deg(18), blanco_point[3]+deg(20), blanco_point[4], blanco_point[5]]

        rojo_approach     = rojo_point
        rojo_drop         = [rojo_point[0], rojo_point[1]-deg(1), rojo_point[2]-deg(14), rojo_point[3]+deg(16), rojo_point[4], rojo_point[5]]

        azul_approach     = azul_point
        azul_drop         = [azul_point[0], azul_point[1]+deg(1), azul_point[2]-deg(13), azul_point[3]+deg(12), azul_point[4], azul_point[5]]

        verde_approach    = verde_point
        verde_drop        = [verde_point[0], verde_point[1]+deg(8), verde_point[2]-deg(30), verde_point[3]+deg(23), verde_point[4], verde_point[5]]

        amarillo_approach = amarillo_point
        amarillo_drop     = [amarillo_point[0], amarillo_point[1]-deg(0), amarillo_point[2]-deg(18), amarillo_point[3]+deg(19), amarillo_point[4], amarillo_point[5]]

        self.bin_approach_joints = {
            '1': rojo_approach,   '2': azul_approach,  '3': verde_approach,
            '4': amarillo_approach, '5': negro_approach, '6': blanco_approach,
            'rojo': rojo_approach, 'azul': azul_approach, 'verde': verde_approach,
            'amarillo': amarillo_approach, 'negro': negro_approach, 'blanco': blanco_approach,
        }

        self.bin_drop_joints = {
            '1': rojo_drop,   '2': azul_drop,  '3': verde_drop,
            '4': amarillo_drop, '5': negro_drop, '6': blanco_drop,
            'rojo': rojo_drop, 'azul': azul_drop, 'verde': verde_drop,
            'amarillo': amarillo_drop, 'negro': negro_drop, 'blanco': blanco_drop,
        }

        for color in self.bin_approach_joints:
            self.bin_approach_joints[color] = self.normalize_joint_vector(self.bin_approach_joints[color])
            self.bin_drop_joints[color]     = self.normalize_joint_vector(self.bin_drop_joints[color])

        # =========================================================
        # POSICIONES XYZ CAJAS
        # =========================================================
        self.bin_drop_xyz = {
            '1': (0.00, -0.39, 0.15),   '2': (0.14, -0.39, 0.15),   '3': (0.28, -0.39, 0.15),
            '4': (0.00, -0.245, 0.15),  '5': (0.14, -0.245, 0.15),  '6': (0.28, -0.245, 0.15),
            'rojo': (0.00, -0.39, 0.15),   'azul': (0.14, -0.39, 0.15),
            'verde': (0.28, -0.39, 0.15),  'amarillo': (0.00, -0.245, 0.15),
            'negro': (0.14, -0.245, 0.15), 'blanco': (0.28, -0.245, 0.15),
        }

        self.bin_marker_xyz = {
            '1': (0.00, -0.39, 0.15),   '2': (0.14, -0.39, 0.15),   '3': (0.28, -0.39, 0.15),
            '4': (0.00, -0.245, 0.15),  '5': (0.14, -0.245, 0.15),  '6': (0.28, -0.245, 0.15),
            'rojo': (0.00, -0.39, 0.15),   'azul': (0.14, -0.39, 0.15),
            'verde': (0.28, -0.39, 0.15),  'amarillo': (0.00, -0.245, 0.15),
            'negro': (0.14, -0.245, 0.15), 'blanco': (0.28, -0.245, 0.15),
        }

        self.home_marker_xyz = (0.15, 0.20, 0.25)

        # =========================================================
        # WORKSPACE
        # =========================================================
        self.workspace_limits = {
            'x_min': -0.60, 'x_max': 0.80,
            'y_min': -0.30, 'y_max': 0.55,
            'z_min': 0.0001, 'z_max': 0.30,
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
        cr = math.cos(roll * 0.5); sr = math.sin(roll * 0.5)
        cp = math.cos(pitch * 0.5); sp = math.sin(pitch * 0.5)
        cy = math.cos(yaw * 0.5);  sy = math.sin(yaw * 0.5)
        return {
            'x': sr * cp * cy - cr * sp * sy,
            'y': cr * sp * cy + sr * cp * sy,
            'z': cr * cp * sy - sr * sp * cy,
            'w': cr * cp * cy + sr * sp * sy,
        }

    def is_front_pick_branch(self, q_vec):
        q = self.normalize_joint_vector(q_vec)
        return (-2.65 < q[1] < 0.35 and abs(q[4]) > 0.20)

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
        lim = self.workspace_limits
        return (lim['x_min'] <= x <= lim['x_max'] and
                lim['y_min'] <= y <= lim['y_max'] and
                lim['z_min'] <= z <= lim['z_max'])

    def build_pick_pose(self, x, y, z, orientation=None):
        pose_stamped = PoseStamped()
        pose_stamped.header.frame_id = self.pose_frame
        pose_stamped.header.stamp = self.get_clock().now().to_msg()
        pose_stamped.pose.position.x = float(x)
        pose_stamped.pose.position.y = float(y)
        pose_stamped.pose.position.z = float(z)
        if orientation is None:
            orientation = self.quaternion_from_euler(math.pi, 0.0, 0.0)
        pose_stamped.pose.orientation.x = orientation['x']
        pose_stamped.pose.orientation.y = orientation['y']
        pose_stamped.pose.orientation.z = orientation['z']
        pose_stamped.pose.orientation.w = orientation['w']
        return pose_stamped

    def build_robot_state_from_seed(self, seed_joints):
        state = RobotState()
        state.joint_state.name = list(self.arm_joint_names)
        state.joint_state.position = [float(q) for q in self.normalize_joint_vector(seed_joints)]
        return state

    def extract_arm_joints_from_solution(self, solution_state):
        joint_map = dict(zip(solution_state.joint_state.name, solution_state.joint_state.position))
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
        q_sol = [self.wrap_to_near(qs, qd) for qs, qd in zip(seed_joints, q_sol)]
        q_sol = self.normalize_joint_vector(q_sol)
        return q_sol

    def joint_path_cost(self, q_ref, q_target):
        if q_ref is None or q_target is None:
            return float('inf')
        q_ref    = self.normalize_joint_vector(q_ref)
        q_target = self.normalize_joint_vector(q_target)
        motion_cost = sum(w * self.angle_distance(a, b) for w, a, b in zip(self.joint_cost_weights, q_ref, q_target))
        branch_cost = self.branch_preference_gain * sum(
            w * self.angle_distance(a, b)
            for w, a, b in zip(self.joint_cost_weights, q_target, self.preferred_pick_branch)
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

        add_seed(preferred_seed)
        add_seed(self.current_joints)
        add_seed(self.home_position)
        return seeds

    def solve_stage_ik(self, x, y, z_candidates, preferred_seed=None, stage_name='stage'):
        seeds = self.build_ik_seed_candidates(preferred_seed=preferred_seed)
        q_ref = self.normalize_joint_vector(preferred_seed if preferred_seed is not None else self.current_joints)

        collision_modes = [True]
        if self.allow_ik_collision_fallback:
            collision_modes.append(False)

        # Probamos las semillas EN ORDEN: la primera (preferred_seed) es una pose
        # FIJA del área de pick, no el estado actual del robot. En cuanto una
        # semilla produce soluciones válidas nos quedamos con la de menor coste y
        # NO probamos las siguientes. Así, ante el mismo (x, y) el resultado
        # depende solo de la semilla fija → trayectorias repetibles entre arranques.
        for seed in seeds:
            found = []
            for avoid_collisions in collision_modes:
                for z_goal in z_candidates:
                    for orientation in self.pick_orientation_candidates:
                        pose = self.build_pick_pose(x, y, z_goal, orientation=orientation)
                        q_sol = self.compute_ik_joints(pose_stamped=pose, seed_joints=seed,
                                                       timeout_sec=self.ik_timeout_sec,
                                                       avoid_collisions=avoid_collisions)
                        if q_sol is None:
                            continue
                        q_sol = self.normalize_joint_vector(q_sol)
                        if stage_name in ('approach', 'pick') and not self.is_front_pick_branch(q_sol):
                            continue
                        too_far = any(
                            self.angle_distance(q_ref[i], q_sol[i]) > lim
                            for i, lim in enumerate(self.max_jump)
                        )
                        if too_far:
                            continue
                        found.append({'q': q_sol, 'z_goal': z_goal,
                                      'cost': self.joint_path_cost(q_ref, q_sol),
                                      'avoid_collisions': avoid_collisions})
                if found:
                    break

            if found:
                best = min(found, key=lambda item: item['cost'])
                self.get_logger().info(
                    f'IK OK para {stage_name}: z_goal={best["z_goal"]:.3f}, '
                    f'avoid_collisions={best["avoid_collisions"]}, cost={best["cost"]:.3f}'
                )
                return best['q'], best['z_goal']

        self.get_logger().warn(f'No se encontró IK para {stage_name}.')
        return None, None

    def get_nearest_pick_cell(self, x, y):
        best_cell, best_dist = None, float('inf')
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
        self.remove_collision_object('table')
        self.remove_collision_object('back_wall')
        time.sleep(0.3)
        self.add_table_collision()
        time.sleep(1.0)
        self.table_added = True

    def remove_collision_object(self, object_id):
        obj = CollisionObject()
        obj.header.frame_id = 'world'
        obj.id = object_id
        obj.operation = CollisionObject.REMOVE
        self.collision_object_pub.publish(obj)
        self.get_logger().info(f'Objeto de colisión eliminado: {object_id}')

    def add_back_wall_collision(self):
        obj = CollisionObject()
        obj.header.frame_id = 'world'
        obj.id = 'back_wall'
        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = [0.06, 0.90, 0.60]
        pose = Pose()
        pose.position.x = -0.25
        pose.position.y = 0.00
        pose.position.z = 0.30
        pose.orientation.w = 1.0
        obj.primitives.append(primitive)
        obj.primitive_poses.append(pose)
        obj.operation = CollisionObject.ADD
        self.collision_object_pub.publish(obj)
        self.get_logger().info('Pared trasera agregada.')

    def add_table_collision(self):
        obj = CollisionObject()
        obj.header.frame_id = 'world'
        obj.id = 'table'
        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = [1.40, 0.90, 0.04]
        pose = Pose()
        pose.position.x = 0.20
        pose.position.y = -0.10
        pose.position.z = -0.02
        pose.orientation.x = 0.0
        pose.orientation.y = 0.0
        pose.orientation.z = -0.70710678
        pose.orientation.w =  0.70710678
        obj.primitives.append(primitive)
        obj.primitive_poses.append(pose)
        obj.operation = CollisionObject.ADD
        self.collision_object_pub.publish(obj)
        self.get_logger().info('Mesa agregada como objeto de colisión.')

    # =========================================================
    # JOINT STATES
    # =========================================================
    def joint_state_callback(self, msg):
        wanted = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
                  'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
        joint_map = dict(zip(msg.name, msg.position))
        try:
            raw = [joint_map[name] for name in wanted]
            self.current_joints_raw = list(raw)
            self.current_joints = self.normalize_joint_vector(raw)
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
        """
        Se ejecuta periódicamente al arrancar.
        Cuando el robot llega a HOME por primera vez, marca el sistema como listo
        y activa la visión publicando /vision_enable=True. El calibrator y el
        detector los lanza el HMI; el detector reacciona a /vision_enable.
        """
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
            self.get_logger().info('Robot en HOME. Visión activada.')

    def update_home_marker_from_tf(self):
        try:
            tf_msg = self.tf_buffer.lookup_transform('base_link', 'tool0', rclpy.time.Time())
            self.home_tcp_xyz = (
                tf_msg.transform.translation.x,
                tf_msg.transform.translation.y,
                tf_msg.transform.translation.z,
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
        self.get_logger().info(f'Target recibido: x={msg.x:.3f}, y={msg.y:.3f}, z={msg.z:.3f}')
        self.try_start_cycle()

    def caja_int_callback(self, msg):
        if self.busy:
            return
        self.last_color = str(msg.data)
        self.current_target_color = self.last_color
        self.get_logger().info(f'Caja recibida INT32: usada="{self.last_color}"')
        self.try_start_cycle()

    def color_callback(self, msg):
        if self.busy:
            return
        raw = str(msg.data).strip().lower()
        normalized = raw.replace('caja', '').replace('_', '').replace('-', '').replace(':', '').strip()
        self.last_color = normalized if normalized.isdigit() else raw
        self.current_target_color = self.last_color
        self.get_logger().info(f'Caja recibida STRING: raw="{raw}" -> usada="{self.last_color}"')
        self.try_start_cycle()

    def try_start_cycle(self):
        if self.busy:
            return
        if self.last_target is None or self.last_color is None:
            return
        if self.last_color not in self.bin_drop_joints:
            self.get_logger().warn(f'Caja/clasificación no reconocida: {self.last_color}')
            self.last_target = None
            self.last_color = None
            return

        self.busy = True
        self.enable_vision(False)

        target = self.last_target
        color  = self.last_color
        self.last_target = None
        self.last_color  = None

        threading.Thread(
            target=self.execute_pick_and_place,
            args=(target, color),
            daemon=True
        ).start()

    # =========================================================
    # MOVIMIENTO ARTICULAR
    # =========================================================
    def publish_single_point_trajectory(self, positions, seconds):
        traj = JointTrajectory()
        traj.joint_names = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
                            'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
        q_des = self.normalize_joint_vector(list(positions))
        if self.current_joints_raw is not None and len(self.current_joints_raw) == 6:
            q_cmd = [self.wrap_to_near(qn, qt) for qn, qt in zip(self.current_joints_raw, q_des)]
        else:
            q_cmd = q_des
        point = JointTrajectoryPoint()
        point.positions = [float(q) for q in q_cmd]
        point.time_from_start.sec = int(seconds)
        traj.points.append(point)
        self.traj_pub.publish(traj)
        self.get_logger().info(f'Trayectoria enviada: {q_cmd}')

    def move_to_joint_waypoint_blocking(self, q_target, move_time_sec=4, timeout_sec=8.0):
        traj = JointTrajectory()
        traj.joint_names = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint',
                            'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
        q_des = self.normalize_joint_vector(list(q_target))
        if self.current_joints_raw is not None and len(self.current_joints_raw) == 6:
            q_cmd = [self.wrap_to_near(qn, qt) for qn, qt in zip(self.current_joints_raw, q_des)]
        else:
            q_cmd = q_des

        q_now_norm = (self.normalize_joint_vector(self.current_joints_raw)
                      if self.current_joints_raw is not None else self.current_joints)

        if q_now_norm is not None and self.joints_almost_equal(
            q_now_norm, self.normalize_joint_vector(q_cmd), tol=0.03
        ):
            self.get_logger().info(f'Waypoint ya alcanzado, omitiendo: {q_cmd}')
            return True

        point = JointTrajectoryPoint()
        point.positions = [float(q) for q in q_cmd]
        point.time_from_start.sec = int(move_time_sec)
        traj.points.append(point)
        self.traj_pub.publish(traj)
        self.get_logger().info(f'Moviendo a waypoint articular: {q_cmd}')

        start_time = self.now_sec()
        while rclpy.ok():
            if self.current_joints_raw is not None:
                if all(self.angle_distance(qn, qd) <= 0.03
                       for qn, qd in zip(self.current_joints_raw, q_cmd)):
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
            finally:
                done_event.set()

        future.add_done_callback(io_done_callback)
        if not done_event.wait(timeout=timeout_sec):
            self.get_logger().error(f'Timeout SetIO pin={pin}, state={state}')
            return False
        return result_box['ok']

    def open_gripper(self):
        self.call_set_io(4, 0)

    def close_gripper(self):
        self.call_set_io(4, 1)

    # =========================================================
    # CICLO PRINCIPAL
    # =========================================================
    def execute_pick_and_place(self, target, color):
        self.get_logger().info(f'Iniciando ciclo pick-and-place para: {color}')

        x = float(target.x)
        y = float(target.y)
        z = float(target.z)

        # Helper interno: finalizar ciclo con error (reactiva la visión para recuperación)
        def abort(msg_warn):
            self.get_logger().warn(msg_warn)
            self.return_home_and_wait(timeout_sec=10.0)
            # Limpiar estado para no arrastrar el target fallido
            self.last_target = None
            self.last_color = None
            self.current_target_xyz = None
            self.current_target_color = None
            self.busy = False
            self.enable_vision(True)

        if not self.is_target_in_workspace(x, y, z):
            self.get_logger().warn(f'Target fuera de workspace: ({x:.3f}, {y:.3f}, {z:.3f})')
            self.last_target = None
            self.last_color = None
            self.current_target_xyz = None
            self.current_target_color = None
            self.busy = False
            self.enable_vision(True)
            return

        if self.current_joints is None:
            self.get_logger().error('No hay joint_states actuales.')
            self.last_target = None
            self.last_color = None
            self.current_target_xyz = None
            self.current_target_color = None
            self.busy = False
            self.enable_vision(True)
            return

        # Semilla IK FIJA = pose HOME. Es una rama de pick frontal válida
        # (is_front_pick_branch) y es donde el robot está al iniciar cada ciclo.
        # Usar una semilla fija en vez del estado actual (que varía dentro de la
        # tolerancia de HOME) hace que KDL devuelva la misma solución entre
        # arranques → trayectorias repetibles.
        pick_seed = list(self.home_position)

        # ---------------------------------------------------------
        # 1) APPROACH
        # ---------------------------------------------------------
        q_approach, used_approach_z = self.solve_stage_ik(
            x=x, y=y,
            z_candidates=[z + dz for dz in self.pick_approach_offset_candidates],
            preferred_seed=pick_seed,
            stage_name='approach'
        )
        if q_approach is None:
            abort('No se pudo resolver IK para approach.')
            return

        if not self.move_to_joint_waypoint_blocking(q_approach, move_time_sec=5, timeout_sec=8.0):
            abort('Falló movimiento a approach.')
            return

        # ---------------------------------------------------------
        # 2) PICK
        # ---------------------------------------------------------
        q_pick, used_pick_z = self.solve_stage_ik(
            x=x, y=y,
            z_candidates=[z + dz for dz in self.pick_contact_offset_candidates],
            preferred_seed=pick_seed,
            stage_name='pick'
        )
        if q_pick is None:
            abort('No se pudo resolver IK para pick.')
            return

        if not self.move_to_joint_waypoint_blocking(q_pick, move_time_sec=5, timeout_sec=10.0):
            abort('Falló movimiento a pick.')
            return

        self.close_gripper()
        time.sleep(0.7)   # esperar a que la ventosa/pinza coja firmemente

        # ---------------------------------------------------------
        # 3) RETREAT (volver al approach ya validado)
        # ---------------------------------------------------------

        # ---------------------------------------------------------
        # 4) HOME intermedio  ← NO se lanza detector aquí
        # ---------------------------------------------------------
        if not self.move_to_joint_waypoint_blocking(self.home_position, move_time_sec=4, timeout_sec=10.0):
            abort('Falló movimiento a HOME tras retreat.')
            return

        # ---------------------------------------------------------
        # 5) Ir al bin por color
        # ---------------------------------------------------------
        if self.use_bins:
            if self.bin_approach_joints[color] is None or self.bin_drop_joints[color] is None:
                self.get_logger().warn(f'Waypoints de caja para {color} no definidos.')
                self.open_gripper()
                self.busy = False
                self.enable_vision(True)
                return

            if not self.move_to_joint_waypoint_blocking(
                self.bin_approach_joints[color], move_time_sec=8, timeout_sec=45.0
            ):
                abort(f'Falló bin_approach para {color}.')
                return

            if not self.move_to_joint_waypoint_blocking(
                self.bin_drop_joints[color], move_time_sec=7, timeout_sec=35.0
            ):
                abort(f'Falló bin_drop para {color}.')
                return

            self.open_gripper()
            time.sleep(0.8)   # ← esperar a que el tapón se suelte realmente

            if not self.joints_almost_equal(
                self.bin_approach_joints[color], self.bin_drop_joints[color], tol=0.03
            ):
                self.move_to_joint_waypoint_blocking(
                    self.bin_approach_joints[color], move_time_sec=5, timeout_sec=25.0
                )

            # HOME final del ciclo
            self.move_to_joint_waypoint_blocking(
                self.home_position, move_time_sec=6, timeout_sec=30.0
            )

        else:
            self.get_logger().info('Modo prueba: cajas desactivadas.')
            self.open_gripper()
            time.sleep(0.8)

        # ---------------------------------------------------------
        # FIN DEL CICLO: robot en HOME → reactivar visión para el siguiente tapón
        # ---------------------------------------------------------
        self.get_logger().info(
            f'Ciclo terminado. approach_z={used_approach_z:.3f}, pick_z={used_pick_z:.3f}'
        )

        # ── Limpiar estado para no arrastrar valores del ciclo anterior ──
        self.last_target = None
        self.last_color = None
        self.current_target_xyz = None
        self.current_target_color = None

        self.busy = False
        self.enable_vision(True)   # ← el detector vuelve a muestrear al recibir True

    # =========================================================
    # MARKERS
    # =========================================================
    def publish_markers(self):
        marker_array = MarkerArray()
        now = self.get_clock().now().to_msg()

        if self.home_tcp_xyz is not None:
            marker_array.markers.append(self.make_sphere_marker(
                0, self.home_tcp_xyz, (1.0, 1.0, 1.0, 1.0), 0.06, 'base_link', now, 'home'))
            marker_array.markers.append(self.make_text_marker(
                1, (self.home_tcp_xyz[0], self.home_tcp_xyz[1], self.home_tcp_xyz[2] + 0.08),
                'HOME', (1.0, 1.0, 1.0, 1.0), 'base_link', now, 'home_text'))

        bin_colors = {
            'rojo':     (1.0, 0.0, 0.0, 0.9),
            'azul':     (0.0, 0.2, 1.0, 0.9),
            'verde':    (0.0, 1.0, 0.0, 0.9),
            'amarillo': (1.0, 1.0, 0.0, 0.9),
            'negro':    (0.0, 0.0, 0.0, 0.9),
            'blanco':   (1.0, 1.0, 1.0, 0.9),
        }

        for i, name in enumerate(['rojo', 'azul', 'verde', 'amarillo', 'negro', 'blanco']):
            xyz  = self.bin_marker_xyz[name]
            rgba = bin_colors[name]
            base_id = 100 + i * 2
            marker_array.markers.append(self.make_cube_marker(
                base_id, xyz, rgba, (0.06, 0.06, 0.06), 'base_link', now, 'bins'))
            marker_array.markers.append(self.make_text_marker(
                base_id + 1, (xyz[0], xyz[1], xyz[2] + 0.08),
                name.upper(), rgba, 'base_link', now, 'bins_text'))

        if self.current_target_xyz is not None:
            rgba  = (1.0, 0.0, 1.0, 1.0)
            label = (f'TARGET {self.current_target_color.upper()}'
                     if self.current_target_color else 'TARGET')
            marker_array.markers.append(self.make_sphere_marker(
                200, self.current_target_xyz, rgba, 0.05, 'base_link', now, 'target'))
            marker_array.markers.append(self.make_text_marker(
                201,
                (self.current_target_xyz[0], self.current_target_xyz[1],
                 self.current_target_xyz[2] + 0.08),
                label, rgba, 'base_link', now, 'target_text'))

        self.marker_pub.publish(marker_array)

    def make_sphere_marker(self, marker_id, xyz, rgba, scale, frame_id, stamp, ns):
        m = Marker()
        m.header.frame_id = frame_id; m.header.stamp = stamp
        m.ns = ns; m.id = marker_id; m.type = Marker.SPHERE; m.action = Marker.ADD
        m.pose.position.x = float(xyz[0]); m.pose.position.y = float(xyz[1])
        m.pose.position.z = float(xyz[2]); m.pose.orientation.w = 1.0
        m.scale.x = m.scale.y = m.scale.z = scale
        m.color.r, m.color.g, m.color.b, m.color.a = rgba
        return m

    def make_cube_marker(self, marker_id, xyz, rgba, scale_xyz, frame_id, stamp, ns):
        m = Marker()
        m.header.frame_id = frame_id; m.header.stamp = stamp
        m.ns = ns; m.id = marker_id; m.type = Marker.CUBE; m.action = Marker.ADD
        m.pose.position.x = float(xyz[0]); m.pose.position.y = float(xyz[1])
        m.pose.position.z = float(xyz[2]); m.pose.orientation.w = 1.0
        m.scale.x, m.scale.y, m.scale.z = (float(s) for s in scale_xyz)
        m.color.r, m.color.g, m.color.b, m.color.a = rgba
        return m

    def make_text_marker(self, marker_id, xyz, text, rgba, frame_id, stamp, ns):
        m = Marker()
        m.header.frame_id = frame_id; m.header.stamp = stamp
        m.ns = ns; m.id = marker_id; m.type = Marker.TEXT_VIEW_FACING; m.action = Marker.ADD
        m.pose.position.x = float(xyz[0]); m.pose.position.y = float(xyz[1])
        m.pose.position.z = float(xyz[2]); m.pose.orientation.w = 1.0
        m.scale.z = 0.05
        m.color.r, m.color.g, m.color.b, m.color.a = rgba
        m.text = text
        return m


def main(args=None):
    rclpy.init(args=args)
    node = UR3PickSort()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
