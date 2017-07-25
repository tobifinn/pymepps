# -*- coding: utf-8 -*-
"""
Created on 09.05.16

Based on: https://github.com/pypa/sampleproject

@author: Tobias Sebastian Finn, tobias.sebastian.finn@studium.uni-hamburg.de

    Copyright (C) {2016}  {Tobias Sebastian Finn}

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
# System modules
from distutils.core import setup
from codecs import open
from os import path

# External modules

# Internal modules
import pymepps

__version__ = "0.1"


setup(
    name='pymepps',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=pymepps.__version__,

    description='A meteorological post-processing system based on python',

    # The project's main homepage.
    url='https://github.com/maestrotf/pymepps',

    # Author details
    author='Tobias Sebastian Finn',
    author_email='t.finn@meteowindow.com',

    # Choose your license
    license='GPL3',

    # What does your project relate to?
    keywords='statistics meteorology post-processing system forecast '
             'verification plotting',
    packages=["pymepps"],
    package_dir={"pymepps": "pymepps"},
)
