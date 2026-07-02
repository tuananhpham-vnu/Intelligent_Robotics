"""Launch the trajectory controller together with RViz path publishing."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='path_node',
            executable='path_node',
            name='live_path_visualizer',
            parameters=[{
                'odom_topic': '/odom',
                'path_topic': '/robot_path',
                'frame_id': 'odom',
            }],
            output='screen',
        ),
        Node(
            package='pattern_trajectory',
            executable='pattern_trajectory',
            name='pattern_trajectory',
            parameters=[{
                'patterns': ['square', 'infinity', 'star'],
                'side_length': 1.0,
                'circle_radius': 0.5,
                'linear_speed': 0.15,
                'angular_speed': 0.45,
            }],
            output='screen',
        ),
    ])
