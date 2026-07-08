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
from tf_transformations import quaternion_from_euler
from std_msgs.msg import String
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from threading import Lock

class LidarImuDataCollector(Node):
    """
    ROS2 node for collecting LIDAR and IMU data
    """
    def __init__(self):
        super().__init__('data_collector')
        # Data lock to ensure thread safety
        self._data_lock = Lock()
        # Store QR code data
        self.qrcode_data = None
        # Create QR code subscriber
        self.qrcode_sub = self.create_subscription(
            String,
            '/qr_track_result',
            self.qrcode_callback,
            10
        )

    def qrcode_callback(self, msg):
        """
        Callback function for QR code messages
        """
        # Record the start time of the callback
        start = time.perf_counter()
        # Use lock to ensure data consistency
        with self._data_lock:
            self.qrcode_data = msg.data
        # Calculate callback latency
        latency = (time.perf_counter() - start) * 1000
        # Warn if latency is too high
        if latency > 50:
            self.get_logger().warn(f"Callback delay is too high: {latency:.2f}ms")


class PatrolNode(BasicNavigator):
    """
    ROS2 node for robot patrol
    """
    def __init__(self, node_name='Patrol_Node'):
        super().__init__(node_name)
        # Initialize data collector
        self.datas = LidarImuDataCollector()
        # Laser scan data reception flag
        self.scan_received_flag = False
        # AMCL pose data reception flag
        self.amcl_pose_received = False
        # Initialize subscribers
        self.init_subscribers()
        # Initialize robot's initial pose
        self.init_pose()
        # Wait for the system to be ready
        self.wait_for_system_ready()

    def init_subscribers(self):
        """Securely create subscribers"""
        try:
            # Create AMCL pose subscriber
            self.amcl_pose_sub = self.create_subscription(
                PoseWithCovarianceStamped,
                '/amcl_pose',
                self.amcl_pose_callback,
                10
            )
            # Create laser scan subscriber
            self.scan_sub = self.create_subscription(
                LaserScan,
                '/scan',
                self.scan_received,
                10
            )
        except Exception as e:
            # Log fatal error and exit if subscriber creation fails
            self.get_logger().fatal(f"Subscription creation failed: {str(e)}")
            rclpy.shutdown()
            exit(1)

    def amcl_pose_callback(self, msg):
        """Process PoseWithCovarianceStamped message"""
        self.amcl_pose_received = True
        self.get_logger().info("AMCL data has been received.")

    def scan_received(self, msg):
        """Callback for laser scan data reception"""
        self.scan_received_flag = True

    def wait_for_system_ready(self):
        """Wait for system initialization to complete"""
        self.get_logger().info("Waiting for system initialization...")
        # Create multi-threaded executor
        executor = MultiThreadedExecutor(num_threads=2)
        # Add current node and data collector node
        executor.add_node(self)
        executor.add_node(self.datas)
        # Set timeout
        timeout = 60
        # Record start time
        start_time = self.get_clock().now().seconds_nanoseconds()[0]

        while rclpy.ok():
            # Spin executor once to process one callback
            executor.spin_once(timeout_sec=0.1)
            # Check if all necessary data has been received
            if self.amcl_pose_received and self.scan_received_flag:
                self.get_logger().info("System initialization completed.")
                # Shutdown executor
                executor.shutdown()
                return
            # Check if timeout
            if (self.get_clock().now().seconds_nanoseconds()[0] - start_time) > timeout * 1e9:
                self.get_logger().error("Initialization timeout")
                executor.shutdown()
                rclpy.shutdown()
                exit(1)
        # Shutdown executor
        executor.shutdown()

    def init_pose(self):
        """Initialize robot's pose in the map"""
        initial_pose = PoseStamped()
        initial_pose.header.frame_id = 'map'
        initial_pose.header.stamp = self.get_clock().now().to_msg()
        # Set initial position coordinates
        initial_pose.pose.position.x = 0.0
        initial_pose.pose.position.y = 0.0
        # Set initial orientation
        initial_pose.pose.orientation.w = 1.0
        # Set initial pose
        self.setInitialPose(initial_pose)
        self.get_logger().info("Initial pose setting completed")
        # Wait for navigation system to activate
        self.waitUntilNav2Active()

    def run_voice(self,num):
        """
        voice broadcast function
        """
        file_path = "/home/turtlebot4/test/voice"

        pygame.mixer.init()
        pygame.mixer.music.load(os.path.join(file_path,f"{num}.mp3"))
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()

    def get_and_print_qrcode(self):
        """Get and print QR code information, and perform voice broadcast"""
        # Create multi-threaded executor
        executor = MultiThreadedExecutor(num_threads=2)
        # Add data collector node
        executor.add_node(self.datas)
        # Record start time
        st = time.perf_counter()
        try:
            while rclpy.ok():
                print(f"time:{time.perf_counter()-st}")
                # Spin executor once
                executor.spin_once(timeout_sec=0.1)
                # Get QR code data
                qrcode = self.datas.qrcode_data
                # Check if there is valid QR code data
                if qrcode is not None and qrcode != '':
                    print(f'QR code recognition result: {self.datas.qrcode_data}')
                    # Call voice broadcast function
                    self.run_voice(int(qrcode))
                    return int(qrcode)
                # Check if timeout
                elif (time.perf_counter()-st) > 3:
                    print("no qrcode ...")
                    return 0
        finally:
            # Shutdown executor
            executor.shutdown()

    def nav_to_point(self, goal):
        """
        Navigate to specified point
        goal = [x, y] hoặc [x, y, yaw_deg]
        """

        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.get_clock().now().to_msg()

        goal_pose.pose.position.x = float(goal[0])
        goal_pose.pose.position.y = float(goal[1])

        if len(goal) >= 3:
            yaw_deg = float(goal[2])
            yaw_rad = math.radians(yaw_deg)

            q = quaternion_from_euler(0, 0, yaw_rad)

            goal_pose.pose.orientation.x = q[0]
            goal_pose.pose.orientation.y = q[1]
            goal_pose.pose.orientation.z = q[2]
            goal_pose.pose.orientation.w = q[3]
        else:
            goal_pose.pose.orientation.w = 1.0

        if len(goal) >= 3:
            self.get_logger().info(
                f"Navigate to the destination: x={goal[0]:.2f}, "
                f"y={goal[1]:.2f}, yaw={goal[2]:.0f}°"
            )
        else:
            self.get_logger().info(
                f"Navigate to the destination: x={goal[0]:.2f}, "
                f"y={goal[1]:.2f}"
            )

        self.goToPose(goal_pose)

        timeout_sec = 60
        start_time = self.get_clock().now().nanoseconds

        while rclpy.ok() and not self.isTaskComplete():
            current_time = self.get_clock().now().nanoseconds

            if current_time - start_time > timeout_sec * 1e9:
                self.cancelTask()
                self.get_logger().warn("Navigation timeout")
                break

        result = self.getResult()

        if result == TaskResult.SUCCEEDED:
            self.get_logger().info("Navigation successful")
            return True

        self.get_logger().error(f"Navigation failed: {result}")
        return False

def main():
    """Main function: Initialize system and execute patrol task"""
    rclpy.init()
    # Create patrol node instance
    patrol = PatrolNode()
    # Load navigation points
    point = [2.5,-1.5,-90.0]
    patrol.nav_to_point(point)
    time.sleep(1)
    patrol.get_and_print_qrcode()
    time.sleep(3)

    print("Goal end")
    # 关闭ROS2
    # Shutdown ROS2
    rclpy.shutdown()

if __name__ == '__main__':
    main()