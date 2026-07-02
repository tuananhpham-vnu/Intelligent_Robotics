import os
import pygame
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from threading import Lock

class QrCodeReceiver(Node):
    def __init__(self):
        super().__init__('qr_code_receiver')
        self._data_lock = Lock()
        self.qrcode_data = None
        self.qrcode_sub = self.create_subscription(
            String,
            '/qr_track_result',
            self.qrcode_callback,
            10
        )

    def qrcode_callback(self, msg):
        with self._data_lock:
            self.qrcode_data = msg.data

    def get_qrcode_data(self):
        with self._data_lock:
            return self.qrcode_data


def run_voic(num):
    file_path = "./voice"
    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join(file_path, f"{num}.mp3"))
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()


def get_and_print_qrcode():
    rclpy.init()
    receiver = QrCodeReceiver()
    try:
        while rclpy.ok():
            rclpy.spin_once(receiver, timeout_sec=0.1)
            qrcode = receiver.get_qrcode_data()
            if qrcode is not None and qrcode != '':
                print(f'QR code recognition result: {qrcode}')
                run_voic(int(qrcode))
                return int(qrcode)
    finally:
        rclpy.shutdown()


if __name__ == "__main__":
    get_and_print_qrcode()
