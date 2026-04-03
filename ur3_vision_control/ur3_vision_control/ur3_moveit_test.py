import sys
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped

from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    Constraints,
    PositionConstraint,
    OrientationConstraint,
    BoundingVolume,
    MotionPlanRequest,
    WorkspaceParameters,
)
from shape_msgs.msg import SolidPrimitive
from rclpy.action import ActionClient


class UR3MoveItTest(Node):

    def __init__(self):
        super().__init__('ur3_moveit_test')

        self.move_group_client = ActionClient(self, MoveGroup, '/move_action')

        self.get_logger().info('Esperando action server /move_action ...')
        self.move_group_client.wait_for_server()
        self.get_logger().info('Conectado a /move_action')

    def send_goal(self):
        goal_msg = MoveGroup.Goal()

        request = MotionPlanRequest()
        request.group_name = 'ur_manipulator'
        request.num_planning_attempts = 10
        request.allowed_planning_time = 5.0
        request.max_velocity_scaling_factor = 0.1
        request.max_acceleration_scaling_factor = 0.1

        request.workspace_parameters = WorkspaceParameters()
        request.workspace_parameters.header.frame_id = 'base_link'
        request.workspace_parameters.min_corner.x = -1.0
        request.workspace_parameters.min_corner.y = -1.0
        request.workspace_parameters.min_corner.z = -1.0
        request.workspace_parameters.max_corner.x = 1.0
        request.workspace_parameters.max_corner.y = 1.0
        request.workspace_parameters.max_corner.z = 1.0

        constraints = Constraints()

        # OBJETIVO DE PRUEBA
        # ajustaremos luego con vision
        target_x = 0.20
        target_y = 0.00
        target_z = 0.20

        # restricción de posición
        pos_constraint = PositionConstraint()
        pos_constraint.header.frame_id = 'base_link'
        pos_constraint.link_name = 'tool0'

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = [0.01, 0.01, 0.01]

        pose = PoseStamped()
        pose.header.frame_id = 'base_link'
        pose.pose.position.x = target_x
        pose.pose.position.y = target_y
        pose.pose.position.z = target_z
        pose.pose.orientation.w = 1.0

        bounding_volume = BoundingVolume()
        bounding_volume.primitives.append(primitive)
        bounding_volume.primitive_poses.append(pose.pose)

        pos_constraint.constraint_region = bounding_volume
        pos_constraint.weight = 1.0

        # restricción de orientación
        ori_constraint = OrientationConstraint()
        ori_constraint.header.frame_id = 'base_link'
        ori_constraint.link_name = 'tool0'

        # orientación inicial simple, luego la ajustamos
        ori_constraint.orientation.x = 0.0
        ori_constraint.orientation.y = 1.0
        ori_constraint.orientation.z = 0.0
        ori_constraint.orientation.w = 0.0

        ori_constraint.absolute_x_axis_tolerance = 0.2
        ori_constraint.absolute_y_axis_tolerance = 0.2
        ori_constraint.absolute_z_axis_tolerance = 0.2
        ori_constraint.weight = 1.0

        constraints.position_constraints.append(pos_constraint)
        constraints.orientation_constraints.append(ori_constraint)

        request.goal_constraints.append(constraints)

        goal_msg.request = request
        goal_msg.planning_options.plan_only = False

        self.get_logger().info(
            f'Enviando pose objetivo: x={target_x:.3f}, y={target_y:.3f}, z={target_z:.3f}'
        )

        future = self.move_group_client.send_goal_async(goal_msg)
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goal rechazado')
            return

        self.get_logger().info('Goal aceptado, esperando resultado...')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result
        error_code = result.error_code.val
        self.get_logger().info(f'Resultado MoveIt, error_code={error_code}')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = UR3MoveItTest()
    node.send_goal()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
