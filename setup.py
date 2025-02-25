from setuptools import setup, find_packages

setup(
    name="teleop",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.22.0",
        "scipy>=1.8.0",
        "pybullet>=3.2.1",
        "matplotlib>=3.5.0",
    ],
) 