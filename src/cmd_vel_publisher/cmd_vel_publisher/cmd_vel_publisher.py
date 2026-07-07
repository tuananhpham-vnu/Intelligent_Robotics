#!/usr/bin/env python3

import time

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int8


class CmdVelPublisher(Node):
    def __init__(self):
        super().__init__('cmd_vel_publisher')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.voice_pub = self.create_publisher(Int8, '/Voice', 10)

    def send(self, vx: float, wz: float):
        msg = Twist()
        msg.linear.x = vx
        msg.angular.z = wz
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelPublisher()
    voice_msg = Int8()

    try:
        node.get_logger().info('Going straight for 5 s ...')
        t0 = time.time()
        while time.time() - t0 < 5.0:
            node.send(0.1, 0.0)
            time.sleep(0.1)

        time.sleep(1)
        voice_msg.data = 1
        node.voice_pub.publish(voice_msg)

        time.sleep(3)
        voice_msg.data = 0
        node.voice_pub.publish(voice_msg)

        node.get_logger().info('Turning right for 3 s ...')
        t0 = time.time()
        while time.time() - t0 < 3.0:
            node.send(0.0, -0.5)
            time.sleep(0.1)
    finally:
        node.send(0.0, 0.0)
        node.get_logger().info('Mission complete, shutting down.')
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
