from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'run_cmd_vel',
            default_value='false',
            description='Run cmd_vel_publisher for Task D',
        ),
        DeclareLaunchArgument(
            'voice_dir',
            default_value='/home/turtlebot4/training_code/voice',
            description='Directory containing 1.mp3, 2.mp3, and 3.mp3',
        ),
        Node(
            package='cmd_vel_publisher',
            executable='cmd_vel_publisher',
            name='cmd_vel_publisher',
            output='screen',
            condition=IfCondition(LaunchConfiguration('run_cmd_vel')),
        ),
        Node(
            package='qr_code_voice_node',
            executable='qr_code_voice_node',
            name='qr_code_voice_node',
            output='screen',
            parameters=[{
                'voice_dir': LaunchConfiguration('voice_dir'),
                'auto_play_on_scan': True,
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
