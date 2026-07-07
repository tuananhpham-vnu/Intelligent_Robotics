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
        self.declare_parameter('auto_play_on_scan', True)
        self.voice_dir = str(self.get_parameter('voice_dir').value)
        self.auto_play_on_scan = bool(
            self.get_parameter('auto_play_on_scan').value)
        self.last_played_num = None

        pygame.mixer.init()
        if not os.path.isdir(self.voice_dir):
            self.get_logger().warning(
                f'Voice directory does not exist: {self.voice_dir}')

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
            'QR code voice broadcast node started: '
            f'voice_dir={self.voice_dir}, '
            f'auto_play_on_scan={self.auto_play_on_scan}')

    def qrcode_callback(self, msg):
        """Store a recognized QR code and optionally play it immediately."""
        qrcode = msg.data.strip()
        with self._data_lock:
            self.qrcode_data = qrcode
        self.get_logger().info(f'Received QR code data: {qrcode}')

        if self.auto_play_on_scan:
            self.broadcast_qrcode(qrcode)

    def voice_command_callback(self, msg):
        """Play the QR-code voice file when command 1 is received."""
        if msg.data != 1:
            self.get_logger().info(f'Ignoring Voice command: {msg.data}')
            return

        with self._data_lock:
            current_qrcode = self.qrcode_data
            self.qrcode_data = None

        self.broadcast_qrcode(current_qrcode)

    def broadcast_qrcode(self, current_qrcode):
        """Validate a QR payload and play its corresponding MP3 file."""

        if not current_qrcode:
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
        self.get_logger().info(f'Finished broadcasting QR code: {num}')

    def play_voice(self, num):
        """Play the corresponding voice file."""
        file_path = os.path.join(self.voice_dir, f'{num}.mp3')
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'Voice file not found: {file_path}')

        self.get_logger().info(f'Playing voice file: {file_path}')
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
