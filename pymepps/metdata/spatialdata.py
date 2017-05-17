#!/bin/env python
# -*- coding: utf-8 -*-
# """
# Created on 09.12.16
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
import xarray as xr

# Internal modules
from .metdata import MetData
from .tsdataset import TSDataset
from pymepps.metfile.netcdfhandler import cube_to_series
import pymepps.plot

__math_operators = ['__add__', '__sub__']

logger = logging.getLogger(__name__)


class SpatialData(MetData):
    """
    SpatialData contains spatial based data structures. This class is the
    standard data type for file types like netCDF or grib. It's prepared
    for the output of numerical and statistical weather models.
    Array based data is always saved to netcdf via xarray.

    Attributes
    ----------
    data_base : xarray.DataArray or None
        The data of this grid based data structure.
    grid : Child instance of Grid or None
        The corresponding grid of this SpatialData instance. This grid is 
        used to interpolate/remap the data and to select the nearest grid
        point to a given longitude/latitude pair. The grid is also used to 
        get a basemap instance to determine the grid boundaries for plotting
        purpose.
    data_origin : object of pymepps or None, optional
        The origin of this data. This could be a model run, a station, a
        database or something else. Default is None.
    """
    def __init__(self, data_base, grid=None, data_origin=None):
        super().__init__(data_base, data_origin)
        self._grid = None
        self.grid = grid

    def set_data_coordinates(self, data=None, grid=None):
        """
        Set new data and coordinates based on given np.array and and grid.

        Parameters
        ----------
        data : np.ndarray or None, optional
            The data of this instance is set to this data. If this is None the 
            data is set to the values of instance's data. The data needs the 
            same number of dimensions as instance's data. The length of the 
            coordinates needs also to be the same as instance's coordinates
            except the horizontal grid coordinates. The length of the horizontal
            grid coordinates needs to be the same as specified in the grid.
            Default is None.
        grid : Child instance of Grid or None, optional
            The grid of this instance is set to this grid. If this is None
            instance's grid is used. The last two dimensions of instance's data
            is set according to to the grid. Default is None.

        Returns
        -------
        self
            This spatial data instance with the set data and coordinates.
        """
        if data is None:
            data = self.data.values
        if grid is None:
            grid = self.grid
        new_coords = grid.get_coords()
        for dim in self.data.dims[:-2]:
            new_coords[dim] = self.data[dim]
        new_darray = xr.DataArray(
            data, coords=new_coords,
            dims=list(self.data.dims[:-2])+list(grid.get_coord_names()),
            attrs=self.data.attrs
        )
        self.data = new_darray
        self.grid = grid
        return self

    @property
    def grid(self):
        if self._grid is None:
            raise ValueError('This spatial data has no grid defined!')
        else:
            return self._grid

    @grid.setter
    def grid(self, grid):
        if grid is not None and not hasattr(grid, '_grid_dict'):
            raise TypeError('The given grid is not a valid defined grid type!')
        self._grid = grid

    def to_tsdata(self, lonlat=None):
        """
        Transform the SpatialData to a TSData based on given coordinates. If
        coordinates are given this method selects the nearest neighbour grid 
        point to this coordinates. The data is flatten to a 2d-Array with the
        time as row axis.

        Parameters
        ----------
        lonlat : tuple(float, float) or None
            The nearest grid point to this coordinates (longitude, latitude) is 
            used to generate the time series data. If lonlat is None no
            coordinates will be selected and the data is flatten. If the
            horizontal grid coordiantes are not a single point it is recommended
            to set lonlat.

        Returns
        -------
        extracted_data : TSData
            The extracted TSData instance. The data is based on either a pandas
            Series or Dataframe depending on the dimensions of this SpatialData.
        """
        if isinstance(lonlat, tuple) and len(lonlat)==2:
            extracted_data = self.grid.get_nearest_point(
                data=self.data.values, coord=reversed(lonlat))
            logger.debug(extracted_data)
            dims_wo_grid = [dim for dim in self.data.dims
                            if dim not in self.grid.get_coord_names()]
            logger.debug(dims_wo_grid)
            coords = {dim: self.data.coords[dim] for dim in dims_wo_grid}
            logger.debug(coords)
            cube = xr.DataArray(
                extracted_data,
                coords=coords,
                dims=dims_wo_grid,
            )
        else:
            cube = self.data
        series_data = cube_to_series(cube, self.data.name)
        ts_ds = TSDataset(None, data_origin=self, lonlat=lonlat)
        extracted_data = ts_ds.data_merge(series_data, self.data.name)
        return extracted_data

    def remapnn(self, new_grid):
        """
        Remap the horizontal grid with the nearest neighbour approach to a given
        new grid.

        Parameters
        ----------
        new_grid : Child instance of Grid
            The data is remapped to this grid.

        Returns
        -------
        self
            This SpatialData instance.
        """
        new_data = self.grid.remapnn(self.data.values, new_grid)
        self.set_data_coordinates(new_data, new_grid)
        return self

    def remapbil(self, new_grid):
        """
        Remap the horizontal grid with a bilinear approach to a given new grid.

        Parameters
        ----------
        new_grid : Child instance of Grid
            The data is remapped to this grid.

        Returns
        -------
        self
            This SpatialData instance.
        """
        new_data = self.grid.remapbil(self.data.values, new_grid)
        self.set_data_coordinates(new_data, new_grid)
        return self

    def plot(self, method='contourf'):
        plot = pymepps.plot.SpatialPlot()
        plot.add_subplot()
        getattr(plot, method)(self.data)
        plot.suptitle('{0:s} plot of {1:s}'.format(method, self.data.variable))
        return plot

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
            if isinstance(result, xr.DataArray):
                return self.__class__(result, self.grid, self.data_origin)
            else:
                return result
        return wrapped_func

    def save(self, path):
        save_array = self.data.copy()
        save_array.attrs['grid_dict'] = self.grid._grid_dict
        save_array.attrs['data_origin'] = self.data_origin
        save_array.to_netcdf(path)
