import os.path
import re
from setuptools import setup, find_packages


def get_requirements(filename):
    with open(filename, 'r') as f:
        requirements = f.read().split('\n')

    return requirements


def find_lib_packages():
    return [package for package in find_packages()
            if not package.startswith('tests')]


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def read(fname):
    '''Utility function to read the README file.'''
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='django-rest-registration',
    version=get_version('rest_registration'),
    packages=find_lib_packages(),
    author='Andrzej Pragacz',
    author_email='apragacz@o2.pl',
    description=(
        'User registration REST API, based on django-rest-framework'
    ),
    license='MIT',
    keywords='django rest rest-framework registration',
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers'
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=get_requirements('requirements.txt'),
)
