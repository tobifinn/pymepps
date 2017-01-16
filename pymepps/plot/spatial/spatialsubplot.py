#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 09.01.17

Created for pymepps

@author: Tobias Sebastian Finn, tobias.sebastian.finn@studium.uni-hamburg.de

    Copyright (C) {2017}  {Tobias Sebastian Finn}

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
import numpy as np
import xarray.core.dataarray
import matplotlib.pyplot as plt

# Internal modules
from ..subplot import Subplot


logger = logging.getLogger(__name__)


class SpatialSubplot(Subplot):
    def __init__(self, stylesheets=None, *args, **kwargs):
        super().__init__(stylesheets, *args, **kwargs)
        self._plot_methods = [
            'contourf',
            'contour'
        ]

    def _extract_data(self, data):
        if isinstance(data, xarray.core.dataarray.DataArray):
            dim_names = data.squeeze().dims
            dims = tuple([data[dim] for dim in dim_names])
            plot_data = data.values.squeeze()
        elif isinstance(data, np.ndarray):
            array_shape = data.squeeze().shape
            dims = tuple([np.arange(shp) for shp in array_shape])
            plot_data = data
        elif hasattr(data, '__iter__') and len(data) == 3:
            dims = data[:2]
            plot_data = data[2]
        else:
            raise ValueError('The data has to be a xarray.DataArray or a '
                             'numpy.ndarray!')
        return dims[0], dims[1], plot_data
