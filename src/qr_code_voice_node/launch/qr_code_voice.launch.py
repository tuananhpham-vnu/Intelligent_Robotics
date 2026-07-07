from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='cmd_vel_publisher',
            executable='cmd_vel_publisher',
            name='cmd_vel_publisher',
            output='screen',
        ),
        Node(
            package='qr_code_voice_node',
            executable='qr_code_voice_node',
            name='qr_code_voice_node',
            output='screen',
            parameters=[{
                'voice_dir': '/home/turtlebot4/training_code/voice',
            }],
        ),
        Node(
            package='qr_track_alvar',
            executable='qr_track_alvar',
            name='qr_camera_tracker',
            output='screen',
            remappings=[
                ('/qr_track_result', '/qr_track_result'),
            ],
        ),
    ])
