"""Launch QR recognition and the navigation/voice mission."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'camera_topic',
            default_value='/oakd/rgb/preview/image_raw/compressed'),
        DeclareLaunchArgument(
            'waypoints_file',
            default_value=PathJoinSubstitution([
                FindPackageShare('qr_track_alvar'), 'config', 'coordinates.csv'
            ])),
        DeclareLaunchArgument(
            'audio_directory',
            default_value='voice'),
        Node(
            package='qr_track_alvar',
            executable='qr_scanner',
            name='qr_scanner',
            parameters=[{
                'show_preview': False,
                'camera_topic': LaunchConfiguration('camera_topic'),
            }],
            output='screen',
        ),
        Node(
            package='qr_track_alvar',
            executable='patrol_mission',
            name='patrol_mission',
            parameters=[{
                'qr_timeout': 10.0,
                'navigation_timeout': 120.0,
                'waypoints_file': LaunchConfiguration('waypoints_file'),
                'audio_directory': LaunchConfiguration('audio_directory'),
            }],
            output='screen',
        ),
    ])
