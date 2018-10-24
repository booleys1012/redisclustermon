# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2018 Justin Bewley Lo (justinbewley.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

DESCRIPTION = 'RedisClusterMon Application'
LONG_DESCRIPTION = 'Monitors statistics from a Redis cluster using a python flask application which serves an angular5 client frontend'

setup(
    # core details
    name="redisclustermon",
    version="0.0.20180423.1",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,

    # Author details
    author='Justin Bewley Lo',
    author_email='justin@justinbewley.com',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Programming Language :: Python :: 2.7'
    ],

    # use find packages with the same path as package_dir
    packages=find_packages(),

    data_files=[],

    scripts=[
        'pyrcm/rcm.py'
    ],

    install_requires=[
        'flask',
        'flask_restful',
        'flask-socketio',
        'gevent',
        'gevent-websocket',
        'redis-py-cluster'
    ]
)
