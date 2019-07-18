#!/usr/bin/env python

"""
Setup script for ParaNoodles.
"""

from pathlib import Path
from setuptools import setup, find_packages

# Get the long description from the README file
here = Path(__file__).parent.absolute()
with (here / 'README.md').open(encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ParaNoodles',
    version='0.1',
    description='Parallel-in-time integration for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Johan Hidding',
    url='https://github.com/ParallelWindfarms/paranoodles',
    packages=find_packages(exclude=['test*']),
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Science/Research',
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.7',
        'Topic :: System :: Distributed Computing',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Physics'],

    install_requires=['noodles[xenon,numpy]', 'scipy'],
    extras_require={
        'develop': [
            'pytest', 'pytest', 'coverage', 'pep8', 'numpy', 'tox',
            'sphinx', 'sphinx_rtd_theme', 'nbsphinx', 'flake8'],
    },
)
