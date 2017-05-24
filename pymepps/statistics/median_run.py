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


def median_run(spdata, ens_dim='ensemble', iterate_dim='runtime'):
    """
    Calculate the runs with the smallest mean squared deviation to the ensemble
    median. This run could be called median run and could be seen as physically
    correct median solution of the ensemble.

    Parameters
    ----------
    spdata: SpatialData
        This SpatialData instance is used as base for the calculations of the 
        median run.
    ens_dim: str, optional
        Name of the ensemble axis. Default is ensemble.
    iterate_dim: str, optional
        For every entry within the data of this iterate_dim a new median run is
        calculated. If this is None or the axis is not found, there will be only
        one median run. Default is runtime.

    Returns
    -------
    median_run: SpatialData
        The median run SpatialData instance is based on the spdata instance, 
        without the ensemble dimension and with new data values.
    """
    spdata_data = spdata.data
    median_run = spdata.copy()
    # Interpolation is set to nearest to get a cluster selecting behaviour
    spdata_median = spdata_data.quantile(0.5, dim=ens_dim,
                                         interpolation='nearest')

    dimensions = list(spdata_median.dims)
    if iterate_dim in dimensions:
        dimensions.remove(iterate_dim)
    median_deviation = spdata.data-spdata_median
    mean_squared_dev = (median_deviation**2).mean(dim=dimensions).squeeze()
    if iterate_dim in spdata_median.dims:
        data_arrays = []
        for t in mean_squared_dev.coords[iterate_dim]:
            ensemble_dev = mean_squared_dev.loc[{iterate_dim: t}]
            logger.debug(ensemble_dev)
            best_iloc = int(ensemble_dev.argmin())
            logger.debug(best_iloc)
            best_ens_mem = ensemble_dev.coords[ens_dim][best_iloc]
            logger.debug('Selected {0} for {1} as best median member'.format(
                best_ens_mem.values, t.values))
            temp_array = spdata.data.loc[{
                iterate_dim: t,
                ens_dim: best_ens_mem}].expand_dims(iterate_dim)
            data_arrays.append(temp_array)
        median_run.data = xr.concat(data_arrays, dim=iterate_dim)
    else:
        ensemble_member = mean_squared_dev.argmin()
        median_run.data = spdata.data.loc[{ens_dim: ensemble_member}]
    median_run.data.coords[ens_dim] = ['median_run',]
    return median_run
