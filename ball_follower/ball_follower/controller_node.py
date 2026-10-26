#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, Twist

class ControllerNode(Node):
    def __init__(self):
        super().__init__('controller_node')

        self.subscription = self.create_subscription(
            Point,
            '/ball_detection',
            self.detection_callback,
            10)

        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        # Control parameters
        self.Kp_angular = 0.004
        self.max_angular = 1.0
        self.image_center_x = 320          # change if your camera width is different
        self.filtered_error = 0.0
        self.alpha = 0.3                   # smoothing factor

        self.get_logger().info('Controller node started')

    def detection_callback(self, msg: Point):
        twist = Twist()

        # msg.z == 0 means no ball detected
        if msg.z > 0:
            error = msg.x - self.image_center_x

            # Smooth the error
            self.filtered_error = self.alpha * error + (1 - self.alpha) * self.filtered_error

            # Calculate angular velocity
            angular_z = -self.Kp_angular * self.filtered_error
            angular_z = max(min(angular_z, self.max_angular), -self.max_angular)

            twist.angular.z = angular_z

            # Simple forward speed logic
            if abs(self.filtered_error) < 40:
                twist.linear.x = 0.12
            else:
                twist.linear.x = 0.06

            self.get_logger().info(
                f'error={self.filtered_error:.1f}  angular={angular_z:.2f}',
                throttle_duration_sec=0.4)
        else:
            # No ball → stop
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        self.cmd_vel_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Safety: stop the robot
        stop = Twist()
        node.cmd_vel_pub.publish(stop)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
