#!/usr/bin/env python3
"""Decode QR codes from the TurtleBot 4 OAK-D compressed image topic."""

import cv2
import rclpy
from cv_bridge import CvBridge, CvBridgeError
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import String


class QrScanner(Node):
    """Publish stable, non-empty QR payloads with duplicate suppression."""

    def __init__(self):
        super().__init__('qr_scanner')
        self.declare_parameter(
            'camera_topic', '/oakd/rgb/preview/image_raw/compressed')
        self.declare_parameter('result_topic', '/qr_track_result')
        self.declare_parameter('show_preview', False)
        self.declare_parameter('repeat_delay', 2.0)

        camera_topic = str(self.get_parameter('camera_topic').value)
        result_topic = str(self.get_parameter('result_topic').value)
        self.show_preview = bool(self.get_parameter('show_preview').value)
        self.repeat_delay = float(self.get_parameter('repeat_delay').value)

        self.bridge = CvBridge()
        self.detector = cv2.QRCodeDetector()
        self.last_payload = ''
        self.last_publish_ns = 0
        self.publisher = self.create_publisher(String, result_topic, 10)
        self.subscription = self.create_subscription(
            CompressedImage, camera_topic, self.camera_callback, 10)
        self.get_logger().info(f'Scanning QR codes on {camera_topic}')

    def camera_callback(self, image_msg):
        try:
            image = self.bridge.compressed_imgmsg_to_cv2(image_msg, 'bgr8')
        except CvBridgeError as error:
            self.get_logger().warning(f'Cannot convert camera image: {error}')
            return

        payload, points, _ = self.detector.detectAndDecode(image)
        payload = payload.strip()
        now_ns = self.get_clock().now().nanoseconds
        delay_ns = int(self.repeat_delay * 1e9)
        can_publish = (
            payload and
            (payload != self.last_payload or now_ns - self.last_publish_ns >= delay_ns)
        )
        if can_publish:
            message = String()
            message.data = payload
            self.publisher.publish(message)
            self.last_payload = payload
            self.last_publish_ns = now_ns
            self.get_logger().info(f'QR detected: {payload}')

        if self.show_preview:
            if points is not None:
                polygon = points.astype(int).reshape((-1, 1, 2))
                cv2.polylines(image, [polygon], True, (0, 255, 0), 2)
            cv2.imshow('QR scanner', image)
            cv2.waitKey(1)

    def destroy_node(self):
        if self.show_preview:
            cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = QrScanner()
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
