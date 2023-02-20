from setuptools import setup, find_packages

setup(
    name="my_package",
    version="1.0.0",
    description="A package for linear regression",
    packages=find_packages(),
    install_requires=[
        "numpy",
    ],
    test_suite="tests",
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
