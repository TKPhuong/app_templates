from setuptools import setup, find_packages

setup(
    name="templates",
    version="0.1",
    packages=find_packages(),
    description="Code templates for ease of future usages",
    author="Author Name",
    author_email="author@example.com",
    install_requires=[
        'sqlalchemy',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
