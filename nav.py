# 导入ROS2相关模块和消息类型
# Import ROS2 related modules and message types
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseStamped
from sensor_msgs.msg import LaserScan, Imu
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy
from rclpy.duration import Duration
from rclpy.client import Client
import time
import math
from tf_transformations import quaternion_from_euler
from std_msgs.msg import String
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from threading import Lock
import voice

class LidarImuDataCollector(Node):
    """
    用于收集LIDAR和IMU数据的ROS2节点
    ROS2 node for collecting LIDAR and IMU data
    """
    def __init__(self):
        super().__init__('data_collector')
        # 数据锁，确保线程安全
        # Data lock to ensure thread safety
        self._data_lock = Lock()
        # 存储二维码数据
        # Store QR code data
        self.qrcode_data = None
        # 创建二维码订阅者
        # Create QR code subscriber
        self.qrcode_sub = self.create_subscription(
            String,
            '/qr_track_result',
            self.qrcode_callback,
            10
        )

    def qrcode_callback(self, msg):
        """
        二维码消息回调函数
        Callback function for QR code messages
        """
        # 记录回调开始时间
        # Record the start time of the callback
        start = time.perf_counter()
        # 使用锁保证数据一致性
        # Use lock to ensure data consistency
        with self._data_lock:
            self.qrcode_data = msg.data
        # 计算回调延迟
        # Calculate callback latency
        latency = (time.perf_counter() - start) * 1000
        # 当延迟过高时发出警告
        # Warn if latency is too high
        if latency > 50:
            self.get_logger().warn(f"Callback delay is too high: {latency:.2f}ms")

    def get_data(self):
        """获取二维码数据，如果没有则返回默认值"""
        """Get QR code data, return default value if none"""
        with self._data_lock:
            return self.qrcode_data if self.qrcode_data else "NO_DATA"

