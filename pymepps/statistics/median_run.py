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
import xarray as xr

# Internal modules


logger = logging.getLogger(__name__)


def median_run(data_array, ens_dim='ensemble', iterate_dim='runtime'):
    """
    Calculate the runs with the smallest mean squared deviation to the ensemble
    median. This run could be called median run and could be seen as physically
    correct median solution of the ensemble.

    Parameters
    ----------
    data_array: xarray.DataArray
        This DataArray instance is used as base for the calculations of the
        median run.
    ens_dim: str, optional
        Name of the ensemble axis. Default is ensemble.
    iterate_dim: str, optional
        For every entry within the data of this iterate_dim a new median run is
        calculated. If this is None or the axis is not found, there will be only
        one median run. Default is runtime.

    Returns
    -------
    median_run_array: xarray.DataArray
        The DataArray with the median run data.
    """
    # Interpolation is set to nearest to get a cluster selecting behaviour
    data_median = data_array.quantile(0.5, dim=ens_dim, interpolation='nearest')
    dimensions = list(data_median.dims)
    if iterate_dim in dimensions:
        dimensions.remove(iterate_dim)
    median_deviation = data_array-data_median
    mean_squared_dev = (median_deviation**2).mean(dim=dimensions).squeeze()
    if iterate_dim in data_median.dims:
        data_arrays = []
        for t in mean_squared_dev.coords[iterate_dim]:
            ensemble_dev = mean_squared_dev.loc[{iterate_dim: t}]
            best_iloc = int(ensemble_dev.argmin())
            best_ens_mem = ensemble_dev.coords[ens_dim][best_iloc]
            logger.debug('Selected {0} for {1} as best median member'.format(
                best_ens_mem.values, t.values))
            temp_array = data_array.loc[{
                iterate_dim: t,
                ens_dim: best_ens_mem}].expand_dims(iterate_dim)
            data_arrays.append(temp_array)
        median_run_array = xr.concat(data_arrays, dim=iterate_dim)
    else:
        ensemble_member = mean_squared_dev.argmin()
        median_run_array = data_array.loc[{ens_dim: ensemble_member}]
    median_run_array.pp._grid = data_array.pp._grid
    return median_run_array
