#!/usr/bin/env python
from setuptools import find_packages, setup

# see setup.cfg for package configuration
setup(
    packages=find_packages(exclude=['tests.*', 'tests']),
)
