#!/usr/bin/env python

import versioneer
from setuptools import setup, find_packages
from codecs import open
from os import path

# Get the long description from the relevant file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cornbread',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),

    description='Desktop activity tracking',
    long_description=long_description,

    url='https://github.com/tomislacker/cornbread',

    author='Ben Tomasik',
    author_email='ben@tomasik.io',

    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',

        'License :: OSI Approved :: Apache',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords='desktop activity',

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=[
        'docopt',
    ],

    extras_require={
        'dev': [
            'coverage',
            'cov-core',
            'flake8',
            'mock',
            'nose2',
            'pylint',
            'Sphinx',
            'versioneer',
        ],
        'test': [
            'coverage',
            'cov-core',
            'Sphinx',
            'pylint',
            'versioneer',
        ],
    },

    package_data={},
    data_files=[],
    entry_points={
        'console_scripts': [
            'cornbread=cornbread.__main__:entrypoint',
        ],
    },
)
