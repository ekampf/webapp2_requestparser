#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import codecs
import os
import re

root_dir = os.path.abspath(os.path.dirname(__file__))

def get_build_number():
    fname = 'build.info'
    if os.path.isfile(fname):
        with open(fname) as f:
            build_number = f.read()
            build_number = re.sub("[^a-z0-9]+","", build_number, flags=re.IGNORECASE)
            return '.' + build_number

    return ''

def get_version(package_name):
    build_number = get_build_number()

    version_re = re.compile(r"^__version__ = [\"']([\w_.-]+)[\"']$")
    package_components = package_name.split('.')
    init_path = os.path.join(root_dir, *(package_components + ['__init__.py']))
    with codecs.open(init_path, 'r', 'utf-8') as f:
        for line in f:
            match = version_re.match(line[:-1])
            if match:
                return match.groups()[0]+build_number

    return '0.1.0' + build_number

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'webapp2==2.5.2',
    'webob==1.2.3',
    'jsonschema==2.3.0',
    'inflection==0.3.1'
]

test_requirements = [
    'mock==1.1.2'
]

setup(
    name='webapp2_restful',
    version=get_version('webapp2_restful'),
    description="A Request parsing interface designed to provide simple and uniform access to any variable on the webapp2.Request object in Webapp2",
    long_description=readme + '\n\n' + history,
    author="Eran Kampf",
    author_email='eran@ekampf.com',
    url='https://github.com/ekampf/webapp2_restful',
    packages=[
        'webapp2_restful',
    ],
    package_dir={'webapp2_restful': 'webapp2_restful'},
    include_package_data=True,
    setup_requires=[
        'setuptools-lint',
    ],
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='webapp2_restful',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ],
    test_suite='tests',
    tests_require=test_requirements
)
