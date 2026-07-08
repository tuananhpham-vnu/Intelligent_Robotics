# Import ROS2 related modules and message types
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseStamped
from sensor_msgs.msg import LaserScan, Imu
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy
from rclpy.duration import Duration
from rclpy.client import Client
import time
import math
import os
import pygame
from std_msgs.msg import String
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from threading import Lock


# 原生实现欧拉角转四元数，接口与tf_transformations完全一致
def quaternion_from_euler(roll, pitch, yaw):
    qx = math.sin(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) - math.cos(roll / 2) * math.sin(pitch / 2) * math.sin(yaw / 2)
    qy = math.cos(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2) + math.sin(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2)
    qz = math.cos(roll / 2) * math.cos(pitch / 2) * math.sin(yaw / 2) - math.sin(roll / 2) * math.sin(pitch / 2) * math.cos(yaw / 2)
    qw = math.cos(roll / 2) * math.cos(pitch / 2) * math.cos(yaw / 2) + math.sin(roll / 2) * math.sin(pitch / 2) * math.sin(yaw / 2)
    return [qx, qy, qz, qw]


class LidarImuDataCollector(Node):
    """
    ROS2 node for collecting LIDAR and IMU data
    """
    def __init__(self):
        super().__init__('data_collector')
        self._data_lock = Lock()
        self.qrcode_data = None
        self.qrcode_sub = self.create_subscription(
            String,
            '/qr_track_result',
            self.qrcode_callback,
            10
        )

    def qrcode_callback(self, msg):
        start = time.perf_counter()
        with self._data_lock:
            self.qrcode_data = msg.data
        latency = (time.perf_counter() - start) * 1000
        if latency > 50:
            self.get_logger().warn(f"Callback delay is too high: {latency:.2f}ms")


