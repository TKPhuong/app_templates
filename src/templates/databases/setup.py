from setuptools import setup, find_packages

setup(
    name="your_package_name",
    version="0.1",
    description="A description of your package",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=["sqlite3"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords=["database", "sqlite"],
)
