#!/usr/bin/env python
import os.path
import re

from setuptools import find_packages, setup

ROOT_DIR = os.path.dirname(__file__)


def get_requirements(requirements_filepath):
    '''
    Return list of this package requirements via local filepath.
    '''
    requirements = []
    with open(os.path.join(ROOT_DIR, requirements_filepath), 'rt') as f:
        for line in f:
            if line.startswith('#'):
                continue
            line = line.rstrip()
            if not line:
                continue
            requirements.append(line)
    return requirements


def get_version(package):
    '''
    Return package version as listed in `__version__` in `init.py`.
    '''
    with open(os.path.join(ROOT_DIR, package, '__init__.py'), 'rt') as f:
        init_py = f.read()
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


setup(
    version=get_version('rest_registration'),
    packages=find_packages(exclude=['tests.*', 'tests']),
    install_requires=get_requirements('requirements/requirements-base.txt'),
)
