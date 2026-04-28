from setuptools import setup
import os
from glob import glob

package_name = 'rec_vision'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Delia',
    maintainer_email='delia@alumnos.upm.es',
    description='Vision package REC - Clasificacion tapones por color',
    license='TODO',
    entry_points={
        'console_scripts': [
            'color_calibrator_node = rec_vision.color_calibrator_node:main',
            'detector_tapones      = rec_vision.detector_tapones:main',
            'mcap_publisher        = rec_vision.mcap_publisher:main',
        ],
    },
)
