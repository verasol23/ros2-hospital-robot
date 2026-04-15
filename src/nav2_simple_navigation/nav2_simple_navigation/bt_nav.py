import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import math

class CircleNavigator(Node):
    def __init__(self):
        super().__init__('circle_navigator')

        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.center_x = 0.0
        self.center_y = 0.0
        self.radius = 2.0
        self.angle = 0.0

        self.timer = self.create_timer(2.0, self.send_goal)

    def send_goal(self):
        if not self.client.wait_for_server(timeout_sec=1.0):
            self.get_logger().warn("Nav2 action server not ready")
            return

        goal_msg = NavigateToPose.Goal()

        pose = PoseStamped()
        pose.header.frame_id = 'odom'
        pose.header.stamp = self.get_clock().now().to_msg()

        pose.pose.position.x = self.center_x + self.radius * math.cos(self.angle)
        pose.pose.position.y = self.center_y + self.radius * math.sin(self.angle)
        pose.pose.orientation.w = 1.0

        goal_msg.pose = pose

        self.get_logger().info(f"Sending goal: {pose.pose.position.x:.2f}, {pose.pose.position.y:.2f}")

        self.client.send_goal_async(goal_msg)

        self.angle += 0.3


def main():
    rclpy.init()
    node = CircleNavigator()
    rclpy.spin(node)
    rclpy.shutdown()