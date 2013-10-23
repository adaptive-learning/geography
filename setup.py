#!/usr/bin/env python

from setuptools import setup

setup(
    name='Geography',
    version='1.0',
    description='Intelligent application for practicing blind maps.',
    author='Vit Stanislav',
    author_email='slaweet@seznam.cz',
    url='https://github.com/slaweet/geography',
    install_requires=['Django>=1.5','south', 'django-lazysignup', 'django-social-auth' ,'django-flatblocks>=0.7'],
)