class PatrolNode(BasicNavigator):
    """
    ROS2 node for robot patrol
    """
    def __init__(self, node_name='Patrol_Node'):
        super().__init__(node_name)
        self.datas = LidarImuDataCollector()
        self.scan_received_flag = False
        self.amcl_pose_received = False
        self.init_subscribers()
        self.init_pose()
        self.wait_for_system_ready()

    def init_subscribers(self):
        try:
            self.amcl_pose_sub = self.create_subscription(
                PoseWithCovarianceStamped,
                '/amcl_pose',
                self.amcl_pose_callback,
                10
            )
            self.scan_sub = self.create_subscription(
                LaserScan,
                '/scan',
                self.scan_received,
                10
            )
        except Exception as e:
            self.get_logger().fatal(f"Subscription creation failed: {str(e)}")
            rclpy.shutdown()
            exit(1)

    def amcl_pose_callback(self, msg):
        self.amcl_pose_received = True
        self.get_logger().info("AMCL data has been received.")

    def scan_received(self, msg):
        self.scan_received_flag = True

    def wait_for_system_ready(self):
        self.get_logger().info("Waiting for system initialization...")
        executor = MultiThreadedExecutor(num_threads=2)
        executor.add_node(self)
        executor.add_node(self.datas)
        timeout = 60
        start_time = self.get_clock().now()

        while rclpy.ok():
            executor.spin_once(timeout_sec=0.1)
            if self.amcl_pose_received and self.scan_received_flag:
                self.get_logger().info("System initialization completed.")
                executor.shutdown()
                return
            if (self.get_clock().now() - start_time) > Duration(seconds=timeout):
                self.get_logger().error("Initialization timeout")
                executor.shutdown()
                rclpy.shutdown()
                exit(1)
        executor.shutdown()

    def init_pose(self):
        initial_pose = PoseStamped()
        initial_pose.header.frame_id = 'map'
        initial_pose.header.stamp = self.get_clock().now().to_msg()
        initial_pose.pose.position.x = 0.0
        initial_pose.pose.position.y = 0.0
        initial_pose.pose.orientation.w = 1.0
        self.setInitialPose(initial_pose)
        self.get_logger().info("Initial pose setting completed")
        self.waitUntilNav2Active()

    def run_voice(self, num):
        file_path = "/home/turtlebot4/training_code/voice"
        pygame.mixer.init()
        pygame.mixer.music.load(os.path.join(file_path, f"{num}.mp3"))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()

    def get_and_print_qrcode(self):
        executor = MultiThreadedExecutor(num_threads=2)
        executor.add_node(self.datas)
        st = time.perf_counter()
        try:
            while rclpy.ok():
                print(f"time:{time.perf_counter()-st}")
                executor.spin_once(timeout_sec=0.1)
                qrcode = self.datas.qrcode_data
                if qrcode is not None and qrcode != '':
                    print(f'QR code recognition result: {self.datas.qrcode_data}')
                    self.run_voice(int(qrcode))
                    return int(qrcode)
                elif (time.perf_counter() - st) > 3:
                    print("no qrcode ...")
                    return 0
        finally:
            executor.shutdown()

    def nav_to_point(self, goal):
        """
        Navigate to specified point
        """
        # Wait for navigation system to activate
        goal_pose = PoseStamped()

        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.get_clock().now().to_msg()

        # Set target position coordinates
        goal_pose.pose.position.x = goal[0]
        goal_pose.pose.position.y = goal[1]

        # Set target orientation if provided
        if len(goal) >= 3:
            yaw_deg = goal[2]
            yaw_rad = math.radians(yaw_deg)

            # Calculate quaternion from Euler angles
            q = quaternion_from_euler(0, 0, yaw_rad)

            goal_pose.pose.orientation = PoseStamped().pose.orientation
            goal_pose.pose.orientation.x = q[0]
            goal_pose.pose.orientation.y = q[1]
            goal_pose.pose.orientation.z = q[2]
            goal_pose.pose.orientation.w = q[3]
        else:
            # Default orientation
            goal_pose.pose.orientation.w = 1.0

        # Log navigation target information
        self.get_logger().info(f"Navigate to the destination: x={goal[0]:.2f}, y={goal[1]:.2f}, yaw={goal[2]:.0f}")

        # Send navigation goal
        self.goToPose(goal_pose)

        # Set navigation timeout
        timeout_sec = 60

        # Record start time
        start_time = self.get_clock().now().seconds_nanoseconds()[0]

        # Wait for navigation to complete or timeout
        while rclpy.ok() and not self.isTaskComplete():
            if (self.get_clock().now().seconds_nanoseconds()[0] - start_time) > timeout_sec * 1e9:
                # Cancel task and log warning
                self.cancelTask()
                self.get_logger().warn("Navigation timeout")
                break

        # Get navigation result
        result = self.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info("Navigation successful")
            return True

        # Log navigation failure information
        self.get_logger().error(f"Navigation failed: {result}")

        return False


    def load_navigation_points(self, csv_file_path):
        """
        Load navigation points from CSV file
        """
        goal_list = []
        try:
            with open(csv_file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        # Parse coordinates from CSV file
                        coords = list(map(float, line.strip('[]').split(',')))
                        goal_list.append(coords)
            return goal_list
        except Exception as e:
            # Log error if loading fails
            self.get_logger().error(f"Failed to load the navigation points: {str(e)}")

        return []

    def plan(self, qr_result, wirefram_points):
        """
        Determine the next navigation point based on the QR code recognition result
        """
        if qr_result == 1:
            self.nav_to_point(wirefram_points[0])
            self.run_voice("1_1")
            time.sleep(3)
        elif qr_result == 2:
            self.nav_to_point(wirefram_points[1])
            self.run_voice("2_2")
            time.sleep(3)
        elif qr_result == 3:
            self.nav_to_point(wirefram_points[2])
            self.run_voice("3_3")
            time.sleep(3)
        else:
            print("no valid qr code,go to next points")


def main():
    rclpy.init()
    patrol = PatrolNode()
    wirefram_points = patrol.load_navigation_points(
        csv_file_path='/home/turtlebot4/training_code/points/wirefram_points.csv')
    qr_code_points = patrol.load_navigation_points(
        csv_file_path='/home/turtlebot4/training_code/points/qr_code_points.csv')

    for i in range(len(qr_code_points)):
        patrol.nav_to_point(qr_code_points[i])
        time.sleep(1)
        qr_result = patrol.get_and_print_qrcode()
        time.sleep(3)
        patrol.plan(int(qr_result), wirefram_points)
    patrol.nav_to_point(wirefram_points[3])
    patrol.run_voice("end")
    print("Goal end")
    rclpy.shutdown()


if __name__ == '__main__':
    main()