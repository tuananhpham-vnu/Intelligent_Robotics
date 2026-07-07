from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'qr_code_voice_node'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools', 'pygame'],
    zip_safe=True,
    maintainer='turtlebot4',
    maintainer_email='cobala869@gmail.com',
    description='QR code voice broadcast node',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'qr_code_voice_node = '
            'qr_code_voice_node.qr_code_voice_node:main',
        ],
    },
)
