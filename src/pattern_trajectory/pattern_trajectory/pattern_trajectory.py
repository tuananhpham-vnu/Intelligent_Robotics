"""Drive a differential robot through square, infinity, and star patterns."""

import math

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data


def normalize_angle(angle):
    """Wrap an angle to [-pi, pi]."""
    return math.atan2(math.sin(angle), math.cos(angle))


def yaw_from_quaternion(q):
    """Return planar yaw from a quaternion."""
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


class PatternTrajectory(Node):
    """Odometry-feedback state machine for the Experiment 4 patterns."""

    def __init__(self):
        super().__init__('pattern_trajectory')

        self.declare_parameter('patterns', ['square', 'infinity', 'star'])
        self.declare_parameter('side_length', 1.0)
        self.declare_parameter('circle_radius', 0.5)
        self.declare_parameter('linear_speed', 0.15)
        self.declare_parameter('angular_speed', 0.45)
        self.declare_parameter('distance_tolerance', 0.015)
        self.declare_parameter('angle_tolerance', 0.025)
        self.declare_parameter('pause_seconds', 1.0)
        self.declare_parameter('odom_topic', '/odom')
        self.declare_parameter('cmd_vel_topic', '/cmd_vel')

        self.patterns = list(self.get_parameter('patterns').value)
        self.side = float(self.get_parameter('side_length').value)
        self.radius = float(self.get_parameter('circle_radius').value)
        self.linear_speed = float(self.get_parameter('linear_speed').value)
        self.angular_speed = float(self.get_parameter('angular_speed').value)
        self.distance_tolerance = float(
            self.get_parameter('distance_tolerance').value)
        self.angle_tolerance = float(self.get_parameter('angle_tolerance').value)
        self.pause_seconds = float(self.get_parameter('pause_seconds').value)

        cmd_topic = str(self.get_parameter('cmd_vel_topic').value)
        odom_topic = str(self.get_parameter('odom_topic').value)
        self.cmd_pub = self.create_publisher(Twist, cmd_topic, 10)
        self.odom_sub = self.create_subscription(
            Odometry, odom_topic, self.odom_callback, qos_profile_sensor_data)
        self.timer = self.create_timer(0.02, self.control_loop)

        self.pose = None
        self.steps = self.make_steps(self.patterns)
        self.step_index = 0
        self.step_started = False
        self.start_x = 0.0
        self.start_y = 0.0
        self.previous_yaw = 0.0
        self.accumulated_angle = 0.0
        self.pause_start_ns = 0
        self.finished = False

        self.get_logger().info(
            f'Ready: {len(self.steps)} motion steps; waiting for {odom_topic}')

    def make_steps(self, patterns):
        """Translate pattern names into closed-loop motion primitives."""
        steps = []
        for name in patterns:
            key = name.lower().strip()
            if key == 'square':
                for _ in range(4):
                    steps += [('line', self.side), ('turn', math.pi / 2.0)]
            elif key == 'infinity':
                # Two tangent full circles, first counter-clockwise then clockwise.
                steps += [('arc', 2.0 * math.pi, self.radius),
                          ('arc', -2.0 * math.pi, self.radius)]
            elif key == 'star':
                # A regular pentagram: five equal edges and 144-degree turns.
                for _ in range(5):
                    steps += [('line', self.side), ('turn', -4.0 * math.pi / 5.0)]
            else:
                self.get_logger().warning(f'Ignoring unknown pattern: {name}')
                continue
            steps.append(('pause', self.pause_seconds))
        return steps

    def odom_callback(self, msg):
        p = msg.pose.pose.position
        yaw = yaw_from_quaternion(msg.pose.pose.orientation)
        self.pose = (p.x, p.y, yaw)

    def begin_step(self, step):
        self.start_x, self.start_y, self.previous_yaw = self.pose
        self.accumulated_angle = 0.0
        if step[0] == 'pause':
            self.pause_start_ns = self.get_clock().now().nanoseconds
        self.step_started = True
        self.get_logger().info(
            f'Step {self.step_index + 1}/{len(self.steps)}: {step}')

    def measured_turn(self, yaw):
        delta = normalize_angle(yaw - self.previous_yaw)
        self.accumulated_angle += delta
        self.previous_yaw = yaw
        return self.accumulated_angle

    def control_loop(self):
        if self.pose is None or self.finished:
            return
        if self.step_index >= len(self.steps):
            self.stop()
            self.finished = True
            self.get_logger().info('All requested patterns are complete.')
            return

        step = self.steps[self.step_index]
        if not self.step_started:
            self.begin_step(step)

        kind, target = step[0], step[1]
        x, y, yaw = self.pose
        cmd = Twist()
        complete = False

        if kind == 'line':
            distance = math.hypot(x - self.start_x, y - self.start_y)
            error = target - distance
            complete = error <= self.distance_tolerance
            if not complete:
                cmd.linear.x = min(self.linear_speed, max(0.05, 0.8 * error))
                heading_error = normalize_angle(self.previous_yaw - yaw)
                cmd.angular.z = max(-0.35, min(0.35, 1.8 * heading_error))
        elif kind == 'turn':
            turned = self.measured_turn(yaw)
            error = target - turned
            complete = abs(error) <= self.angle_tolerance
            if not complete:
                limit = self.angular_speed
                cmd.angular.z = max(-limit, min(limit, 1.5 * error))
        elif kind == 'arc':
            turned = self.measured_turn(yaw)
            error = target - turned
            complete = abs(error) <= self.angle_tolerance
            if not complete:
                direction = 1.0 if target > 0.0 else -1.0
                nominal = direction * self.linear_speed / step[2]
                # Slow both velocities together near the end, preserving radius.
                magnitude = min(abs(nominal), max(0.08, abs(error)))
                cmd.angular.z = direction * magnitude
                cmd.linear.x = magnitude * step[2]
        elif kind == 'pause':
            elapsed = (self.get_clock().now().nanoseconds - self.pause_start_ns) / 1e9
            complete = elapsed >= target

        if complete:
            self.stop()
            self.step_index += 1
            self.step_started = False
        else:
            self.cmd_pub.publish(cmd)

    def stop(self):
        self.cmd_pub.publish(Twist())

    def destroy_node(self):
        self.stop()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = PatternTrajectory()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
