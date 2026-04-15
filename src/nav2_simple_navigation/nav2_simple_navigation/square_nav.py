#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from builtin_interfaces.msg import Duration

import math
import time


class SquareNavigator(Node):

    def __init__(self):
        super().__init__('square_navigator')

        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.get_logger().info('Waiting for Nav2 action server...')
        self.client.wait_for_server()

        self.get_logger().info('Nav2 ready!')

    def create_goal(self, x, y, yaw):
        goal = NavigateToPose.Goal()

        pose = PoseStamped()
        pose.header.frame_id = 'odom'   # IMPORTANT (no map mode)
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = x
        pose.pose.position.y = y

        # Convert yaw → quaternion
        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)

        goal.pose = pose

        return goal

    def send_goal(self, x, y, yaw):
        goal = self.create_goal(x, y, yaw)

        self.get_logger().info(f'Sending goal: x={x}, y={y}, yaw={yaw}')

        future = self.client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)

        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected!')
            return False

        self.get_logger().info('Goal accepted, waiting result...')

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)

        result = result_future.result().result

        self.get_logger().info('Goal reached!')

        return True

    def run_square(self, side_length=1.0):

        # Square corners (odom frame)
        waypoints = [
            (0.0, 0.0, 0.0),
            (side_length, 0.0, 0.0),
            (side_length, side_length, math.pi/2),
            (0.0, side_length, math.pi),
            (0.0, 0.0, -math.pi/2)
        ]

        for (x, y, yaw) in waypoints:
            success = self.send_goal(x, y, yaw)

            if not success:
                self.get_logger().error('Stopping due to failure')
                break

            time.sleep(1.0)  # small pause


def main(args=None):
    rclpy.init(args=args)

    navigator = SquareNavigator()
    navigator.run_square(side_length=5.0)

    navigator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()