#sudo systemctl restart turtlebot4.service
#ros2 launch turtlebot4_bringup lite.launch.py 
#gnome-terminal --window -e 'bash -c "ros2 launch turtlebot4_bringup lite.launch.py; exec bash"' \
gnome-terminal --window -e 'bash -c " source ~/training_code/install/setup.bash;ros2 launch turtlebot4_navigation localization.launch.py map:=/home/turtlebot4/training_code/src/turtlebot4_navigation/maps/map.yaml; exec bash"' \
--tab -e 'bash -c "sleep 8; source ~/training_code/install/setup.bash;ros2 launch turtlebot4_navigation nav2.launch.py; exec bash"' \
--tab -e 'bash -c "sleep 8; source ~/training_code/install/setup.bash;ros2 launch turtlebot4_viz view_robot.launch.py; exec bash"' \
--tab -e 'bash -c "sleep 8; source ~/training_code/install/setup.bash;ros2 run qr_track_alvar qr_track_alvar"' \

