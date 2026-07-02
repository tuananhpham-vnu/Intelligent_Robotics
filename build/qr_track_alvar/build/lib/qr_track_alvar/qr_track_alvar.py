#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from .decodeimg import *
import cv2
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
from sensor_msgs.msg import CompressedImage
 
bridge = CvBridge() # 转换为ros2的消息类型(imgmsg)的工具

class QrTrackAlvar(Node):

    def __init__(self):
        super().__init__('qr_track_alvar')
        self.get_logger().info("qr_track_alvar node init")
        self.subscription_camera = self.create_subscription(
            CompressedImage,
            #'color/preview/image',
            '/oakd/rgb/preview/image_raw/compressed',
            #'/image_raw/compressed',
            self.camera_callback,
            15)
        self.subscription_camera  # prevent unused variable warning
        self.subscription_image = self.create_subscription(
            String,
            'local_path',
            self.image_callback,
            3)
        self.subscription_image  # prevent unused variable warning
        self.publisher_ = self.create_publisher(String, 'qr_track_result', 10)

    def camera_callback(self, image):
        #self.get_logger().info('I heard a image: "%s"' % image.data)
        global bridge
        #cv_img = bridge.imgmsg_to_cv2(image, "bgr8")
        cv_img = bridge.compressed_imgmsg_to_cv2(image, "bgr8")
        result = decodeimg(cv_img, 0)
        self.result_publish(result)

    def image_callback(self, path):
        #self.get_logger().info('I heard a imagepath: "%s"' % path.data)
        global bridge
        cv_img = cv2.imread(path.data)
        result = decodeimg(cv_img, 1)
        self.result_publish(result)
        
    def result_publish(self, result):
        msg = String()
        msg.data = result
        self.publisher_.publish(msg)
        #self.get_logger().info('Publishing: "%s"' % msg.data)

def main(args=None):
    rclpy.init(args=args)

    qr_subscriber = QrTrackAlvar()

    rclpy.spin(qr_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    qr_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
