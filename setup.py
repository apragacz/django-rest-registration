#!/usr/bin/env python
import os.path
import re

from setuptools import find_packages, setup

ROOT_DIR = os.path.dirname(__file__)
PACKAGE_NAME = 'rest_registration'


def get_requirements(local_filepath):
    '''
    Return list of this package requirements via local filepath.
    '''
    requirements_path = os.path.join(ROOT_DIR, local_filepath)
    requirements = []
    with open(requirements_path, 'rt', encoding='utf-8') as req_file:
        for line in req_file:
            if line.startswith('#'):
                continue
            line = line.rstrip()
            if not line:
                continue
            requirements.append(line)
    return requirements


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
    install_requires=get_requirements('requirements/requirements-base.in'),
)
