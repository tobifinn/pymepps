#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 28.11.16

Created for pymepps

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
import abc

# External modules
import xarray
import pandas as pd

# Internal modules
from . import station


class Forecast(object):
    def __init__(self, base=None):
        self.base = base
        self.operations = []

    def __sub__(self, other):
        if isinstance(other, SpatialForecast):
            return self.diff_spatial(other)
        elif isinstance(other, PointForecast):
            return self.diff_point(other)
        elif isinstance(other, station.StationData):
            return self.diff_station(other)
        else:
            raise ValueError('Subtraction with an instance of class {0:s}'
                             ' isn\'t implemented yet'.format(other.__name__))

    @abc.abstractmethod
    def open(self):
        pass

    @abc.abstractmethod
    def plot(self):
        pass

    @abc.abstractmethod
    def diff_spatial(self, other):
        pass

    @abc.abstractmethod
    def diff_point(self, other):
        pass

    @abc.abstractmethod
    def diff_station(self, other):
        pass

    @abc.abstractmethod
    def plot(self):
        pass


class SpatialForecast(Forecast):
    """
    Internal data structure is based on xarray instances.
    """
    pass


class SpatialAnalysis(SpatialForecast):
    """
    For more informations see SpatialForecast.
    """
    pass


class PointForecast(Forecast):
    """
    Internal data structure is based on pandas.dataframe instances.
    """
    pass

