#!/bin/env python
# -*- coding: utf-8 -*-
# """
# Created on 14.12.16
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

# External modules
import xarray as xr
import numpy as np

# Internal modules
from .filehandler import FileHandler


logger = logging.getLogger(__name__)


def cube_to_series(cube, var_name):
    cleaned_dims = list(cube.dims)
    logger.debug(cleaned_dims)
    if 'index' in cleaned_dims:
        cleaned_dims.remove('index')
    elif 'time' in cleaned_dims:
        cleaned_dims.remove('time')
    elif 'validtime' in cleaned_dims:
        cleaned_dims.remove('validtime')
    if cleaned_dims:
        stacked = cube.stack(col=cleaned_dims)
        data = stacked.to_pandas()
        #data = [pd_stacked.ix[:,col] for col in pd_stacked.columns]
    else:
        data = cube.to_series()
        data.name = var_name
    return data


class NetCDFHandler(FileHandler):
    def _get_varnames(self):
        var_names = list(self.ds.data_vars)
        return var_names

    def is_type(self):
        try:
            self.open()
            self.close()
            return True
        except OSError:
            return False

    def open(self):
        if self.ds is None:
            self.ds = xr.open_dataset(self.file, engine='netcdf4')
        return self

    def close(self):
        if self.ds is not None:
            self.ds.close()
        self.ds = None

    @property
    def lon_lat(self):
        attrs = {}
        try:
            attrs['latitude'] = float(self.ds.lat.values)
        except TypeError or KeyError:
            pass
        try:
            attrs['longitude'] = float(self.ds.lon.values)
        except TypeError or KeyError:
            pass
        try:
            attrs['altitude'] = float(self.ds.zsl.values)
        except TypeError or KeyError:
            pass
        return attrs

    def load_cube(self, var_name):
        """
        Method to load a variable from the netcdf file and return it as
        xr.DataArray.

        Parameters
        ----------
        var_name : str
            The variable name, which should be extracted.

        Returns
        -------
        variable : xr.DataArray
            The DataArray of the variable.
        """
        logger.debug('Get {0:s} from {1:s}'.format(var_name, self.file))
        variable = self.ds[var_name]
        if hasattr(variable, '_FillValue'):
            variable.values[variable.values == variable._FillValue] = np.nan
        elif hasattr(variable, 'missing_value'):
            variable.values[variable.values == variable.missing_value] = np.nan
        else:
            variable.values[variable.values==9.96921e+36] = np.nan
        return variable

    def get_timeseries(self, var_name, **kwargs):
        """
        Method to get the time series from a NetCDF file. This is designed for
        measurement site data in netcdf format. At the moment this method is
        only tested for Wettermast Hamburg data!

        Parameters
        ----------
        var_name : str
            The variable name, which should be extracted.

        Returns
        -------
        data : dict with pandas series
            The selected variable is extracted as dict with pandas series as
            values.
        """
        cube = self.load_cube(var_name).load()
        data = cube_to_series(cube, var_name)
        return data

    def _normalize_coordinates(self, cube):
        """
        Normalize the coordinates of a given cube. The non-grid coordinates are
        renamed to a common name. If there is a valid runtime coordinate, then
        the validtime coordinate is converted to timedelta.
        """
        rename_dim = ['runtime', 'ensemble', 'validtime', 'height']
        cube_dims = cube.dims
        if cube_dims[0] == 'variable':
            cube_dims = cube_dims[1:]
        rename_coords = {cube_dims[k]: rename
                      for k, rename in enumerate(rename_dim)}
        cube = cube.rename(rename_coords)
        if np.issubdtype(cube['validtime'].values.dtype, np.datetime64) and \
                np.issubdtype(cube['runtime'].values.dtype, np.datetime64):
            cube['validtime'] = cube['validtime']-cube['runtime'].values
        return cube

    def get_messages(self, var_name, **kwargs):
        """
        Method to imitate the message-like behaviour of grib files.

        Parameters
        ----------
        var_name : str
            The variable name, which should be extracted.
        runtime : np.datetime64, optional
            If the dataset has no runtime this runtime is used. If the runtime
            is not set, the  runtime will be inferred from file name.
        ensemble : int or str, optional
            If the dataset has no ensemble information this ensemble is used. If
            the ensemble is not set, the ensemble will be inferred from file
            name.
        sliced_coords : tuple(slice), optional
            If the cube should be sliced before it is loaded. This is helpful
            by large opendap requests. These slice will be used from the behind.
            So (slice(1,2,1), slice(3,5,1)) means [..., 1:2, 3:5]. If it is not
            set all data is used. T

        Returns
        -------
        data : list of xr.DataArray
            The list with the message-wise data as DataArray. The DataArray
            have six coordinates (analysis, ensemble, time, level, y, x).
            The shape of DataArray are normally (1,1,1,1,y_size,x_size).
        """
        cube = self.load_cube(var_name)
        if 'sliced_coords' in kwargs:
            cube = cube[(...,)+kwargs['sliced_coords']]
        logger.debug('Loaded the cube')
        cube.attrs.update(self.ds.attrs)
        logger.debug('Updated the attributes')
        cube = self._get_missing_coordinates(cube, **kwargs)
        cube = self._normalize_coordinates(cube)
        cube = cube.load()
        return cube
