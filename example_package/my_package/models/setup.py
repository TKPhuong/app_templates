from setuptools import setup, find_packages

setup(
    name="my_package_models",
    version="1.0.0",
    description="Linear regression models",
    packages=find_packages(),
    install_requires=[
        "numpy",
    ],
)
