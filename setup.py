#!/usr/bin/env python
import os.path
import re

from setuptools import find_packages, setup

ROOT_DIR = os.path.dirname(__file__)


def read_contents(local_filepath):
    with open(os.path.join(ROOT_DIR, local_filepath)) as f:
        return f.read()


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
    init_py = read_contents(os.path.join(package, '__init__.py'))
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_long_description(markdown_filepath):
    '''
    Return the long description in RST format, when possible.
    '''
    try:
        import pypandoc
        return pypandoc.convert(markdown_filepath, 'rst')
    except ImportError:
        return read_contents(markdown_filepath)


def get_cmdclass():
    cmdclass = {}
    try:
        from sphinx.setup_command import BuildDoc
    except ImportError:
        pass
    else:
        cmdclass['build_sphinx'] = BuildDoc
    return cmdclass


setup(
    version=get_version('rest_registration'),
    packages=find_packages(exclude=['tests.*', 'tests']),
    long_description=get_long_description('README.md'),
    install_requires=get_requirements('requirements/requirements-base.txt'),
    cmdclass=get_cmdclass(),
    command_options={
        'build_sphinx': {
            'source_dir': ('setup.py', 'docs'),
            'build_dir': ('setup.py', 'docs/_build'),
        },
    },
)
