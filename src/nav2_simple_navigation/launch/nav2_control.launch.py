from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Package chứa launch/config/map của Nav2
    nav_pkg = get_package_share_directory('nav2_simple_navigation')

    # Package chứa robot-specific assets (nếu có)
    robot_pkg = get_package_share_directory('robot_omni')

    # ==== File của Nav2 ====
    nav2_config = os.path.join(nav_pkg, 'config', 'nav2_params.yaml')
    rviz_config_file = os.path.join(nav_pkg, 'rviz', 'test.rviz')
    map_yaml_file = os.path.join(nav_pkg, 'maps', 'my_map.yaml')

    # ==== File riêng của robot ====
    bt_xml_file = os.path.join(robot_pkg, 'behavior_trees', 'smart_recovery_bt.xml')

    return LaunchDescription([
        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_file],
            parameters=[{'use_sim_time': True}]
        ),

        # Map Server
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[nav2_config, {'yaml_filename': map_yaml_file}]
        ),

        # AMCL
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[nav2_config],
            remappings=[('/scan', '/scan_front_raw')]
        ),

        # Planner Server
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[nav2_config]
        ),

        # Controller Server
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[nav2_config],
            remappings=[('/cmd_vel', '/cmd_vel_nav')]
        ),

        # Smoother Server
        Node(
            package='nav2_smoother',
            executable='smoother_server',
            name='smoother_server',
            output='screen',
            parameters=[nav2_config]
        ),

        # Behavior Server
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[nav2_config],
            remappings=[('/cmd_vel', '/cmd_vel_nav')]
        ),

        # BT Navigator
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[nav2_config, {'default_nav_to_pose_bt_xml': bt_xml_file}]
        ),

        # Waypoint Follower
        Node(
            package='nav2_waypoint_follower',
            executable='waypoint_follower',
            name='waypoint_follower',
            output='screen',
            parameters=[nav2_config]
        ),

        # Velocity Smoother
        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            name='velocity_smoother',
            output='screen',
            parameters=[nav2_config],
            remappings=[
                ('/cmd_vel', '/cmd_vel_nav'),
                ('/cmd_vel_smoothed', '/mobile_base_controller/reference')
            ]
        ),

        # Lifecycle Manager cho localization
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'autostart': True,
                'node_names': ['map_server', 'amcl']
            }]
        ),

        # Lifecycle Manager cho navigation
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

        # GUI riêng: chỉ giữ nếu robot_omni thật sự có executable này
        # Node(
        #     package='robot_omni',
        #     executable='waypoint_gui.py',
        #     name='waypoint_gui',
        #     output='screen'
        # )
    ])