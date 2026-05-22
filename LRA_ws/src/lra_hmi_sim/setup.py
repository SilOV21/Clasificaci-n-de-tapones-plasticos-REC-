import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'lra_hmi_sim'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='LRA Team',
    maintainer_email='asil.arnous@opendeusto.es',
    description='Simulation nodes and test harness for the lra_hmi package.',
    license='Apache-2.0',
    extras_require={'test': ['pytest']},
    entry_points={
        'console_scripts': [
            'fake_ur_driver = lra_hmi_sim.fake_ur_driver:main',
            'fake_vision = lra_hmi_sim.fake_vision:main',
            'vision_enable_logger = lra_hmi_sim.vision_enable_logger:main',
            'crashy_node = lra_hmi_sim.crashy_node:main',
        ],
    },
)
