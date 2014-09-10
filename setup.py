# coding:utf8
"""
Created on Jun 18, 2014

@author: ilcwd
"""

import os
from setuptools import setup, find_packages


_CWD = os.path.dirname(__file__)

NAME = 'wechat-server'
DESCRIPTION = 'A wechat server midware.'
AUTHOR = 'ilcwd'
EMAIL = 'ilcwd23@gmail.com'
INSTALL_REQUIRES = [i for i in open(os.path.join(_CWD, 'requirements.txt')).readlines()
                    if not i.startswith(('-', '#', '\n'))]
VERSION = open(os.path.join(_CWD, 'VERSION')).read().strip()

setup(
    name=NAME,
    description=DESCRIPTION,
    # long_description=open(os.path.join(_CWD, 'README.md')).read(),
    version=VERSION,
    packages=find_packages(exclude=['example', 'test']),
    install_requires=INSTALL_REQUIRES,
    author=AUTHOR,
    author_email=EMAIL,
    license="No License",
    platforms=['any'],
    url="",
    classifiers=["Intended Audience :: Developers",
                 "Programming Language :: Python",
                 "Topic :: Server",
                 "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True,
)
