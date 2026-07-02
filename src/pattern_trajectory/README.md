# Experiment 4: complex pattern trajectory

This ROS 2 package uses odometry feedback to draw, in order:

1. a 1 m square;
2. an infinity symbol made from two tangent circles of radius 0.5 m;
3. an optional regular five-point star.

The existing `path_node` package publishes the measured odometry trail as
`nav_msgs/Path` on `/robot_path` for RViz.

## Build and run

```bash
cd ~/your_workspace
colcon build --packages-select path_node pattern_trajectory
source install/setup.bash
ros2 launch pattern_trajectory experiment4.launch.py
```

Start the robot and SLAM/mapping launch before the final command. In RViz, set
Fixed Frame to `odom` and add a **Path** display with topic `/robot_path`.

Run only one shape while tuning:

```bash
ros2 run pattern_trajectory pattern_trajectory --ros-args \
  -p patterns:="['square']" -p linear_speed:=0.10
```

Use a clear area at low speed first. Tune `distance_tolerance`,
`angle_tolerance`, `linear_speed`, and `angular_speed` if corners or closures
show accumulated odometry error.
