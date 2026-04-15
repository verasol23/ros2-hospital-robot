from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    nav_pkg = get_package_share_directory('nav2_simple_navigation')

    nav2_config = os.path.join(nav_pkg, 'config', 'nav2_params.yaml')
    map_yaml_file = os.path.join(nav_pkg, 'maps', 'my_map.yaml')
    rviz_config_file = os.path.join(nav_pkg, 'rviz', 'test2.rviz')

    return LaunchDescription([
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_file],
            parameters=[{'use_sim_time': True}]
        ),

        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[nav2_config, {'yaml_filename': map_yaml_file}]
        ),

        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[nav2_config],
            remappings=[('/scan', '/scan_front_raw')]
        ),

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
    ])