#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 06.07.17
#
#Created for pymepps
#
#@author: Tobias Sebastian Finn, tobias.sebastian.finn@studium.uni-hamburg.de
#
#    Copyright (C) {2017}  {Tobias Sebastian Finn}
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# System modules
import logging

# External modules
from xarray.core.extensions import _register_accessor
import pandas as pd

# Internal modules


logger = logging.getLogger(__name__)


def register_dataframe_accessor(name):
    """
    Register a custom accessor on pandas.DataFrame objects.


    Parameters
    ----------
    name : str
        Name under which the accessor should be registered. A warning is issued
        if this name conflicts with a preexisting attribute.
    """
    return _register_accessor(name, pd.DataFrame)


def register_series_accessor(name):
    """
    Register a custom accessor on pandas.Series objects.


    Parameters
    ----------
    name : str
        Name under which the accessor should be registered. A warning is issued
        if this name conflicts with a preexisting attribute.
    """
    return _register_accessor(name, pd.Series)
