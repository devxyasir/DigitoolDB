#!/usr/bin/env python3
"""
Setup script for DigitoolDB
"""
from setuptools import setup, find_packages

setup(
    name="digitooldb",
    version="0.1.0",
    description="A lightweight NoSQL database system similar to MongoDB",
    author="Digitool Team",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=[],  # No external dependencies needed
    entry_points={
        'console_scripts': [
            'digid=src.server.digid:main',        # Server command
            'digi=src.client.cli:main',          # Client command
            'digid-rest=src.server.rest_api:main', # REST API server
            'digi-shell=src.client.interactive_cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
