import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'ball_follower'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pouyan',
    maintainer_email='p.damghani@ostfalia.de',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
	   'perception_node = ball_follower.perception_node:main',
	   'controller_node = ball_follower.controller_node:main',
	   'image_subscriber = ball_follower.image_subscriber:main',
        ],
    },
)
