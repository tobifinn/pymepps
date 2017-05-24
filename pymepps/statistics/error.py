#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 23.05.17
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
import pandas as pd
import xarray as xr
from pandas.core.datetools import is_timedelta64_dtype

# Internal modules


logger = logging.getLogger(__name__)


def error(spdata, truth_tsdata, iterate_axis='runtime'):
    truth_ts = truth_tsdata.data
    error = []
    for iteration in spdata.data.coords[iterate_axis]:
        logger.debug(iteration.values)
        temp_spdata = spdata.copy()
        temp_spdata.data = spdata.data.loc[{iterate_axis: iteration}]
        pred_tsdata = temp_spdata.to_tsdata(truth_tsdata.lonlat)
        pred_ts = pred_tsdata.data
        if is_timedelta64_dtype(pred_ts.index.dtype):
            pred_ts.index = pred_ts.index+iteration.values
            error_ts = pred_ts.subtract(truth_ts, axis=0).dropna()
            error_ts.index = pd.to_timedelta(
                (error_ts.index-iteration.values).values)
        else:
            error_ts = pred_ts.subtract(truth_ts, axis=0).dropna()
        error_xr = error_ts.to_xarray()
        error_xr[iterate_axis] = iteration
        error_xr = error_xr.set_coords(iterate_axis).expand_dims(iterate_axis)
        error.append(error_xr)
    error = xr.concat(error, dim=iterate_axis)
    return error


def mean_squared_error(spdata, truth_tsdata, iterate_axis='runtime'):
    error_xr = error(spdata, truth_tsdata, iterate_axis)
    return (error_xr**2).mean(dim=iterate_axis)
