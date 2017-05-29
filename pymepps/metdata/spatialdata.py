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
from collections import OrderedDict

# External modules
import xarray as xr
import pandas as pd
import numpy as np

# Internal modules
from .metdata import MetData
from .tsdataset import TSDataset
from pymepps.metfile.netcdfhandler import cube_to_series
import pymepps.plot
import pymepps.loader


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
    data : xarray.DataArray or None
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
    def __init__(self, data, grid=None, data_origin=None):
        super().__init__(data, data_origin)
        self._grid = None
        self.grid = grid

    def __str__(self):
        dims = str(self.data.dims)
        coords = str(self.data.coords)
        grid = str(self.grid)
        name = "{0:s}({1:s})".format(self.__class__.__name__, self.data.name)
        return "{0:s}\n{1:s}\ndims: {2:s}\ncoords:{3:s}\n" \
               "grid:{4:s}".format(name, '-'*len(name), dims, coords, grid)

    def __getitem__(self, sliced):
        metdata = self.copy()
        metdata.data = metdata.data[sliced]
        return metdata

    def append(self, item, inplace=False):
        if inplace:
            self.data.append(item)
        else:
            metdata = self.copy()
            metdata.data.append(item)
            return metdata

    def remove(self, item, inplace=False):
        if inplace:
            self.data.remove(item)
        else:
            metdata = self.copy()
            metdata.data.remove(item)
            return metdata

    def update(self, *items):
        """
        The update routine could be used to update the data of this SpatialData,
        based on either xarray.DataArrays or other SpatialData. There are some 
        assumptions done:
            1. The used data to update this SpatialData instance has the same 
            grid and dimension variables as this instance.
            2. Beginning from the left the given items are used to update the 
            data. Such that intersection problems are resolved in favor of the
            newest data.

        Parameters
        ----------
        items: xarray.DataArray or SpatialData
            The items are used to update the data of this SpatialData instance.
            The grid has to be same as this SpatialData instance.
        """
        update_data = [self.data.copy(), ]
        for item in items:
            self._test_item_da_sd(item)
            if isinstance(item, SpatialData):
                update_data.append(item.data)
            else:
                update_data.append(item)
        stack_dims = [dim for dim in self.data.dims
                      if dim not in self.grid.get_coord_names()]
        stacked_data = [d.stack(merge=stack_dims) for d in update_data]
        try:
            concated_data = xr.concat(stacked_data, dim='merge')
        except ValueError:
            raise ValueError('The given items have not the same dimension '
                             'variables as the original data!')
        resolving_indexes = ~concated_data.indexes['merge'].duplicated(
            keep='last')
        resolved_data = concated_data[..., resolving_indexes]
        unstacked_data = resolved_data.unstack('merge')
        self.data = unstacked_data.transpose(*self.data.dims)
        logger.info('Updated the data')

    def _test_item_da_sd(self, item):
        """
        Test if the given item is either a xarray.DataArray or a SpatialData 
        instance and test if the grid of the given instance has the same
        dimension lengths as the grid of this instance, assuming that the same 
        grid dimension lengths are belonging to the same grid.

        Parameters
        ----------
        item: xarray.DataArray or SpatialData
            Instance to test for type and grid dimension length.

        Raises
        ------
        TypeError:
            The given item is not either a xarray.DataArray or a SpatialData 
            instance.
        ValueError:
            The given item has not the same grid dimensions as the Data of this
            SpatialData instance.
        """
        if not isinstance(item, (xr.DataArray, SpatialData)):
            logger.info(type(item))
            raise TypeError('The given item needs to be either a'
                            'xarray.DataArray or a SpatialData instance!')
        len_grid_coordinates = self.grid.len_coords
        item_grid_length = item.values.shape[-len_grid_coordinates:]
        data_grid_length = np.array(self.grid._construct_dim).shape
        grid_lengths_equal = all(
            (i==g for i, g in zip(item_grid_length, data_grid_length)))
        if not grid_lengths_equal:
            raise ValueError( 'The grid of the given item has not the same grid'
                              'dimension length as the original grid of this'
                              'SpatialData instance!')

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
        for dim in self.data.dims[:-grid.len_coords]:
            new_coords[dim] = self.data[dim]
        new_darray = xr.DataArray(
            data, name=self.data.name, coords=new_coords,
            dims=list(self.data.dims[:-grid.len_coords]) + \
                 list(grid.get_coord_names()),
            attrs=self.data.attrs
        )
        self.data = new_darray
        self.grid = grid
        return self

    def merge_analysis_timedelta(self, analysis_axis='runtime',
                                 timedelta_axis='time', inplace=False):
        """
        The analysis time axis will be merged with the valid time axis, which
        should be given as timedelta. The merged time axis is called validtime
        and will be the first data axis.

        Parameters
        ----------
        analysis_axis: str, optional
            The analysis time axis name. This axis will be used as basis for the
            valid time. Default is runtime.
        timedelta_axis: str, optional
            The time delta axis name. This axis should contain the difference to
            the analysis time.
        inplace: bool, optional
            If the new data should be replacing the data of this SpatialData
            instance or if the instance should be copied. Default is False.

        Returns
        -------
        spdata: SpatialData
            The SpatialData instance with the replaced axis.
        """
        if inplace:
            spdata = self
        else:
            spdata = self.copy()
        stacked_data = spdata.data.stack(
            validtime=[analysis_axis, timedelta_axis])
        stacked_data.coords['validtime'] = [
            val[0]+val[1] for val in stacked_data.validtime.values]
        dims_to_transpose = ['validtime',] + list(stacked_data.dims[:-1])
        spdata.data = stacked_data.transpose(*dims_to_transpose)
        return spdata

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
        series_data = cube_to_series(cube.squeeze(), self.data.name)
        ts_ds = TSDataset(None, data_origin=self, lonlat=lonlat)
        extracted_data = ts_ds.data_merge(series_data, self.data.name)
        return extracted_data

    def remapnn(self, new_grid, inplace=False):
        """
        Remap the horizontal grid with the nearest neighbour approach to a given
        new grid.

        Parameters
        ----------
        new_grid : Child instance of Grid
            The data is remapped to this grid.
        
        inplace: bool, optional
            If the new data should be replacing the data of this SpatialData
            instance or if the instance should be copied. Default is False.

        Returns
        -------
        spdata: SpatialData
            The SpatialData instance with the replaced grid.
        """
        if inplace:
            spdata = self
        else:
            spdata = self.copy()
        new_data = spdata.grid.remapnn(spdata.data.values, new_grid)
        spdata.set_data_coordinates(new_data, new_grid)
        return spdata

    def remapbil(self, new_grid, inplace=False):
        """
        Remap the horizontal grid with a bilinear approach to a given new grid.

        Parameters
        ----------
        new_grid : Child instance of Grid
            The data is remapped to this grid.
        
        inplace: bool, optional
            If the new data should be replacing the data of this SpatialData
            instance or if the instance should be copied. Default is False.

        Returns
        -------
        spdata: SpatialData
            The SpatialData instance with the replaced grid.
        """
        if inplace:
            spdata = self
        else:
            spdata = self.copy()
        new_data = spdata.grid.remapbil(spdata.data.values, new_grid)
        spdata.set_data_coordinates(new_data, new_grid)
        return spdata

    def plot(self, method='contourf'):
        plot = pymepps.plot.SpatialPlot()
        plot.add_subplot()
        getattr(plot, method)(self.data)
        plot.suptitle('{0:s} plot of {1:s}'.format(method, self.data.variable))
        return plot

    def _wrapped_data_function(self, key):
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
        data_function = getattr(self.data, key)
        if hasattr(data_function, '__call__'):
            def wrapped_func(*args, **kwargs):
                result = data_function(*args, **kwargs)
                try:
                    new_spdata = SpatialData(
                        result,
                        grid=self.grid,
                        data_origin=self.data_origin
                    )
                    new_spdata.set_data_coordinates()
                    return new_spdata
                except ValueError:
                    return result
            wrapped_func.__doc__ = data_function.__doc__
            return wrapped_func
        else:
            return data_function

    def save(self, path):
        """
        To save the SpatialData a copy of this instance is created and the 
        grid dict of the grid is added to the SpatialData attributes. Then the 
        instance is saved as NetCDF file.

        Parameters
        ----------
        path: str
            The path where the netcdf file should be saved.
        """
        save_array = self.data.copy()
        save_array.attrs.update(self.grid._grid_dict)
        save_array.to_netcdf(path)

    @staticmethod
    def load(path):
        """
        Load a SpatialData instance from a given path. The path is loaded as 
        SpatialDataset. A correct saved SpatialData instance will have only one 
        variable within the NetCDF file. So the first variable will be returned
        as newly constructed SpatialData instance.

        Parameters
        ----------
        path: str
            The path to the saved SpatialData instance.

        Returns
        -------
        spdata: SpatialData
            The loaded SpatialData instance.
        """
        spatial_ds = pymepps.loader.open_model_dataset(path, 'nc')
        variable = spatial_ds.var_names[0]
        spdata = spatial_ds.select(variable)
        return spdata
