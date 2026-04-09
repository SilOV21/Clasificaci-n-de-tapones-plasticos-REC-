from setuptools import find_packages
from setuptools import setup

setup(
    name='lra_vision',
    version='1.0.0',
    packages=find_packages(
        include=('lra_vision', 'lra_vision.*')),
)
