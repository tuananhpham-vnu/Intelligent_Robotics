#!/usr/bin/env python3
"""Navigate through waypoints, scan QR codes, and play voice prompts."""

import csv
import math
from pathlib import Path
import time

from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy
from std_msgs.msg import String


def quaternion_from_yaw(yaw):
    """Return z and w components of a planar quaternion."""
    return math.sin(yaw / 2.0), math.cos(yaw / 2.0)


class PatrolMission(BasicNavigator):
    """Orchestrate Nav2, QR reception, and local MP3 playback."""

    def __init__(self):
        super().__init__('patrol_mission')
        share = Path(get_package_share_directory('qr_track_alvar'))
        self.declare_parameter('waypoints_file', str(share / 'config' / 'coordinates.csv'))
        # Reuse the workspace-level voice/ directory; do not duplicate MP3 files
        # inside this ROS package. An absolute path can be supplied at launch.
        self.declare_parameter('audio_directory', str(Path.cwd() / 'voice'))
        self.declare_parameter('qr_topic', '/qr_track_result')
        self.declare_parameter('qr_timeout', 10.0)
        self.declare_parameter('navigation_timeout', 120.0)
        self.declare_parameter('initial_x', 0.0)
        self.declare_parameter('initial_y', 0.0)
        self.declare_parameter('initial_yaw_deg', 0.0)

        self.waypoints_file = Path(str(self.get_parameter('waypoints_file').value))
        self.audio_directory = Path(str(self.get_parameter('audio_directory').value))
        self.qr_timeout = float(self.get_parameter('qr_timeout').value)
        self.navigation_timeout = float(
            self.get_parameter('navigation_timeout').value)
        qr_topic = str(self.get_parameter('qr_topic').value)
        self.latest_qr = None
        self.qr_sequence = 0
        self.create_subscription(String, qr_topic, self.qr_callback, 10)

    def qr_callback(self, message):
        payload = message.data.strip()
        if payload:
            self.latest_qr = payload
            self.qr_sequence += 1

    def make_pose(self, x, y, yaw_deg):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.orientation.z, pose.pose.orientation.w = quaternion_from_yaw(
            math.radians(yaw_deg))
        return pose

    def load_waypoints(self):
        points = []
        with self.waypoints_file.open(newline='', encoding='utf-8') as stream:
            for row_number, row in enumerate(csv.reader(stream), start=1):
                values = [item.strip().strip('[]') for item in row]
                values = [item for item in values if item]
                if not values:
                    continue
                if len(values) < 2:
                    raise ValueError(f'Invalid waypoint at line {row_number}')
                x, y = float(values[0]), float(values[1])
                yaw = float(values[2]) if len(values) >= 3 else 0.0
                points.append((x, y, yaw))
        return points

    def play_voice(self, name):
        audio_file = self.audio_directory / f'{name}.mp3'
        if not audio_file.is_file():
            self.get_logger().warning(f'Audio file not found: {audio_file}')
            return
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(str(audio_file))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() and rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.05)
        except Exception as error:
            self.get_logger().error(f'Cannot play {audio_file.name}: {error}')

    def wait_for_new_qr(self):
        start_sequence = self.qr_sequence
        deadline = time.monotonic() + self.qr_timeout
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)
            if self.qr_sequence > start_sequence:
                return self.latest_qr
        return None

    def navigate_to(self, point):
        self.goToPose(self.make_pose(*point))
        deadline = time.monotonic() + self.navigation_timeout
        while rclpy.ok() and not self.isTaskComplete():
            if time.monotonic() >= deadline:
                self.cancelTask()
                self.get_logger().error('Navigation timed out')
                return False
        return self.getResult() == TaskResult.SUCCEEDED

    def run(self):
        waypoints = self.load_waypoints()
        if not waypoints:
            raise RuntimeError(f'No waypoints in {self.waypoints_file}')

        initial = self.make_pose(
            float(self.get_parameter('initial_x').value),
            float(self.get_parameter('initial_y').value),
            float(self.get_parameter('initial_yaw_deg').value))
        self.setInitialPose(initial)
        self.get_logger().info('Waiting for Nav2 to become active...')
        self.waitUntilNav2Active()

        for index, point in enumerate(waypoints, start=1):
            self.get_logger().info(
                f'Goal {index}/{len(waypoints)}: x={point[0]:.2f}, '
                f'y={point[1]:.2f}, yaw={point[2]:.1f} deg')
            if not self.navigate_to(point):
                self.get_logger().error(f'Goal {index} failed; mission stopped')
                return False

            self.get_logger().info('Arrived. Waiting for a QR code...')
            payload = self.wait_for_new_qr()
            if payload is None:
                self.get_logger().warning('No QR code detected; continuing')
                continue
            self.get_logger().info(f'QR payload: {payload}')
            self.play_voice(payload)

        self.play_voice('end')
        self.get_logger().info('Patrol mission completed')
        return True


def main(args=None):
    rclpy.init(args=args)
    node = PatrolMission()
    try:
        node.run()
    except (KeyboardInterrupt, RuntimeError, OSError, ValueError) as error:
        node.get_logger().error(str(error))
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
