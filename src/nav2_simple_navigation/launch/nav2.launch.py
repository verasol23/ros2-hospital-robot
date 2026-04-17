from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    nav_pkg = get_package_share_directory('nav2_simple_navigation')
    robot_pkg = get_package_share_directory('robot_omni')

    nav2_config = os.path.join(nav_pkg, 'config', 'nav2_params.yaml')
    bt_xml_file = os.path.join(nav_pkg, 'behavior_tree', 'test.xml')
    filter_config = os.path.join(robot_pkg, 'config', 'laser_filters.yaml')
    keepout_mask_yaml = os.path.join(nav_pkg, 'maps', 'my_map_keepout_mask.yaml')

    return LaunchDescription([

        Node(
            package='laser_filters',
            executable='scan_to_scan_filter_chain',
            name='scan_front_filter',
            output='screen',
            parameters=[filter_config, {'use_sim_time': True}],
            remappings=[
                ('scan', '/scan_front_raw'),
                ('scan_filtered', '/scan_front_filtered')
            ]
        ),

        Node(
            package='laser_filters',
            executable='scan_to_scan_filter_chain',
            name='scan_rear_filter',
            output='screen',
            parameters=[filter_config, {'use_sim_time': True}],
            remappings=[
                ('scan', '/scan_rear_raw'),
                ('scan_filtered', '/scan_rear_filtered')
            ]
        ),

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
                ('/cmd_vel_smoothed', '/cmd_vel_nav_smooth')
            ]
        ),

        Node(
            package='nav2_collision_monitor',
            executable='collision_monitor',
            name='collision_monitor',
            output='screen',
            parameters=[nav2_config]
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
            package='nav2_map_server',
            executable='map_server',
            name='keepout_filter_mask_server',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'yaml_filename': keepout_mask_yaml,
                'topic_name': '/keepout_filter_mask',
                'frame_id': 'map'
            }]
        ),

        Node(
            package='nav2_map_server',
            executable='costmap_filter_info_server',
            name='costmap_filter_info_server',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'filter_info_topic': '/costmap_filter_info',
                'type': 0,
                'mask_topic': '/keepout_filter_mask',
                'base': 0.0,
                'multiplier': 1.0
            }]
        ),

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_keepout_zone',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'autostart': True,
                'node_names': [
                    'keepout_filter_mask_server',
                    'costmap_filter_info_server'
                ]
            }]
        ),    

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
                    'velocity_smoother',
                    'collision_monitor'
                ]
            }]
        ),
    ])