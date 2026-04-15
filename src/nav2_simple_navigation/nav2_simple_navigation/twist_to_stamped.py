import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped


class TwistToStamped(Node):
    def __init__(self):
        super().__init__('twist_to_stamped')

        self.declare_parameter('input_topic', '/cmd_vel_nav_smooth')
        self.declare_parameter('output_topic', '/mobile_base_controller/reference')
        self.declare_parameter('frame_id', 'base_link')

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value
        self.frame_id = self.get_parameter('frame_id').value

        self.sub = self.create_subscription(
            Twist,
            input_topic,
            self.cmd_callback,
            10
        )

        self.pub = self.create_publisher(
            TwistStamped,
            output_topic,
            10
        )

    def cmd_callback(self, msg: Twist):
        stamped = TwistStamped()
        stamped.header.stamp = self.get_clock().now().to_msg()
        stamped.header.frame_id = self.frame_id
        stamped.twist = msg
        self.pub.publish(stamped)


def main(args=None):
    rclpy.init(args=args)
    node = TwistToStamped()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()