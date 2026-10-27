# TurtleBot3 Visual Ball Follower

A ROS 2 computer vision and robot control project that enables a TurtleBot3 Burger to detect and follow an orange ball using a monocular camera.

## Features

- Real-time orange ball detection using OpenCV
- HSV color segmentation and morphological filtering
- Contour detection and circularity validation
- Separate perception and control ROS 2 nodes
- Proportional steering with exponential smoothing
- Velocity commands published through `/cmd_vel`
- Stop command when a no-ball detection message is received

## System Architecture

Camera (`/image_raw`)
       |
       v
Perception Node
       |
       | `/ball_detection`
       | geometry_msgs/Point
       v
Controller Node
       |
       | `/cmd_vel`
       | geometry_msgs/Twist
       v
TurtleBot3 Burger

## Technologies

- Python 3
- ROS 2 Humble
- OpenCV
- NumPy
- cv_bridge
- TurtleBot3 Burger

## Detection Algorithm

The perception node uses HSV color thresholds to segment the orange ball.

Detection candidates are filtered using:

- Minimum radius: 15 pixels
- Minimum contour area: 400 pixels²
- Minimum circularity: 0.6

Valid detections publish the ball's image coordinates and radius.

## Robot Control

The controller uses proportional steering with exponential smoothing.

Parameters:

- Angular proportional gain: 0.004
- Smoothing factor: 0.3
- Maximum angular velocity: 1.0 rad/s
- Forward velocity: 0.06 or 0.12 m/s

If the perception node reports no ball, the controller publishes a zero-velocity command.

## Running the Project

Requires ROS 2 Humble and the package dependencies.

Build the ROS 2 package using colcon, then source the install environment.

Launch the perception and controller nodes:

```bash
ros2 launch ball_follower catch_the_ball.launch.py
```

The perception node expects camera images on `/image_raw`.

## Validation

- Original implementation previously operated with a TurtleBot3
- ROS 2 package builds successfully
- All three ROS 2 executables are registered
- Offline `/ball_detection` to `/cmd_vel` controller tests passed

## Known Limitations

- HSV detection is sensitive to changing lighting
- The controller assumes a 640-pixel-wide image
- No watchdog currently handles complete loss of detection messages
- Forward motion does not use distance-based stopping
- The updated GitHub package has not yet been retested on physical hardware

## Author

Pouyan Damghani

M.Sc. Digital Technologies

Computer Vision | Robotics | Machine Learning

[LinkedIn](https://www.linkedin.com/in/pouyan-damghani-b18134325/)
