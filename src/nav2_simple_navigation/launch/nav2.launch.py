from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    nav_pkg = get_package_share_directory('nav2_simple_navigation')
    robot_pkg = get_package_share_directory('robot_omni')

    nav2_config = os.path.join(nav_pkg, 'config', 'nav2_params.yaml')
    bt_xml_file = os.path.join(nav_pkg, 'behavior_tree', 'smart.xml')

    return LaunchDescription([
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[nav2_config]
        ),

        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[nav2_config],
            remappings=[('/cmd_vel', '/cmd_vel_nav_raw')]
        ),

        Node(
            package='nav2_smoother',
            executable='smoother_server',
            name='smoother_server',
            output='screen',
            parameters=[nav2_config]
        ),

        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[nav2_config],
            remappings=[('/cmd_vel', '/cmd_vel_nav_raw')]
        ),

        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            #parameters=[nav2_config]
            parameters=[nav2_config, {'default_nav_to_pose_bt_xml': bt_xml_file}]
        ),

        Node(
            package='nav2_waypoint_follower',
            executable='waypoint_follower',
            name='waypoint_follower',
            output='screen',
            parameters=[nav2_config]
        ),

        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            name='velocity_smoother',
            output='screen',
            parameters=[nav2_config],
            remappings=[
                ('/cmd_vel', '/cmd_vel_nav_raw'),
                ('/cmd_vel_smoothed', '/mobile_base_controller/reference')
            ]
        ),
        # Node(
        #     package='nav2_simple_navigation',
        #     executable='twist_to_stamped',
        #     name='twist_to_stamped',
        #     output='screen',
        #     parameters=[{
        #         'input_topic': '/cmd_vel_nav_smooth',
        #         'output_topic': '/mobile_base_controller/reference',
        #         'frame_id': 'base_link'
        #     }]
        # ),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'autostart': True,
                'node_names': [
                    'planner_server',
                    'controller_server',
                    'smoother_server',
                    'behavior_server',
                    'bt_navigator',
                    'waypoint_follower',
                    'velocity_smoother'
                ]
            }]
        ),
    ])