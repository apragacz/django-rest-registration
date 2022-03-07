#!/usr/bin/env python
import os.path
import re

from setuptools import find_packages, setup

ROOT_DIR = os.path.dirname(__file__)
PACKAGE_NAME = 'rest_registration'


def get_version(package):
    '''
    Return package version as listed in `__version__` in package `__init__.py`.
    '''
    init_path = os.path.join(ROOT_DIR, package, '__init__.py')
    with open(init_path, 'rt', encoding='utf-8') as init_file:
        init_contents = init_file.read()
        return re.search(
            "__version__ = ['\"]([^'\"]+)['\"]", init_contents).group(1)


setup(
    version=get_version(PACKAGE_NAME),
    packages=find_packages(exclude=['tests.*', 'tests']),
)
