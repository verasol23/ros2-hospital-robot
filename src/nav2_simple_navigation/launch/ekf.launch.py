from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    # Get path to config file
    pkg_share = get_package_share_directory('nav2_simple_navigation')
    ekf_config = os.path.join(pkg_share, 'config', 'ekf.yaml')

    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config],
        remappings=[
            # optional (only if needed)
            # ('/odometry/filtered', '/odometry/filtered')
        ]
    )

    return LaunchDescription([
        ekf_node
    ])