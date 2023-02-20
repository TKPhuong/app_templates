from setuptools import setup, find_packages

setup(
    name="my_package_utils",
    version="1.0.0",
    description="Utility functions for linear regression",
    packages=find_packages(),
    install_requires=[
        "numpy",
    ],
)
