#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 24.05.17
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
from .metric import Metric


logger = logging.getLogger(__name__)


class ErrorMetric(Metric):
    def __init__(self, iterate_axis='runtime'):
        super().__init__()
        self.iterate_axis = iterate_axis

    def _calc_error(self):
        truth_ts = self.state['truth']
        error = []
        for iteration in self.state['prediction'].coords[self.iterate_axis]:
            temp_data = self.state['prediction'].loc[
                {self.iterate_axis: iteration}]
            temp_data.pp.grid = self.state['prediction'].pp.grid
            pred_ts = temp_data.pp.to_tsdata(self.state['truth'].lonlat)
            if is_timedelta64_dtype(pred_ts.index.dtype):
                pred_ts.index = pred_ts.index + iteration.values
                error_ts = pred_ts.subtract(truth_ts, axis=0).dropna()
                error_ts.index = pd.to_timedelta(
                    (error_ts.index - iteration.values).values)
            else:
                error_ts = pred_ts.subtract(truth_ts, axis=0).dropna()
            error_xr = error_ts.to_xarray()
            if isinstance(error_xr, xr.DataArray):
                error_xr = error_xr.to_dataset(name=temp_data.name)
            error_xr[self.iterate_axis] = iteration
            error_xr = error_xr.set_coords(self.iterate_axis).expand_dims(
                self.iterate_axis)
            error.append(error_xr)
        error = xr.concat(error, dim=self.iterate_axis)
        return error

    def predict(self, X=None, y=None):
        return self._calc_metric(X, y)

    def _truth_is_ts(self):
        return isinstance(self.state['truth'], TSData)
