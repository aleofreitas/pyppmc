# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='pyppmc',
    version='0.1.dev1',
    packages=find_packages(),
    package_dir={'pyppmc': 'pyppmc'},
    data_files = [('', ['LICENSE'])],
    url='http://example.com',
    license='License',
    author='Alexandre Freitas',
    author_email='me@example.com',
    description='Module to provide access to a Micro Focus™ Project and Portfolio Management Center server'
)
