#!/bin/bash
gnome-terminal --window -e 'bash -c "ros2 launch turtlebot4_navigation slam.launch.py"' \
--tab -e 'bash -c "sleep 5; ros2 launch turtlebot4_viz view_robot.launch.py"' \
--tab -e 'bash -c "sleep 5; ros2 run teleop_twist_keyboard teleop_twist_keyboard"' \


