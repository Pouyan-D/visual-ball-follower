from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    params = str(Path(get_package_share_directory('ball_follower')) / 'config' / 'ball_follower.yaml')
    return LaunchDescription([
        DeclareLaunchArgument('enable_motion', default_value='false'),
        Node(
            package='ball_follower',
            executable='ball_follower',
            name='ball_follower',
            output='screen',
            parameters=[params, {'enable_motion': ParameterValue(LaunchConfiguration('enable_motion'), value_type=bool)}],
        ),
    ])
