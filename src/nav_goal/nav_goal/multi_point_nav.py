"""ROS 2 patrol node using Nav2, QR-code results, and audio prompts."""

import math
import os
import time
from threading import Lock

import pygame
import rclpy
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.duration import Duration
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String


BASE_DIR = "/home/turtlebot4/training_code"


def quaternion_from_euler(roll, pitch, yaw):
    """Convert Euler angles to a quaternion [x, y, z, w]."""
    qx = (
        math.sin(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2)
        - math.cos(roll / 2) * math.sin(pitch / 2) * math.sin(yaw / 2)
    )
    qy = (
        math.cos(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2)
        + math.sin(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2)
    )
    qz = (
        math.cos(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2)
        - math.sin(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2)
    )
    qw = (
        math.cos(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2)
        + math.sin(roll / 2) * math.sin(pitch / 2) * math.sin(yaw / 2)
    )
    return [qx, qy, qz, qw]


class QrDataCollector(Node):
    """Collect QR-code recognition results."""

    def __init__(self):
        super().__init__("data_collector")
        self._data_lock = Lock()
        self.qrcode_data = None
        self.qrcode_sub = self.create_subscription(
            String, "qr_track_result", self.qrcode_callback, 10
        )

    def qrcode_callback(self, msg):
        start = time.perf_counter()
        with self._data_lock:
            self.qrcode_data = msg.data
        latency = (time.perf_counter() - start) * 1000
        if latency > 50:
            self.get_logger().warning(
                f"Callback delay is too high: {latency:.2f} ms"
            )

    def get_qrcode_data(self):
        with self._data_lock:
            return self.qrcode_data

    def clear_qrcode_data(self):
        with self._data_lock:
            self.qrcode_data = None


