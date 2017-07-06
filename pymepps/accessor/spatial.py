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

# External modules
import xarray as xr
import numpy as np

# Internal modules
from .base import MetData
from pymepps.loader.datasets.tsdataset import TSDataset
from pymepps.loader.filehandler.netcdfhandler import cube_to_series


logger = logging.getLogger(__name__)


@xr.register_dataarray_accessor('pp')
class SpatialAccessor(MetData):
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
    """
    def __init__(self, data, grid=None):
        super().__init__(data)
        self._grid = None
        self.grid = grid

    def __str__(self):
        try:
            grid = str(self.grid)
        except TypeError:
            grid = str(None)
        name = "{0:s}({1:s})".format(self.__class__.__name__, self.data.name)
        return "{0:s}\n{1:s}\nGrid: {1:s}".format(name, '-'*len(name), grid)

    @property
    def grid(self):
        if self._grid is None:
            raise TypeError('This DataArray has no grid defined!')
        else:
            return self._grid

    @grid.setter
    def grid(self, grid):
        if grid is not None and not hasattr(grid, '_grid_dict'):
            raise TypeError('The given grid is not a valid defined grid type!')
        self._grid = grid

    def _check_data_coordinates(self, item):
        """
        Check if items grid coordinates are the same as those of the grid.

        Parameters
        ----------
        item: xarray.DataArray
            Instance to test for type and grid dimension length.

        Returns
        -------
        item: xarray.DataArray
            The checked item.

        Raises
        ------
        TypeError:
            The grid is not set.
        ValueError:
            The given item has not the same last coordinates as the grid.
        """
        item_grid_dims = [item[dim] for dim in item.dims[-self.grid.len_coords:]]
        grid_coords = self.grid._construct_dim()
        coords_equal = all([np.array_equal(item_grid_dims[k], grid_coords[k])
                            for k in range(self.grid.len_coords)])
        if not coords_equal:
            raise ValueError('The item {0:s} has not the right last dimensions.'
                             'They need to be the same as the grid!')
        return item

    def merge(self, *items):
        """
        The merge routine could be used to merge this SpatialData instance with
        other instances. The merge creates a new merge dimension, name after the
        variable names. The grid of this instance is used as merged grid.

        Parameters
        ----------
        items : xarray.DataArray
            The items are merged with this xarray.DataArray instance. The grid
            dimensions have to be same as the grid.

        Returns
        -------
        merged_array : xarray.DataArray
            The DataArray instance with the merged data.
        """
        update_data = [self._check_data_coordinates(self.data), ]
        update_data += [self._check_data_coordinates(item) for item in items]
        dataset_data = [
            item.to_dataset('variable') if 'variable' in item.coords else item
            for item in update_data]
        merged_data = xr.merge(dataset_data).to_array(name='merged_array')
        merged_data.pp.grid = self.grid
        return merged_data

    def update(self, *items):
        """
        The update routine could be used to update the DataArray, based on other
        DataArrays. There are some assumptions done:
            1. The used data to update this DataArray instance has the same
            grid coordinates as this instance.
            2. Beginning from the left the given items are used to update the 
            data. Such that intersection problems are resolved in favor of the
            newest data.

        Parameters
        ----------
        items : xarray.DataArray
            The items are merged with this xarray.DataArray instance. The grid
            dimensions have to be same as the grid.

        Returns
        -------
        merged_array : xarray.DataArray
            The DataArray instance with the updated data.
        """
        update_data = [self._check_data_coordinates(self.data), ]
        update_data += [self._check_data_coordinates(item) for item in items]
        stack_dims = [dim for dim in self.data.dims
                      if dim not in self.grid.get_coord_names()]
        stacked_data = [d.stack(merge=stack_dims) for d in update_data]
        try:
            concated_array = xr.concat(stacked_data, dim='merge')
        except (ValueError, TypeError) as e:
            raise e.__class__('The concatenation doesn\'t working, for '
                              'plase see above for the reasons!')
        resolving_indexes = ~concated_array.indexes['merge'].duplicated(
            keep='last')
        resolved_array = concated_array[..., resolving_indexes]
        unstacked_array = resolved_array.unstack('merge')
        updated_array = unstacked_array.transpose(*self.data.dims)
        updated_array.pp.grid = self.grid
        return updated_array

    def set_grid_coordinates(self):
        """
        Set the coordinates of the grid to the DataArray.

        Returns
        -------
        gridded_array : xarray.DataArray
            The DataArray with the grid coordinates.
        """
        data = self._check_data_coordinates(self.data)
        new_coordinates = self.grid.get_coords()
        data_grid_dims = data.dims[-self.grid.len_coords:]
        dims_to_swap = {
            old: new for old, new in zip(data_grid_dims,
                                         self.grid.get_coord_names())}
        added_coords_array = data.assign_coords(new_coordinates)
        gridded_array = added_coords_array.swap_dims(dims_to_swap)
        for dim in data_grid_dims:
            del gridded_array[dim]
        return gridded_array

    def merge_analysis_timedelta(self, analysis_axis='runtime',
                                 timedelta_axis='validtime'):
        """
        The analysis time axis will be merged with the valid time axis,
        which should be given as timedelta. The merged time coordinate is called
        time and will be the first coordinate .

        Parameters
        ----------
        analysis_axis : str, optional
            The analysis time axis name. This axis will be used as basis for the
            valid time. Default is runtime.
        timedelta_axis : str, optional
            The time delta axis name. This axis should contain the difference to
            the analysis time.

        Returns
        -------
        merged_array : xarray.DataArray
            The DataArray with the merged analysis and timedelta coordinate.
        """
        stacked_data = self.data.stack(
            time=[analysis_axis, timedelta_axis])
        stacked_data.coords['time'] = [
            val[0]+val[1] for val in stacked_data.time.values]
        dims_to_transpose = ['time', ] + list(stacked_data.dims[:-1])
        merged_data = stacked_data.transpose(*dims_to_transpose)
        return merged_data

    def to_pandas(self, lonlat=None):
        """
        Transform the DataArray to Pandas based on given coordinates. If
        coordinates are given this method selects the nearest neighbour grid
        point to this coordinates. The data is flatten to a 2d-DataFrame with
        the time as row axis.

        Parameters
        ----------
        lonlat : tuple(float, float) or None
            The nearest grid point to this coordinates (longitude, latitude) is
            used to generate the pandas data. If lonlat is None no
            coordinates will be selected and the data is flatten. If the
            horizontal grid coordinates are not a single point it is recommended
            to set lonlat.

        Returns
        -------
        extracted_data : pandas.Series or pandas.DataFrame
            The extracted pandas data. The data is based on either a
            Series (1 Column) or Dataframe (multiple column) depending on the
            dimensions.
        """
        if isinstance(lonlat, tuple) and len(lonlat) == 2:
            extracted_data = self.grid.get_nearest_point(data=self.data,
                                                         coord=reversed(lonlat))
            dims_wo_grid = [dim for dim in self.data.dims
                            if dim not in self.grid.get_coord_names()]
            coords = {dim: self.data.coords[dim] for dim in dims_wo_grid}
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
    #
    # def remapnn(self, new_grid, inplace=False):
    #     """
    #     Remap the horizontal grid with the nearest neighbour approach to a given
    #     new grid.
    #
    #     Parameters
    #     ----------
    #     new_grid : Child instance of Grid
    #         The data is remapped to this grid.
    #
    #     inplace: bool, optional
    #         If the new data should be replacing the data of this SpatialData
    #         instance or if the instance should be copied. Default is False.
    #
    #     Returns
    #     -------
    #     spdata: SpatialData
    #         The SpatialData instance with the replaced grid.
    #     """
    #     if inplace:
    #         spdata = self
    #     else:
    #         spdata = self.copy()
    #     new_data = spdata.grid.remapnn(new_grid, spdata.data.values)
    #     spdata.set_grid_coordinates(new_data, new_grid)
    #     return spdata
    #
    # def remapbil(self, new_grid, inplace=False):
    #     """
    #     Remap the horizontal grid with a bilinear approach to a given new grid.
    #
    #     Parameters
    #     ----------
    #     new_grid : Child instance of Grid
    #         The data is remapped to this grid.
    #
    #     inplace: bool, optional
    #         If the new data should be replacing the data of this SpatialData
    #         instance or if the instance should be copied. Default is False.
    #
    #     Returns
    #     -------
    #     spdata: SpatialData
    #         The SpatialData instance with the replaced grid.
    #     """
    #     if inplace:
    #         spdata = self
    #     else:
    #         spdata = self.copy()
    #     new_data = spdata.grid.remapbil(new_grid, spdata.data.values)
    #     spdata.set_grid_coordinates(new_data, new_grid)
    #     return spdata
    #
    # def sellonlatbox(self, lonlatbox, inplace=False):
    #     """
    #     The data is sliced with the given lonlatbox. A new grid is created based
    #     on the sliced coordinates.
    #
    #     Parameters
    #     ----------
    #     lonlatbox : tuple(float)
    #         The longitude and latitude box with four entries as degree. The
    #         entries are handled in the following way:
    #             (left/west, top/north, right/east, bottom/south)
    #
    #     inplace: bool, optional
    #         If the new data should be replacing the data of this SpatialData
    #         instance or if the instance should be copied. Default is False.
    #
    #     Returns
    #     -------
    #     spdata: SpatialData
    #         The sliced SpatialData instance with the replaced grid.
    #     """
    #     if inplace:
    #         spdata = self
    #     else:
    #         spdata = self.copy()
    #     new_data, new_grid = spdata.grid.lonlatbox(spdata.data.values,
    #                                                lonlatbox)
    #     spdata.set_grid_coordinates(new_grid, new_data)
    #     return spdata
    #
    # def save(self, path):
    #     """
    #     To save the SpatialData a copy of this instance is created and the
    #     grid dict of the grid is added to the SpatialData attributes. Then the
    #     instance is saved as NetCDF file.
    #
    #     Parameters
    #     ----------
    #     path: str
    #         The path where the netcdf file should be saved.
    #     """
    #     save_array = self.data.copy()
    #     grid_attr = {'grid_{0:s}'.format(k): self.grid._grid_dict[k]
    #                  for k in self.grid._grid_dict}
    #     save_array.attrs.update(grid_attr)
    #     save_array.to_netcdf(path)
    #
    # @staticmethod
    # def load(path):
    #     """
    #     Load a SpatialData instance from a given path. The path is loaded as
    #     SpatialDataset. A correct saved SpatialData instance will have only one
    #     variable within the NetCDF file. So the first variable will be returned
    #     as newly constructed SpatialData instance.
    #
    #     Parameters
    #     ----------
    #     path: str
    #         The path to the saved SpatialData instance.
    #
    #     Returns
    #     -------
    #     spdata: SpatialData
    #         The loaded SpatialData instance.
    #     """
    #     spatial_ds = pymepps.loader.open_model_dataset(path, 'nc')
    #     variable = spatial_ds.var_names[0]
    #     spdata = spatial_ds.select(variable)
    #     return spdata
