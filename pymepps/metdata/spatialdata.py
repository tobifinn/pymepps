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

    def __getattr__(self, key):
        if key == 'data':
            logger.exception(" ".join([
                "Can't access data attribute.",
                "Did you try to access properties before",
                "loading data?"
            ]))
        return self._xr_function(key)

    def _xr_function(self, key):
        """
        Get xarray.DataArray function with given key. This is a wrapper around
        xarray.DataArray functions to secure a SpatialData return value.

        Parameters
        ----------
        key : str
            The function which should be called. Have to be an available
            function for a xarray.DataArray!

        Returns
        -------
        wrapped_func : function
            The wrapped xarray.DataArray function. The wrapped function returns
            a new SpatialData instance, if the result of the function is a new
            xarray.DataArray, else the return value of the function will be
            returned.
        """
        def wrapped_func(*args, **kwargs):
            try:
                result = getattr(self.data, key)(*args, **kwargs)
            except TypeError:
                result = getattr(self.data, key)
            if isinstance(result, xr.DataArray):
                return SpatialData(result, self.data_origin)
            else:
                return result
        return wrapped_func

    def __getitem__(self, key):
        return SpatialData(self.data.__getitem__(key), self.data_origin)

    def __setitem__(self, key, value):
        return self.data.__setitem__(key, value)

    def plot(self, analysis=None, ):
        pass
