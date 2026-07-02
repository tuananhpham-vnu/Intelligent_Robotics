from glob import glob
import os

from setuptools import setup

package_name = 'qr_track_alvar'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*.csv')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ros',
    maintainer_email='ros@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    entry_points={
        'console_scripts': [
            'qr_track_alvar = qr_track_alvar.qr_track_alvar:main',
            'qr_scanner = qr_track_alvar.qr_track_alvar:main',
            'patrol_mission = qr_track_alvar.patrol_mission:main',
        ],
    },
)
