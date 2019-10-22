#! /usr/bin/env python
# -*- coding: utf8 -*-

import os
import io
from setuptools import setup


def read(fname):
    return io.open(os.path.join(os.path.dirname(__file__), fname),'r',encoding='utf-8').read()

setup(
    name = "valkuil-frontend",
    version = "2.0", #also change in __init__.py
    author = "Maarten van Gompel",
    author_email = "proycon@anaproy.nl",
    description = ("Web frontend for Valkuil"),
    license = "GPL",
    keywords = "nlp computational_linguistics spelling_correction",
    url = "https://github.com/proycon/valkuil-frontend",
    packages=['valkuilnet'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Text Processing :: Linguistic",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    entry_points = {
        'console_scripts': [
        ]
    },
    include_package_data=True,
    package_data = {'valkuilnet': ['templates/*', 'static/*']},
    install_requires=['clam >= 2.3', 'folia >= 2.2.0', 'flask >= 1.0']
)
