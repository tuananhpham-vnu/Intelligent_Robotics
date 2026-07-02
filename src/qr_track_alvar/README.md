# Navigation + QR + voice mission

This package provides two ROS 2 nodes:

- `qr_scanner`: reads compressed OAK-D images and publishes decoded text on
  `/qr_track_result`;
- `patrol_mission`: visits every pose in `config/coordinates.csv`, waits for a
  fresh QR result, plays `<QR payload>.mp3`, then plays `end.mp3`.

Audio is read directly from the workspace-level `voice/` directory; the MP3
files are not copied into this package.

Build and run after the robot bringup, localization, and Nav2 are active:

```bash
cd ~/training_code
colcon build --packages-select qr_track_alvar
source install/setup.bash
ros2 launch qr_track_alvar qr_voice_patrol.launch.py
```

Test each function separately:

```bash
ros2 run qr_track_alvar qr_scanner
ros2 topic echo /qr_track_result

ros2 run qr_track_alvar patrol_mission
```

Useful overrides:

```bash
ros2 launch qr_track_alvar qr_voice_patrol.launch.py \
  waypoints_file:=/absolute/path/coordinates.csv \
  audio_directory:=/absolute/path/to/workspace/voice
```

The default camera topic is `/oakd/rgb/preview/image_raw/compressed`. Override
the `camera_topic` parameter if `ros2 topic list` reports a different name.
