from setuptools import find_packages, setup
import os # <--- NUEVO: Necesario para manejar rutas
from glob import glob # <--- NUEVO: Necesario para encontrar los archivos launch

package_name = 'ur3_vision_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # --- NUEVO: Esta línea instala todos los archivos de la carpeta launch ---
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ruth',
    maintainer_email='ruth@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'ur3_controller = ur3_vision_control.ur3_controller:main',
            'vision_fake = ur3_vision_control.vision_fake:main',
            'ur3_pick_sort = ur3_vision_control.ur3_pick_sort:main',
            'ur3_moveit_test = ur3_vision_control.ur3_moveit_test:main',
            'vision_fake_sort = ur3_vision_control.vision_fake_sort:main',
            'inicio = ur3_vision_control.inicio:main'
        ],
    },
)
