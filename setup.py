#!/usr/bin/env python

import akcli
from setuptools import setup

setup(name='akcli',
    version=akcli.__version__,
    description='Akamai CLI tool written in Python',
    author="Niranjan Bommu",
    author_email='niranjan.bommu@gmail.com',
    url='https://github.com/nbommu/python-akcli',
    packages=['python-akcli',],
    scripts=['bin/akcli'],
    keywords = ['akamai', 'dns', 'cli', 'client'],
    install_requires=[
                      'requests>=2.0',
                      'edgegrid-python>=1.0.9',
                      'click>=5.1',
    ],
)
