#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
import numpy as np

class PerceptionNode(Node):
    def __init__(self):
        super().__init__('perception_node')

        self.subscription = self.create_subscription(
            Image,
            '/image_raw',
            self.image_callback,
            10)

        self.detection_pub = self.create_publisher(Point, '/ball_detection', 10)

        self.bridge = CvBridge()

        # Orange ball HSV range (tuned against skin)
        self.lower_color = np.array([6, 110, 110])
        self.upper_color = np.array([22, 255, 255])

        self.get_logger().info('Perception node started - looking for orange ball')

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'CV Bridge error: {e}')
            return

        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)

        # Clean the mask
        mask = cv2.erode(mask, None, iterations=3)
        mask = cv2.dilate(mask, None, iterations=3)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detection = Point()
        detection.x = 0.0
        detection.y = 0.0
        detection.z = 0.0   # z = 0 means "no ball detected"

        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            ((x, y), radius) = cv2.minEnclosingCircle(c)

            if radius > 15 and area > 400:
                perimeter = cv2.arcLength(c, True)
                circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0

                if circularity > 0.6:
                    detection.x = float(x)
                    detection.y = float(y)
                    detection.z = float(radius)   # we use z as radius / confidence

                    # Draw for visualization
                    cv2.circle(cv_image, (int(x), int(y)), int(radius), (0, 255, 0), 2)
                    cv2.circle(cv_image, (int(x), int(y)), 5, (0, 0, 255), -1)

        # Publish the result
        self.detection_pub.publish(detection)

        # Visualization
        cv2.imshow('Perception - Camera', cv_image)
        cv2.imshow('Perception - Mask', mask)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = PerceptionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
