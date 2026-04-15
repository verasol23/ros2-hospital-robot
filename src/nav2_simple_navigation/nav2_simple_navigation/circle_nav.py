import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped
import math

def main():
    rclpy.init()
    nav = BasicNavigator()

    # Wait for Nav2
    nav.waitUntilNav2Active(localizer='bt_navigator')

    radius = 4.0
    steps = 8 # Fewer steps is better for goToPose to avoid stuttering
    
    while True: # Loop to keep circling
        for i in range(steps):
            angle = (2 * math.pi * i) / steps
            
            goal_pose = PoseStamped()
            goal_pose.header.frame_id = 'odom'
            goal_pose.header.stamp = nav.get_clock().now().to_msg()
            
            goal_pose.pose.position.x = radius * math.cos(angle)
            goal_pose.pose.position.y = radius * math.sin(angle)
            
            # Simple orientation: face the next point
            yaw = angle + (math.pi / 2)
            goal_pose.pose.orientation.z = math.sin(yaw / 2)
            goal_pose.pose.orientation.w = math.cos(yaw / 2)

            # Use goToPose instead of followWaypoints
            nav.goToPose(goal_pose)

            # Wait until the robot reaches this specific point
            while not nav.isTaskComplete():
                pass 
                
    rclpy.shutdown()