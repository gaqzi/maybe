#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def version():
    import radish
    return radish.__version__


extra_dependencies = []
extra_test_dependencies = []
if sys.version_info < (3, 0):
    extra_dependencies = [
        'subprocess32',
    ]
    extra_test_dependencies = [
        'mock',
    ]


def try_to_convert_to_rst(text):
    try:
        import pypandoc
    except ImportError:
        return text

    pypandoc.convert_text(text, 'rst', format='md')


README = try_to_convert_to_rst(open(os.path.join(os.path.dirname(__file__), 'README.md')).read())

setup(
    name='radish-run',
    author='Björn Andersson',
    author_email='ba@sanitarium.se',
    license='Beerware license',
    url='https://github.com/gaqzi/radish/',
    description='A task runner that understands version control',
    long_description=README,
    version=version(),
    packages=find_packages(exclude=('tests',)),
    cmdclass={'test': PyTest},
    install_requires=[
        'pyyaml',
        'docopts',
        'six',
        'path.py',
    ] + extra_dependencies,
    tests_require=[
        'pytest',
        'pytest-cov',
    ] + extra_test_dependencies,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts': [
            'radish = radish.cli:main'
        ]
    }
)
