#!/usr/bin/env python3

import os
from threading import Lock

import pygame
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int8, String


class QrCodeVoiceNode(Node):
    def __init__(self):
        super().__init__('qr_code_voice_node')

        self._data_lock = Lock()
        self.qrcode_data = None
        self.declare_parameter(
            'voice_dir', '/home/turtlebot4/training_code/voice')
        self.voice_dir = self.get_parameter('voice_dir').value
        self.last_played_num = None

        pygame.mixer.init()

        self.qrcode_sub = self.create_subscription(
            String,
            '/qr_track_result',
            self.qrcode_callback,
            10,
        )
        self.voice_sub = self.create_subscription(
            Int8,
            '/Voice',
            self.voice_command_callback,
            10,
        )

        self.get_logger().info(
            'QR code voice broadcast node started, listening to /Voice topic')

    def qrcode_callback(self, msg):
        """Store the most recently recognized QR code."""
        with self._data_lock:
            self.qrcode_data = msg.data
        self.get_logger().debug(
            f'Received QR code data: {self.qrcode_data}')

    def voice_command_callback(self, msg):
        """Play the QR-code voice file when command 1 is received."""
        if msg.data != 1:
            self.get_logger().info(f'Ignoring Voice command: {msg.data}')
            return

        with self._data_lock:
            current_qrcode = self.qrcode_data
            self.qrcode_data = None

        if not current_qrcode or not current_qrcode.strip():
            self.get_logger().info('No valid QR code data')
            return

        try:
            num = int(current_qrcode)
        except ValueError:
            self.get_logger().error(f'Invalid QR code: {current_qrcode}')
            return

        if num == self.last_played_num:
            self.get_logger().info(f'Skipping repeated broadcast: {num}')
            return

        try:
            self.play_voice(num)
        except (FileNotFoundError, pygame.error) as error:
            self.get_logger().error(str(error))
            return

        self.last_played_num = num
        self.get_logger().info(f'Broadcasting QR code: {num}')

    def play_voice(self, num):
        """Play the corresponding voice file."""
        file_path = os.path.join(self.voice_dir, f'{num}.mp3')
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'Voice file not found: {file_path}')

        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)


def main(args=None):
    rclpy.init(args=args)
    node = QrCodeVoiceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('User interrupted, shutting down node...')
    finally:
        pygame.mixer.quit()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
