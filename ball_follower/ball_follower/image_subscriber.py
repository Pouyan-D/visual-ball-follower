#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

class BallFollower(Node):
    def __init__(self):
        super().__init__('ball_follower')

        # Subscribe to camera
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)

        # Publisher for robot movement
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.bridge = CvBridge()
        self.get_logger().info('Ball follower started...')

        # Orange color range (stricter against skin)
        self.lower_color = np.array([6, 110, 110])
        self.upper_color = np.array([25, 255, 255])

        # Control gains (you can tune these)
        self.Kp_angular = 0.004     # how strongly it turns
        self.max_angular = 1.0      # maximum turn speed

        cv2.namedWindow('Mask')

        cv2.createTrackbar('HueMin','Mask',self.lower_color[0],179,lambda x: None)
        cv2.createTrackbar('SaturationMin','Mask',self.lower_color[1],255,lambda x: None)
        cv2.createTrackbar('ValueMin','Mask',self.lower_color[2],255,lambda x: None)
        cv2.createTrackbar('HueMax','Mask',self.upper_color[0],179,lambda x: None)
        cv2.createTrackbar('SaturationMax','Mask',self.upper_color[1],255,lambda x: None)
        cv2.createTrackbar('ValueMax','Mask',self.upper_color[2],255,lambda x: None)


    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f'Conversion error: {e}')
            return

        hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        self.lower_color[0] = cv2.getTrackbarPos('HueMin','Mask')
        self.lower_color[1] = cv2.getTrackbarPos('SaturationMin','Mask')
        self.lower_color[2] = cv2.getTrackbarPos('ValueMin','Mask')
        self.upper_color[0] = cv2.getTrackbarPos('HueMax','Mask')
        self.upper_color[1] = cv2.getTrackbarPos('SaturationMax','Mask')
        self.upper_color[2] = cv2.getTrackbarPos('ValueMax','Mask')
        mask = cv2.inRange(hsv, self.lower_color, self.upper_color)

        # Clean mask
        mask_coarse = cv2.erode(mask, None, iterations=3)
        mask_coarse = cv2.dilate(mask_coarse, None, iterations=3)

        contours, _ = cv2.findContours(mask_coarse, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        twist = Twist()   # default = stop

        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            ((x, y), radius) = cv2.minEnclosingCircle(c)

            if radius > 15 and area > 400:
                perimeter = cv2.arcLength(c, True)
                circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0

                if circularity > 0.6:
                    # Draw on image
                    cv2.circle(cv_image, (int(x), int(y)), int(radius), (0, 255, 0), 2)
                    cv2.circle(cv_image, (int(x), int(y)), 5, (0, 0, 255), -1)

                    height, width = cv_image.shape[:2]
                    center_x = width // 2
                    error = int(x - center_x)

                    # === Steering control ===
                    angular_z = -self.Kp_angular * error
                    # Limit the maximum turning speed
                    angular_z = max(min(angular_z, self.max_angular), -self.max_angular)

                    twist.angular.z = angular_z

                    # Optional: move forward a little when ball is centered
                    if abs(error) < 40:
                        twist.linear.x = 0.1   # slow forward
                    else:
                        twist.linear.x = 0.05  # very slow while turning

                    self.get_logger().info(
                        f'x={int(x)} error={error} angular={angular_z:.2f}',
                        throttle_duration_sec=0.4)

        # Always publish (even if no ball → robot stops)
        self.cmd_vel_pub.publish(twist)

        cv2.imshow('Camera', cv_image)
        cv2.imshow('Mask', mask)
        cv2.imshow('MaskCoarse', mask_coarse)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = BallFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop the robot when we quit
        stop = Twist()
        node.cmd_vel_pub.publish(stop)
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()

if __name__ == '__main__':
    main()