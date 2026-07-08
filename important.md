sudo systemctl restart turtlebot4.service

<!-- Check feature -->
ros2 topic list
<!-- Cập nhật code -->
source /opt/ros/humble/setup.bash
colcon build
source ./install/setup.bash


<!-- Điều khiển TB4 -->
./grampping.sh 

<!-- x,y, theta data TB4 -->
ros2 topic echo /turtle1/pose

<!-- Activate odom and scan -->
ros2 topic echo /odom
ros2 topic echo /scan


<!-- run QR -->
ros2 run qr_track_alvar qr_track_alvar

<!--  -->
./go.sh

ros2 topic echo /waypoints <!-- Chạy ở đâu cũng được -->