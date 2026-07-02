import rclpy

from rclpy.node import Node
from nav_msgs.msg import Path, Odometry
from geometry_msgs.msg import PoseStamped
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy


class LivePathVisualizer(Node):
    def __init__(self):
        super().__init__('live_path_visualizer')

        # Declare and initialize node parameters
        self.declare_parameter('odom_topic', '/odom')
        self.declare_parameter('path_topic', '/robot_path')
        self.declare_parameter('frame_id', 'odom')
        self.declare_parameter('max_poses', 10000)  # Maximum number of poses to store
        self.declare_parameter('publish_rate', 10.0)  # Path publishing frequency in Hz

        # Retrieve parameter values
        odom_topic = self.get_parameter('odom_topic').get_parameter_value().string_value
        path_topic = self.get_parameter('path_topic').get_parameter_value().string_value
        self.frame_id = self.get_parameter('frame_id').get_parameter_value().string_value
        self.max_poses = self.get_parameter('max_poses').get_parameter_value().integer_value
        publish_rate = self.get_parameter('publish_rate').get_parameter_value().double_value

        # Initialize Path message
        self.path = Path()
        self.path.header.frame_id = self.frame_id

        # Create Path publisher with reliable QoS
        pub_qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.path_publisher = self.create_publisher(
            Path,
            path_topic,
            pub_qos_profile
        )

        # Subscribe to odometry topic with best effort QoS
        sub_qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.subscription = self.create_subscription(
            Odometry,
            odom_topic,
            self.odom_callback,
            sub_qos_profile
        )

        # Create timer to publish path at specified rate
        self.timer = self.create_timer(
            1.0 / publish_rate,
            self.publish_path
        )

        # Suppress unused variable warning
        self.subscription

        self.get_logger().info(
            f'Started path visualization node. Subscribed to: {odom_topic}'
        )
        self.get_logger().info(
            f'Publishing path to: {path_topic} at {publish_rate} Hz'
        )

    def odom_callback(self, msg):
        """Process incoming odometry messages and update the path."""

        # Create new pose stamped message from odometry
        pose_stamped = PoseStamped()
        pose_stamped.header.stamp = msg.header.stamp
        pose_stamped.header.frame_id = self.frame_id
        pose_stamped.pose = msg.pose.pose

        # Append pose to path
        self.path.poses.append(pose_stamped)

        # Maintain path size within limits
        if len(self.path.poses) > self.max_poses:
            self.path.poses.pop(0)

    def publish_path(self):
        """Publish the accumulated path with updated timestamp."""

        self.path.header.stamp = self.get_clock().now().to_msg()
        self.path_publisher.publish(self.path)


def main(args=None):
    rclpy.init(args=args)

    path_visualizer = LivePathVisualizer()

    try:
        rclpy.spin(path_visualizer)
    except KeyboardInterrupt:
        pass
    finally:
        path_visualizer.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()