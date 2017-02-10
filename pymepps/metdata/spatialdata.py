#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 09.12.16

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
import logging

# External modules
import xarray as xr

# Internal modules
from .metdata import MetData
import pymepps.plot


logger = logging.getLogger(__name__)


class SpatialData(MetData):
    def __init__(self, data_base, data_origin):
        """
        SpatialData contains spatial based data structures. This class is the
        standard data type for file types like netCDF or grib. It's prepared
        for the output of numerical and statistical weather models.
        Array based data is always saved to netcdf via xarray.

        Attributes
        ----------
        data_base : xarray.DataArray or None
            The data of this grid based data structure.
        data_origin : object of pymepps
            The origin of this data. This could be a model run, a station, a
            database or something else.
        """
        super().__init__(data_base, data_origin)

    def plot(self, method='contourf'):
        plot = pymepps.plot.SpatialPlot()
        plot.add_subplot()
        getattr(plot, method)(self.data)
        plot.suptitle('{0:s} plot of {1:s}'.format(method, self.data.variable))
        return plot