class PatrolNode(BasicNavigator):
    """Navigate through patrol points and react to QR-code results."""

    def __init__(self, node_name="patrol_node"):
        super().__init__(node_name=node_name)
        self.datas = QrDataCollector()
        self.scan_received_flag = False
        self.amcl_pose_received = False
        self.init_subscribers()
        self.init_pose()
        self.wait_for_system_ready()

    def init_subscribers(self):
        self.amcl_pose_sub = self.create_subscription(
            PoseWithCovarianceStamped, "amcl_pose", self.amcl_pose_callback, 10
        )
        self.scan_sub = self.create_subscription(
            LaserScan, "scan", self.scan_received, 10
        )

    def amcl_pose_callback(self, _msg):
        if not self.amcl_pose_received:
            self.get_logger().info("AMCL data has been received.")
        self.amcl_pose_received = True

    def scan_received(self, _msg):
        self.scan_received_flag = True

    def wait_for_system_ready(self):
        self.get_logger().info("Waiting for sensor initialization...")
        executor = MultiThreadedExecutor(num_threads=2)
        executor.add_node(self)
        executor.add_node(self.datas)
        start_time = self.get_clock().now()

        try:
            while rclpy.ok():
                executor.spin_once(timeout_sec=0.1)
                if self.amcl_pose_received and self.scan_received_flag:
                    self.get_logger().info("System initialization completed.")
                    return
                if self.get_clock().now() - start_time > Duration(seconds=60):
                    raise TimeoutError("Sensor initialization timed out after 60 seconds")
        finally:
            executor.remove_node(self.datas)
            executor.remove_node(self)
            executor.shutdown()

    def init_pose(self):
        initial_pose = PoseStamped()
        initial_pose.header.frame_id = "map"
        initial_pose.header.stamp = self.get_clock().now().to_msg()
        initial_pose.pose.position.x = 0.0
        initial_pose.pose.position.y = 0.0
        initial_pose.pose.orientation.w = 1.0
        self.setInitialPose(initial_pose)
        self.get_logger().info("Initial pose has been set.")
        self.waitUntilNav2Active()

    def run_voice(self, name):
        file_path = os.path.join(BASE_DIR, "voice", f"{name}.mp3")
        if not os.path.isfile(file_path):
            self.get_logger().error(f"Audio file not found: {file_path}")
            return

        pygame.mixer.init()
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        finally:
            pygame.mixer.quit()

    def get_and_print_qrcode(self):
        executor = MultiThreadedExecutor(num_threads=1)
        executor.add_node(self.datas)
        self.datas.clear_qrcode_data()
        start = time.perf_counter()

        try:
            while rclpy.ok() and time.perf_counter() - start <= 3:
                executor.spin_once(timeout_sec=0.1)
                qrcode = self.datas.get_qrcode_data()
                if qrcode:
                    self.get_logger().info(f"QR-code recognition result: {qrcode}")
                    try:
                        result = int(qrcode)
                    except ValueError:
                        self.get_logger().warning(f"Invalid QR-code value: {qrcode!r}")
                        return 0
                    self.run_voice(result)
                    return result

            self.get_logger().warning("No QR code detected within 3 seconds.")
            return 0
        finally:
            executor.remove_node(self.datas)
            executor.shutdown()

    def nav_to_point(self, goal):
        """Navigate to [x, y] or [x, y, yaw_degrees]."""
        if len(goal) < 2:
            self.get_logger().error(f"Invalid navigation point: {goal}")
            return False

        goal_pose = PoseStamped()
        goal_pose.header.frame_id = "map"
        goal_pose.header.stamp = self.get_clock().now().to_msg()
        goal_pose.pose.position.x = goal[0]
        goal_pose.pose.position.y = goal[1]

        yaw_deg = goal[2] if len(goal) >= 3 else 0.0
        qx, qy, qz, qw = quaternion_from_euler(0.0, 0.0, math.radians(yaw_deg))
        goal_pose.pose.orientation.x = qx
        goal_pose.pose.orientation.y = qy
        goal_pose.pose.orientation.z = qz
        goal_pose.pose.orientation.w = qw

        self.get_logger().info(
            f"Navigating to x={goal[0]:.2f}, y={goal[1]:.2f}, yaw={yaw_deg:.0f}"
        )
        self.goToPose(goal_pose)
        start_time = self.get_clock().now()

        while rclpy.ok() and not self.isTaskComplete():
            if self.get_clock().now() - start_time > Duration(seconds=60):
                self.cancelTask()
                self.get_logger().warning("Navigation timed out after 60 seconds.")
                break
            time.sleep(0.1)

        result = self.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info("Navigation succeeded.")
            return True

        self.get_logger().error(f"Navigation failed: {result}")
        return False

    def load_navigation_points(self, csv_file_path):
        """Load navigation points from a CSV-like file."""
        goal_list = []
        try:
            with open(csv_file_path, "r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    coords = [value.strip() for value in line.strip("[]").split(",")]
                    try:
                        point = list(map(float, coords))
                    except ValueError:
                        self.get_logger().warning(
                            f"Skipping invalid point on line {line_number}: {line}"
                        )
                        continue
                    if len(point) < 2:
                        self.get_logger().warning(
                            f"Skipping incomplete point on line {line_number}: {line}"
                        )
                        continue
                    goal_list.append(point)
        except OSError as exc:
            self.get_logger().error(
                f"Failed to load navigation points from {csv_file_path}: {exc}"
            )
        return goal_list

    def plan(self, qr_result, wireframe_points):
        """Choose the next destination based on a QR-code result."""
        destinations = {1: (0, "1_1"), 2: (1, "2_2"), 3: (2, "3_3")}
        destination = destinations.get(qr_result)
        if destination is None:
            self.get_logger().warning("No valid QR code; continuing patrol.")
            return

        point_index, audio_name = destination
        if point_index >= len(wireframe_points):
            self.get_logger().error(f"Missing wireframe point at index {point_index}")
            return

        if self.nav_to_point(wireframe_points[point_index]):
            self.run_voice(audio_name)
            time.sleep(3)


def main(args=None):
    rclpy.init(args=args)
    patrol = None
    try:
        patrol = PatrolNode()
        points_dir = os.path.join(BASE_DIR, "points")
        wireframe_points = patrol.load_navigation_points(
            os.path.join(points_dir, "wirefram_points.csv")
        )
        qr_code_points = patrol.load_navigation_points(
            os.path.join(points_dir, "qr_code_points.csv")
        )

        if len(wireframe_points) < 4 or not qr_code_points:
            patrol.get_logger().error("Navigation-point files are missing or incomplete.")
            return

        for point in qr_code_points:
            if patrol.nav_to_point(point):
                time.sleep(1)
                qr_result = patrol.get_and_print_qrcode()
                time.sleep(3)
                patrol.plan(qr_result, wireframe_points)

        patrol.nav_to_point(wireframe_points[3])
        patrol.run_voice("end")
        patrol.get_logger().info("Patrol complete.")
    except (KeyboardInterrupt, TimeoutError) as exc:
        if patrol is not None:
            patrol.get_logger().warning(str(exc) or "Patrol interrupted.")
    finally:
        if patrol is not None:
            patrol.datas.destroy_node()
            patrol.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
