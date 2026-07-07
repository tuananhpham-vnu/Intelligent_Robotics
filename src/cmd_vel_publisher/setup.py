from setuptools import find_packages, setup

package_name = 'cmd_vel_publisher'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='turtlebot4',
    maintainer_email='cobala869@gmail.com',
    description='Command velocity publisher for Experiment 3',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'cmd_vel_publisher = '
            'cmd_vel_publisher.cmd_vel_publisher:main',
        ],
    },
)
