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
import re
import datetime

# External modules
import xarray as xr
import numpy as np

# Internal modules
import pymepps
from .base import MetData
from pymepps.grid.builder import GridBuilder
from pymepps.loader.datasets.tsdataset import TSDataset
from pymepps.loader.filehandler.netcdfhandler import cube_to_series


logger = logging.getLogger(__name__)


@xr.register_dataarray_accessor('pp')
class SpatialAccessor(MetData):
    """
    The SpatialAccessor extends a xarray.DataArray for post-processing of
    meteorological numerical weather model data. The SpatialAccessor works
    mostly with grid and gridded data.
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
        """
        The corresponding grid of this xarray.DataArray instance. This grid is
        used to interpolate/remap the data and to select the nearest grid
        point to a given longitude/latitude pair.
        """
        if self._grid is None:
            raise TypeError('This DataArray has no grid defined!')
        else:
            return self._grid

    @grid.setter
    def grid(self, grid):
        if grid is not None and not hasattr(grid, '_grid_dict'):
            raise TypeError('The given grid is not a valid defined grid type!')
        self._grid = grid

    def set_grid(self, grid=None):
        """
        Set the grid to the given grid and set the grid coordinates.

        Parameters
        ----------
        grid : Grid or None, optional
            This grid is used to set the grid and the grid coordinates of the
            returned array. If this is None, the grid of this DataArray instance
            is used. Default is None.

        Returns
        -------
        gridded_array : xarray.DataArray
            The DataArray with the grid coordinates and the grid.

        Raises
        ------
        ValueError
            A ValueError is raised if the grid of this instance is used and not
            grid set.
        """
        if grid is None and self._grid is not None:
            grid = self.grid
        elif grid is None:
            raise ValueError('The grid of this DataArray is used and not set!')
        coord_names = grid.get_coord_names()
        rename_dict = {new: old for new, old in zip(
            self.data.dims[-grid.len_coords:], coord_names,)}
        gridded_array = self.data.rename(rename_dict)
        gridded_array.pp.grid = grid
        gridded_array = gridded_array.pp.check_data_coordinates(gridded_array)
        new_coordinates = grid.get_coords()
        for coord in coord_names:
            gridded_array[coord] = new_coordinates[coord]
        return gridded_array

    def check_data_coordinates(self, item):
        """
        Check if items grid coordinates shape is the same as those of the grid.

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
        item_grid_shape = item.shape[-self.grid.len_coords:]
        coords_equal = all(
            [np.equal(item, grid) for item, grid
             in zip(item_grid_shape, self.grid.shape)])
        if not coords_equal:
            raise ValueError('The item {0:s} has not the right last dimensions.'
                             'They need to be the same as the grid!')
        return item

    def normalize_coords(self, runtime=None, ensemble='det', validtime=None,
                         height=None):
        """
        Normalize the coordinates of the DataArray. The number, order and names
        of the coordinates are normalized. The number of coordinates will be
        four to six, depending if the DataArray is a merged multi-variable
        DataArray and the number of grid coordinates. The values of the added
        coordinates is set to the given values or will be None as filling value.
        The order and name of the DataArray will be:

        - (variable) (Only if the DataArray is a multi-variable DataArray.
          This is the variable name)
        - runtime (The analysis time of the model. The model is started at this
          time. The runtime is np.datetime64 as type)
        - ensemble (The ensemble member of the model.)
        - validtime (The lead time of the model. The model is valid for this
          times. The validtime timedelta to the runtime.)
        - height (The height information of the model.)
        - first grid coordinate
        - (second grid coordinate) (Only if the grid is not an unstructured
          grid)

        Parameters
        ----------
        runtime : datetime.datetime, np.datetime64  or None, optional
            The runtime of the model. The runtime will be converted to
            np.datetime64[ns] if it is not already this type. Default is None.
        ensemble : int or str, optional
            The ensemble member of the model. An integer is indicating the
            member number, with zero as control run. Default is 'det'.
        validtime : datetime.datetime, np.datetiime64, np.timedelta or None,
                optional
            The validtime of the model. The validtime is converted to
            np.timedelta. Default is None.
        height : int, str or None, optional
            The height of the model. Default is None.

        Returns
        -------
        normalized_array : xr.DataArray
            The DataArray with normalized coordinates.
        """
        arg_dict = locals()
        coord_dict = OrderedDict(
            height=dict(
                approx=['height', 'surf', 'sig', 'lev'],
                exact=['height', ]
            ),
            validtime=dict(
                approx=['lead', ],
                exact=['validtime', 'time']
            ),
            ensemble=dict(
                approx=['ens', 'mem', 'num'],
                exact=['ensemble', ]
            ),
            runtime=dict(
                approx=['ana', 'ref', 'run'],
                exact=['runtime']
            )
        )
        normalized_array = self.data
        for key in coord_dict.keys():
            coord_name = self._get_coord_name(coord_dict[key])
            if coord_name is None:
                normalized_array = self._create_coord(coord=key,
                                                      value=arg_dict[key],
                                                      data=normalized_array)
            else:
                normalized_array = self._rename_coord(orig=coord_name, to=key,
                                                      data=normalized_array)
        normalized_array = self._get_normalized_order(normalized_array)
        normalized_array = self._transform_datetime(normalized_array)
        normalized_array = self._validtime_to_timedelta(normalized_array)
        return normalized_array

    def _get_coord_name(self, variants):
        """
        Check if the coordinate name variants is any dimensions within the
        DataArray.

        Parameters
        ----------
        variants : dict(str, list(str)) or list(str)
            These variants are checked within the dimensions of the DataArray.
            If variants is a dict, it needs exact and approx as key with a
            sublist of variants. The exact list is used to check the exact
            dimension name. The approx list is used to check if the variant is
            within the name of a dimension. If variants is a list of strings
            the list values are used for exact matching.

        Returns
        -------
        str or None
            The matched dimension is returned. If the return value is None, no
            matching dimension was found.
        """
        if isinstance(variants, (tuple, list)):
            variants = dict(exact=variants, approx=[])
        data_dims = [re.sub('[^a-zA-Z]+', '', d) for d in self.data.dims]
        for k, dim in enumerate(data_dims):
            for variant in variants['exact']:
                if variant == dim:
                    return self.data.dims[k]
            for variant in variants['approx']:
                if variant in dim:
                    return self.data.dims[k]
        return None

    @staticmethod
    def _get_normalized_order(data):
        if 'variable' in data.dims:
            normalized_order = ['variable']
        else:
            normalized_order = []
        normalized_order.extend(['runtime', 'ensemble', 'validtime', 'height'])
        normalized_order.extend([
            dim for dim in data.dims if dim not in normalized_order
        ])
        normalized_array = data.transpose(*normalized_order)
        return normalized_array

    @staticmethod
    def _transform_datetime(data):
        """
        Transform the datetime dimensions of the given data to
        np.datetime64[ns].

        Parameters
        ----------
        data : xr.DataArray
            The dimensions of this DataArray are used for the transformation.

        Returns
        -------
        transformed_data : xr.DataArray
            The DataArray with the transformed time coordinates.
        """
        transformed_data = data.copy()
        dims_to_transform = [
            dim for dim in data.dims
            if isinstance(data[dim].values[0],
                          (datetime.datetime, np.datetime64))]
        for dim in dims_to_transform:
            transformed_data[dim] = transformed_data[dim].astype(
                'datetime64[ns]')
        return transformed_data

    @staticmethod
    def _create_coord(data, coord, value=None,):
        """
        Create a coordinate within the given DataArray with given value.

        Parameters
        ----------
        data : xr.DataArray
            The DataArray is used to create and add the coordinate.
        coord : str
            The name of the coordinate.
        value : obj or None, optional
            The value of the coordinate. None is used as filling value. Default
            is None.

        Returns
        -------
        coordinated_array : xr.DataArray
            The DataArray with the added coordinate.

        Raises
        ------
        ValueError
            A coordinate with the same name already exists within the
            coordinates dict or the dimension list of the DataArray.
        """
        coordinated_array = data.expand_dims(coord)
        coordinated_array[coord] = np.array((value,))
        return coordinated_array

    @staticmethod
    def _rename_coord(data, orig, to):
        """
        Rename a given coordinate to a new name.

        Parameters
        ----------
        data : xr.DataArray
            The DataArray is used to rename the coordinate.
        orig : str
            The name of the original coordinate. The coordinate needs to be
            within the DataArray coordinates.
        to : str
            The coordinate is renamed to this name.

        Returns
        -------
        renamed_array : xr.DataArray
            The DataArray with the renamed coordinate.
        """
        renamed_array = data.rename({orig: to})
        return renamed_array

    @staticmethod
    def _validtime_to_timedelta(data, validtime='validtime', runtime='runtime'):
        """
        Transform the validtime coordinate from a np.datetime64 coordinate to a
        np.timedelta coordinate if also the runtime coordinate is a
        np.datetime64 coordinate. The timedelta is create with
        :math:`validtime-runtime`.

        Parameters
        ----------
        data : xr.DataArray
            The DataArray is used to transform the validtime coordinate.
        validtime : str, optional
            Name of the validtime coordinate. Default is validtime.
        runtime : str, optional
            Name of the runtime coordinate. Default is runtime.

        Returns
        -------
        transformed_array : xr.DataArray
            The DataArray with the transformed validtime coordinate.
        """
        transformed_array = data.copy()
        runtime_values = data[runtime].values
        validtime_values = data[validtime].values
        if np.issubdtype(runtime_values.dtype, np.datetime64) and \
                np.issubdtype(validtime_values.dtype, np.datetime64):
            transformed_array[validtime] = validtime_values - runtime_values
        return transformed_array

    def merge(self, *items):
        """
        The merge routine could be used to merge this SpatialData instance with
        other instances. The merge creates a new merge dimension, named after
        the variable names. The grid of this instance is used as merged grid.

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
        update_data = [self.check_data_coordinates(self.data), ]
        update_data += [self.check_data_coordinates(item) for item in items]
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
        update_data = [self.check_data_coordinates(self.data), ]
        update_data += [self.check_data_coordinates(item) for item in items]
        stack_dims = [dim for dim in self.data.dims
                      if dim not in self.grid.get_coord_names()]
        stacked_data = [d.stack(merge=stack_dims) for d in update_data]
        try:
            concated_array = xr.concat(stacked_data, dim='merge')
        except (ValueError, TypeError) as e:
            raise e.__class__("The concatenation doesn't working, for "
                              'please see above for the reasons!')
        resolving_indexes = ~concated_array.indexes['merge'].duplicated(
            keep='last')
        resolved_array = concated_array[..., resolving_indexes]
        unstacked_array = resolved_array.unstack('merge')
        updated_array = unstacked_array.transpose(*self.data.dims)
        updated_array.pp.grid = self.grid
        return updated_array

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
        try:
            merged_data.pp.grid = self.grid
        except TypeError:
            pass
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
        if isinstance(lonlat, (list, tuple)) and len(lonlat) == 2:
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
        series_data = cube_to_series(cube, self.data.name)
        ts_ds = TSDataset(None, data_origin=self, lonlat=lonlat)
        extracted_data = ts_ds.data_merge(series_data, self.data.name)
        return extracted_data

    def remapnn(self, new_grid):
        """
        Remap the horizontal grid with a nearest neighbour approach to a given
        new grid.

        Parameters
        ----------
        new_grid : Child instance of Grid
            The data is remapped to this grid.

        Returns
        -------
        remapped_array : xarray.DataArray
            The xarray.DataArray with the replaced grid.
        """
        remapped_array = self.grid.interpolate(self.data, new_grid, order=0)
        remapped_array.pp.grid = new_grid
        return remapped_array

    def remapbil(self, new_grid):
        """
        Remap the horizontal grid with a bilinear approach to a given
        new grid.

        Parameters
        ----------
        new_grid : Child instance of Grid
            The data is remapped to this grid.

        Returns
        -------
        remapped_array : xarray.DataArray
            The xarray.DataArray with the replaced grid.
        """
        remapped_array = self.grid.interpolate(self.data, new_grid, order=1)
        remapped_array.pp.grid = new_grid
        return remapped_array

    def sellonlatbox(self, lonlatbox):
        """
        This DataArray instance is sliced by given lonlatbox. A new grid is
        created and set based on the sliced coordinates.

        Parameters
        ----------
        lonlatbox : tuple(float)
            The longitude and latitude box with four entries as degree. The
            entries are handled in the following way:
                (left/west, top/north, right/east, bottom/south)

        Returns
        -------
        sliced_array : xarray.DataArray
            The sliced data array with the new grid.

        Notes
        -----
        For some grids the new grid is based on an UnstructuredGrid, due to
        technical limitations.
        """
        sliced_array, sliced_grid = self.grid.lonlatbox(self.data, lonlatbox)
        sliced_array.pp.grid = sliced_grid
        return sliced_array

    def save(self, save_path):
        """
        Save the DataArray and the grid as attributes together. The grid
        attributes are used by the load method to recreate the grid, but it is
        also possible to load the data with the normal xarray load functions.

        Parameters
        ----------
        save_path : str
            The path where the netcdf file should be saved.
        """
        save_array = self.data.copy()
        try:
            grid_attr = {'ppgrid_{0:s}'.format(k): self.grid._grid_dict[k]
                         for k in self.grid._grid_dict}
            save_array.attrs.update(grid_attr)
        except TypeError:
            pass
        save_array.to_netcdf(save_path)

    @staticmethod
    def load(load_path):
        """
        Load a NetCDF-based previously saved xarray.DataArray instance. If the
        NetCDF file has grid attributes they will be decoded as new grid.

        Parameters
        ----------
        load_path : str
            The path to the saved xarray.DataArray instance.

        Returns
        -------
        loaded_array : xarray.DataArray
            The loaded DataArray instance. If a grid could be created it will be
            set to the DataArray instance.
        """
        loaded_array = xr.open_dataarray(load_path)
        grid_attrs = [attr for attr in loaded_array.attrs
                      if attr[:7] == 'ppgrid_']
        grid_dict = {attr[7:]: loaded_array.attrs[attr] for attr in grid_attrs}
        try:
            loaded_grid = GridBuilder(grid_dict).build_grid()
            loaded_array.pp.grid = loaded_grid
            for key in grid_attrs:
                loaded_array.attrs.pop(key, None)
        except (KeyError, ValueError):
            pass
        logger.debug(grid_attrs)
        return loaded_array
