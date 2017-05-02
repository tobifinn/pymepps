#!/bin/env python
# -*- coding: utf-8 -*-
# """
# Created on 03.12.16
#
# Created for pymepps
#
# @author: Tobias Sebastian Finn, tobias.sebastian.finn@studium.uni-hamburg.de
#
#     Copyright (C) {2016}  {Tobias Sebastian Finn}
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
# """
# System modules
import logging
from copy import deepcopy

# External modules
import pandas as pd
import xarray as xr

# Internal modules


logger = logging.getLogger(__name__)

math_ops = [
    '__add__',
    '__sub__',
    '__div__',
    '__mul__',
    '__pow__',
]


class MetData(object):
    """
    MetData is the base class for meteorological data, like station data,
    nwp forecast data etc.
    """
    def __init__(self, data, data_origin=None):
        self._data = None
        self.data_origin = data_origin
        self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if isinstance(data, str):
            data = self.load(data)
        if data is None:
            raise ValueError(
                '{0:s} needs data!'.format(self.__class__.__name__))
        self._data = data

    def _copy_of_self(self):
        return deepcopy(self)

    def _extract_math_data(self, obj):
        try:
            return getattr(obj, 'data')
        except AttributeError:
            return obj

    def _math_ops(self, op, other):
        data_obj = self._copy_of_self()
        other = self._extract_math_data(other)
        data_obj.data = getattr(data_obj.data, op)(other)
        return data_obj

    def __getattr__(self, key):
        if key == 'data':
            logger.exception(" ".join([
                "Can't access data attribute.",
                "Did you try to access properties before",
                "loading data?"
            ]))
        elif key in math_ops:
            def math_method(other):
                return self._math_ops(key, other)
            return math_method
        else:
            return self._xr_function(key)

    def __getitem__(self, key):
        return type(self)(self.data.__getitem__(key), self.data_origin)

    def __setitem__(self, key, value):
        return self.data.__setitem__(key, value)

    def __call__(self):
        return self.data

    def _xr_function(self, key):
        """
        Get data function with given key. This is a wrapper around
        type(self.data) functions to secure a proper return value.

        Parameters
        ----------
        key : str
            The function which should be called. Have to be an available
            function for type of self.data!

        Returns
        -------
        wrapped_func : function
            The wrapped type(self.data) function. The wrapped function returns
            a new TS/SpatialData instance, if the result of the function is a
            type(self.data), else the return value of the function will be
            returned.
        """
        def wrapped_func(*args, **kwargs):
            try:
                result = getattr(self.data, key)(*args, **kwargs)
            except TypeError:
                result = getattr(self.data, key)
            if isinstance(result, (pd.DataFrame, pd.Series, xr.DataArray)):
                return type(self)(result, self.data_origin)
            else:
                return result
        return wrapped_func

    def data_plot(self, **kwargs):
        """
        Method to refer to the xr_plot layer.
        Parameters
        ----------
        kwargs

        Returns
        -------

        """
        return self.data.plot(**kwargs)
