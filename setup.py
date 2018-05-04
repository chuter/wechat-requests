#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import find_packages, setup

DESCRIPTION = 'so eazy to interact with wechat api'
URL = 'https://github.com/chuter/wechat'
EMAIL = 'topgun.chuter@gmail.com'
AUTHOR = 'chuter'
VERSION = None

# What packages are required for this module to be executed?
REQUIRED = [
    'six',
    'certifi',
    'requests>=2.18.4',
    'lxml',
    'bs4'
]

TEST_REQUIREMENTS = [
    'pytest-httpbin==0.0.7',
    'pytest-cov',
    'pytest-mock',
    'pytest-xdist',
    'pytest>=2.8.0'
]

here = os.path.abspath(os.path.dirname(__file__))
src = os.path.join(here, 'src')


with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()


about = {}
if VERSION is None:
    with open(os.path.join(src, 'wechat', '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


setup(
    name=about['__name__'],
    version=about['__version__'],
    description=DESCRIPTION,
    license='MIT',
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=">=2.6, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    url=URL,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=REQUIRED,
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: Chinese (Simplified)',
        'License :: OSI Approved :: MIT',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    keywords=[
        'wechat', 'weixin', 'wxpay', 'api', 'apiclient', 'requests'
    ],
    tests_require=TEST_REQUIREMENTS,
    setup_requires=['pytest-runner'],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
)
