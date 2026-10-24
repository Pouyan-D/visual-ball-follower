from glob import glob
from os.path import join
from setuptools import find_packages, setup

package_name = 'ball_follower'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (join('share', package_name, 'launch'), glob('launch/*.py')),
        (join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Pouyan Damghani',
    maintainer_email='damghani.pouyan@gmail.com',
    description='ROS 2 OpenCV visual ball following for TurtleBot3 Burger',
    license='License not selected',
    entry_points={
        'console_scripts': [
            'ball_follower = ball_follower.image_subscriber:main',
        ],
    },
)
