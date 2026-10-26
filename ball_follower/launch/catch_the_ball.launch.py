from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ball_follower',
            executable='perception_node',
            name='perception_node',
            output='screen'
        ),
        Node(
            package='ball_follower',
            executable='controller_node',
            name='controller_node',
            output='screen'
        )
    ])