class PatrolNode(BasicNavigator):
    """
    用于机器人巡逻的ROS2节点
    ROS2 node for robot patrol
    """
    def __init__(self, node_name='Patrol_Node'):
        super().__init__(node_name)
        # 初始化数据收集器
        # Initialize data collector
        self.datas = LidarImuDataCollector()
        # 激光扫描数据接收标志
        # Laser scan data reception flag
        self.scan_received_flag = False
        # AMCL位姿数据接收标志
        # AMCL pose data reception flag
        self.amcl_pose_received = False
        # 初始化订阅者
        # Initialize subscribers
        self.init_subscribers()
        # 初始化机器人初始位姿
        # Initialize robot's initial pose
        self.init_pose()
        # 等待系统准备就绪
        # Wait for the system to be ready
        self.wait_for_system_ready()

    def init_subscribers(self):
        """安全地创建订阅者"""
        """Securely create subscribers"""
        try:
            # 创建AMCL位姿订阅者
            # Create AMCL pose subscriber
            self.amcl_pose_sub = self.create_subscription(
                PoseWithCovarianceStamped,
                '/amcl_pose',
                self.amcl_pose_callback,
                10
            )
            # 创建激光扫描订阅者
            # Create laser scan subscriber
            self.scan_sub = self.create_subscription(
                LaserScan,
                '/scan',
                self.scan_received,
                10
            )
        except Exception as e:
            # 订阅者创建失败时记录致命错误并退出
            # Log fatal error and exit if subscriber creation fails
            self.get_logger().fatal(f"Subscription creation failed: {str(e)}")
            rclpy.shutdown()
            exit(1)

    def amcl_pose_callback(self, msg):
        """处理PoseWithCovarianceStamped消息"""
        """Process PoseWithCovarianceStamped message"""
        self.amcl_pose_received = True
        self.get_logger().info("AMCL data has been received.")

    def scan_received(self, msg):
        """激光扫描数据接收回调"""
        """Callback for laser scan data reception"""
        self.scan_received_flag = True

    def wait_for_system_ready(self):
        """等待系统初始化完成"""
        """Wait for system initialization to complete"""
        self.get_logger().info("Waiting for system initialization...")
        # 创建多线程执行器
        # Create multi-threaded executor
        executor = MultiThreadedExecutor(num_threads=2)
        # 添加当前节点和数据收集器节点
        # Add current node and data collector node
        executor.add_node(self)
        executor.add_node(self.datas)
        # 设置超时时间
        # Set timeout
        timeout = 60
        # 记录开始时间
        # Record start time
        start_time = self.get_clock().now().seconds_nanoseconds()[0]

        while rclpy.ok():
            # 单次旋转执行器，处理一次回调
            # Spin executor once to process one callback
            executor.spin_once(timeout_sec=0.1)
            # 检查是否接收到所有必要数据
            # Check if all necessary data has been received
            if self.amcl_pose_received and self.scan_received_flag:
                self.get_logger().info("System initialization completed.")
                # 关闭执行器
                # Shutdown executor
                executor.shutdown()
                return
            # 检查是否超时
            # Check if timeout
            if (self.get_clock().now().seconds_nanoseconds()[0] - start_time) > timeout * 1e9:
                self.get_logger().error("Initialization timeout")
                executor.shutdown()
                rclpy.shutdown()
                exit(1)
        # 关闭执行器
        # Shutdown executor
        executor.shutdown()

    def init_pose(self):
        """初始化机器人在地图中的位姿"""
        """Initialize robot's pose in the map"""
        initial_pose = PoseStamped()
        initial_pose.header.frame_id = 'map'
        initial_pose.header.stamp = self.get_clock().now().to_msg()
        # 设置初始位置坐标
        # Set initial position coordinates
        initial_pose.pose.position.x = 0.0
        initial_pose.pose.position.y = 0.0
        # 设置初始朝向
        # Set initial orientation
        initial_pose.pose.orientation.w = 1.0
        # 设置初始位姿
        # Set initial pose
        self.setInitialPose(initial_pose)
        self.get_logger().info("Initial pose setting completed")
        # 等待导航系统激活
        # Wait for navigation system to activate
        self.waitUntilNav2Active()

    def get_and_print_qrcode(self):
        """获取并打印二维码信息，同时进行语音播报"""
        """Get and print QR code information, and perform voice broadcast"""
        # 创建多线程执行器
        # Create multi-threaded executor
        executor = MultiThreadedExecutor(num_threads=2)
        # 添加数据收集器节点
        # Add data collector node
        executor.add_node(self.datas)
        # 记录开始时间
        # Record start time
        st = time.perf_counter()
        try:
            while rclpy.ok():
                # 单次旋转执行器
                # Spin executor once
                executor.spin_once(timeout_sec=0.1)
                # 获取二维码数据
                # Get QR code data
                qrcode = self.datas.qrcode_data
                # 检查是否有有效的二维码数据
                # Check if there is valid QR code data
                if qrcode is not None and qrcode != '':
                    print(f'QR code recognition result: {self.datas.qrcode_data}')
                    # 调用语音播报功能
                    # Call voice broadcast function
                    voice.run_voic(int(qrcode))
                    return int(qrcode)
                # 检查是否超时
                # Check if timeout
                elif (time.perf_counter()-st) > 10:
                    print("no qrcode ...")
                    return 0
        finally:
            # 关闭执行器
            # Shutdown executor
            executor.shutdown()

    def load_navigation_points(self, csv_file_path='./coordinates.csv'):
        """
        从CSV文件加载导航点
        Load navigation points from CSV file
        """
        goal_list = []
        try:
            with open(csv_file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        # 解析CSV文件中的坐标
                        # Parse coordinates from CSV file
                        coords = list(map(float, line.strip('[]').split(',')))
                        goal_list.append(coords)
            return goal_list
        except Exception as e:
            # 加载失败时记录错误
            # Log error if loading fails
            self.get_logger().error(f"Failed to load the navigation point: {str(e)}")
            return []

    def nav_to_point(self, goal):
        """
        导航到指定点
        Navigate to specified point
        """
        # 等待导航系统激活
        # Wait for navigation system to activate
        self.waitUntilNav2Active()
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.get_clock().now().to_msg()
        # 设置目标位置坐标
        # Set target position coordinates
        goal_pose.pose.position.x = goal[0]
        goal_pose.pose.position.y = goal[1]

        # 如果提供了朝向信息，设置目标朝向
        # Set target orientation if provided
        if len(goal) >= 3:
            yaw_deg = goal[2]
            yaw_rad = math.radians(yaw_deg)
            # 从欧拉角计算四元数
            # Calculate quaternion from Euler angles
            q = quaternion_from_euler(0, 0, yaw_rad)
            goal_pose.pose.orientation = PoseStamped().pose.orientation
            goal_pose.pose.orientation.x = q[0]
            goal_pose.pose.orientation.y = q[1]
            goal_pose.pose.orientation.z = q[2]
            goal_pose.pose.orientation.w = q[3]
        else:
            # 默认朝向
            # Default orientation
            goal_pose.pose.orientation.w = 1.0

        # 记录导航目标信息
        # Log navigation target information
        self.get_logger().info(f"Navigate to the destination: x={goal[0]:.2f}, y={goal[1]:.2f}, yaw={goal[2]:.0f}°")
        # 发送导航目标
        # Send navigation goal
        self.goToPose(goal_pose)

        # 设置导航超时时间
        # Set navigation timeout
        timeout_sec = 120
        # 记录开始时间
        # Record start time
        start_time = self.get_clock().now().seconds_nanoseconds()[0]
        # 等待导航完成或超时
        # Wait for navigation to complete or timeout
        while rclpy.ok() and not self.isTaskComplete():
            if (self.get_clock().now().seconds_nanoseconds()[0] - start_time) > timeout_sec * 1e9:
                # 取消任务并记录警告
                # Cancel task and log warning
                self.cancelTask()
                self.get_logger().warn("Navigation timeout")
                break
            # time.sleep(0.1)
        # 获取导航结果
        # Get navigation result
        result = self.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info("Navigation successful")
            return True
        # 记录导航失败信息
        # Log navigation failure information
        self.get_logger().error(f"Navigation failed: {result}")
        return False

def test():
    """测试二维码数据收集功能"""
    """Test QR code data collection function"""
    rclpy.init()
    # 创建数据收集器实例
    # Create data collector instance
    datas = LidarImuDataCollector()
    # 创建多线程执行器
    # Create multi-threaded executor
    executor = MultiThreadedExecutor(num_threads=2)
    # 添加数据收集器节点
    # Add data collector node
    executor.add_node(datas)
    try:
        while rclpy.ok():
            # 非阻塞处理，每0.1秒检查一次
            # Non-blocking processing, check every 0.1 seconds
            executor.spin_once(timeout_sec=0.1)
            # 获取二维码数据
            # Get QR code data
            qrcode = datas.qrcode_data
            if qrcode is not None and qrcode != '':
                print(f'QR code recognition result: {datas.qrcode_data}')
                #voice.run_voic(int(qrcode))
    finally:
        # 关闭执行器
        # Shutdown executor
        executor.shutdown()

def main():
    """主函数：初始化系统并执行巡逻任务"""
    """Main function: Initialize system and execute patrol task"""
    rclpy.init()
    # 创建巡逻节点实例
    # Create patrol node instance
    patrol = PatrolNode()
    # 加载导航点
    # Load navigation points
    point = patrol.load_navigation_points()
    if not point:
        # 没有导航点时关闭系统
        # Shutdown system if no navigation points
        rclpy.shutdown()
        return
    # 导航到第一个点
    # Navigate to the first point
    patrol.nav_to_point(point[0])
    # 获取并处理二维码
    # Get and process QR code
    result = patrol.get_and_print_qrcode()
    #补全其他的导航点
    # Complete other navigation points



    print("goal_end")
    # 关闭ROS2
    # Shutdown ROS2
    rclpy.shutdown()

if __name__ == '__main__':
    main()
