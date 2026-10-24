"""ROS 2 visual ball follower with an opt-in motion safety switch."""

import rclpy
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image

from .vision import detect_orange_ball


class BallFollower(Node):
    def __init__(self):
        super().__init__('ball_follower')
        parameters = {
            'camera_topic': '/camera/image_raw',
            'cmd_vel_topic': '/cmd_vel',
            'enable_motion': False,
            'linear_speed': 0.08,
            'angular_gain': 0.004,
            'max_angular_speed': 1.0,
            'max_center_error_ratio_for_forward': 0.25,
            'frame_timeout_sec': 0.5,
            'lower_hsv': [6, 110, 110],
            'upper_hsv': [25, 255, 255],
            'min_area': 400.0,
            'min_radius': 15.0,
            'min_circularity': 0.6,
            'morphology_iterations': 3,
        }
        for name, value in parameters.items():
            self.declare_parameter(name, value)

        self._bridge = CvBridge()
        self._last_frame_ns = None
        self._last_detection_ns = None
        self._desired_cmd = Twist()
        self._enabled = bool(self.get_parameter('enable_motion').value)
        camera_topic = str(self.get_parameter('camera_topic').value)
        cmd_vel_topic = str(self.get_parameter('cmd_vel_topic').value)
        self._cmd_pub = self.create_publisher(Twist, cmd_vel_topic, 10)
        self._image_sub = self.create_subscription(
            Image, camera_topic, self._on_image, qos_profile_sensor_data
        )
        self._timer = self.create_timer(0.1, self._publish_command)
        self.get_logger().info(
            f'Ball follower ready: camera={camera_topic}, cmd={cmd_vel_topic}, '
            f'motion_enabled={self._enabled}'
        )

    def _on_image(self, msg: Image):
        now_ns = self.get_clock().now().nanoseconds
        self._last_frame_ns = now_ns
        try:
            image = self._bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            detection = detect_orange_ball(
                image,
                lower_hsv=self.get_parameter('lower_hsv').value,
                upper_hsv=self.get_parameter('upper_hsv').value,
                min_area=float(self.get_parameter('min_area').value),
                min_radius=float(self.get_parameter('min_radius').value),
                min_circularity=float(self.get_parameter('min_circularity').value),
                morphology_iterations=int(self.get_parameter('morphology_iterations').value),
            )
        except (CvBridgeError, ValueError, TypeError) as exc:
            self.get_logger().warning(f'Image could not be processed: {exc}')
            self._desired_cmd = Twist()
            return

        command = Twist()
        if detection is not None:
            self._last_detection_ns = now_ns
            half_width = image.shape[1] / 2.0
            # Positive angular.z turns left in standard ROS base_link convention.
            horizontal_error = half_width - detection.center_x
            gain = float(self.get_parameter('angular_gain').value)
            angular_max = abs(float(self.get_parameter('max_angular_speed').value))
            command.angular.z = max(-angular_max, min(angular_max, gain * horizontal_error))
            if abs(horizontal_error) / max(half_width, 1.0) <= float(
                self.get_parameter('max_center_error_ratio_for_forward').value
            ):
                command.linear.x = max(0.0, float(self.get_parameter('linear_speed').value))

        self._desired_cmd = command

    def _publish_command(self):
        if not self._enabled:
            return
        timeout_ns = int(float(self.get_parameter('frame_timeout_sec').value) * 1e9)
        now_ns = self.get_clock().now().nanoseconds
        if (
            self._last_frame_ns is None
            or self._last_detection_ns is None
            or now_ns - self._last_frame_ns > timeout_ns
            or now_ns - self._last_detection_ns > timeout_ns
        ):
            self._cmd_pub.publish(Twist())
            return
        self._cmd_pub.publish(self._desired_cmd)

    def stop(self):
        if self._enabled:
            self._cmd_pub.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = BallFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
