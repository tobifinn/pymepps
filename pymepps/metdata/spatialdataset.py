#!/bin/env python
# -*- coding: utf-8 -*-
# """
# Created on 10.12.16
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
import operator
import os.path
import itertools
from functools import partial
from multiprocessing import Pool

# External modules
import numpy as np
import xarray as xr
from tqdm import tqdm

# Internal modules
from pymepps.utilities import tqdm_handler
from pymepps.grid import GridBuilder
from .cdo_inject import CDO
from .metdataset import MetDataset
from .spatialdata import SpatialData


logger = logging.getLogger(__name__)
#logger.addHandler(tqdm_handler)


class SpatialDataset(MetDataset):
    """
    SpatialDataset is a class for a pool of file handlers. Typically a
    spatial dataset combines the files of one model run, such that it is
    possible to select a variable and get a SpatialData instance. For
    memory reasons the data of a variable is only loaded if it is selected.

    Parameters
    ----------
    file_handlers : list of childs of FileHandler or None
        The spatial dataset is based on these files. The files should be
        either instances of GribHandler or NetCDFHandler. If file handlers
        is None then the dataset is used for conversion from TSData to
        SpatialData.
    grid : str or Grid or None
        The grid describes the horizontal grid of the spatial data. The grid 
        will be appended to every created SpatialData instance. If a str is
        given it will be checked if the str is a path to a cdo-conform grid
        file or a cdo-conform grid string. If this is a instance of a child 
        of Grid it is assumed that the grid is already initialized and this
        grid will be used. If this is None the Grid will be automatically 
        read from the first file handler. Default is None. 
    data_origin : optional
        The data origin. This parameter is important to trace the data
        flow. If this is None, there is no data origin and this
        dataset will be the starting point of the data flow. Default is
        None.
    processes : int, optional
        This number of processes is used to calculate time-consuming functions.
        For time-consuming functions a progress bar is shown. If the number of 
        processes is one the functions will be processed sequential. For more
        processes than one the multiprocessing module will be used.
        Default is 1.

    Methods
    -------
    select
        Method to select a variable.
    selnearest
        Method to select the nearest grid point for given coordinates.
    sellonlatbox
        Method to slice a box with the given coordinates.
    """
    def __init__(self, file_handlers, grid=None, data_origin=None, processes=1):
        super().__init__(file_handlers, data_origin, processes)
        self.grid = grid
        self._cdo = CDO(self._multiproc)

    def __getattr__(self, key):
        if self._cdo is not None:
            cdo_func = getattr(self._cdo, key)
            return partial(cdo_func, ds=self)

    def get_grid(self, var_name):
        """
        Method to get for given variable name a Grid instance. If the grid
        attribute is already a Grid instance this grid will be returned. If the 
        grid attribute is a str instance, the str will be read from file or from
        the given grid str. If the grid attribute isn't set the grid instance
        will be the grid for the variable selected with the first corresponding
        file handler and cdo.

        Parameters
        ----------
        var_name: str
            The variable name, which should be used to generate the grid.

        Returns
        -------
        grid: Instance of child of grid or None
            The returned grid. If the returned grid is None, the grid could not
            be read.
        """
        grid = None
        if isinstance(self.grid, str):
            grid = self._get_grid_from_str(self.grid)
        elif hasattr(self.grid, 'get_coords'):
            grid = self.grid
        if grid is None:
            grid = self._get_grid_from_cdo(var_name)
        return grid

    def _get_grid_from_cdo(self, var_name):
        grid = None
        file = self.variables[var_name][0].file
        try:
            grid_str = self.griddes(
                input='-selvar,{0:s} {1:s}'.format(var_name, file))
            grid = self._get_grid_from_str(grid_str)
        except AttributeError:
            logger.warning('To load the grid description with the cdos you '
                           'need to install the cdos!')
        return grid

    def _get_grid_from_str(self, grid_str):
        try:
            gf = open(grid_str, 'r')
            read_str = gf.read()
            gf.close()
        except (IOError, TypeError):
            read_str = grid_str
        try:
            grid_builder = GridBuilder(read_str)
            grid = grid_builder.build_grid()
        except KeyError or ValueError:
            grid = None
        return grid

    def _get_file_data(self, file, var_name):
        file.open()
        data = file.get_messages(var_name)
        file.close()
        return data

    def _construct_nan_data(self, combinations, templ_data):
        nan_data = []
        for c in combinations:
            values = np.ones_like(templ_data.values)*np.NaN
            coords = {}
            for k, dim in enumerate(templ_data.dims):
                try:
                    coords[dim] = c[k]
                except IndexError:
                    coords[dim] = templ_data[dim]
            xr_array = xr.DataArray(
                data=values,
                coords=coords,
                dims=templ_data.dims,
                attrs=templ_data.attrs
            )
            nan_data.append(xr_array)
        logger.info('Contructed the missing nan_data')
        return nan_data

    def _index_data_chunk(self, data_chunk, coordinate_names, uniques):
        d_ind = [data_chunk.values]
        for key, dim in enumerate(coordinate_names):
            if dim in data_chunk.coords:
                d_ind.append(uniques[key].index(data_chunk[dim].values))
            else:
                d_ind.append(0)
        return d_ind

    def _combine_index_data_chunk(self, data_chunk, coordinate_names, uniques):
        combination = tuple([data_chunk.coords[dim].values[0]
                             for dim in coordinate_names[:-2]])
        d_index = self._index_data_chunk(data_chunk, coordinate_names, uniques)
        return combination, d_index

    def data_merge(self, data, var_name):
        """
        Method to merge instances of xarray.DataArray into a SpatialData
        instance. Also the grid is read and inserted into the SpatialData
        instance.

        Parameters
        ----------
        data : list of xarray.DataArray
            The data list.

        Returns
        -------
        SpatialData
            The SpatialData instance with the extracted data and the extracted
            grid.
        """
        logger.debug('Input length of data_merge: {0:d}'.format(len(data)))
        logger.debug('Data coordinates {0}'.format(data[0].coords))
        logger.debug('Data dimensions {0}'.format(data[0].dims))
        if len(data) == 1:
            logger.info('Found only one message')
            extracted_data = data[0]
        else:
            logger.info('Get unique coordinates')
            coordinate_names = list(data[0].dims)
            uniques = []
            logger.debug(coordinate_names)
            for dim in coordinate_names[:-2]:
                def dim_func(d):
                    return d.coords[dim].values
                dim_gen = self._multiproc.map(dim_func, data)
                uniques.append(list(np.unique(dim_gen)))
            logger.info('Calculate possible data combinations')
            unique_combinations = list(itertools.product(*uniques))
            def combi_func(d):
                return tuple([d.coords[dim].values[0]
                              for dim in coordinate_names[:-2]])
            logger.info('Remove already satisfied combinations')
            combine_index_func = partial(
                self._combine_index_data_chunk,
                coordinate_names=coordinate_names[:-2],
                uniques=uniques)
            indexes = []
            p = Pool(processes=self.processes)
            with tqdm(total=len(data)) as pbar:
                for comb_ind in p.imap_unordered(combine_index_func, data):
                    unique_combinations.remove(comb_ind[0])
                    indexes.append(comb_ind[1])
                    pbar.update()
            p.close()
            logger.info('Set nan combinations')
            fake_data = self._construct_nan_data(unique_combinations,
                                                 templ_data=data[0])
            single_func = partial(self._index_data_chunk,
                                  coordinate_names=coordinate_names[:-2],
                                  uniques=uniques)
            fake_indexes = self._multiproc.map(single_func, fake_data)
            indexes = indexes+fake_indexes
            logger.info('Start data sorting')
            n_dims = len(coordinate_names[:-2])
            sort_dims = tuple(range(1, n_dims+1))
            sorted_data = zip(*sorted(
                indexes, key=operator.itemgetter(*sort_dims)))
            logger.debug('Start data reordering')
            sorted_data = np.array(list(sorted_data)[0])
            logger.info('Start data reshaping and coordinates setting')
            logger.debug(sorted_data.shape)
            try:
                shaped_data = sorted_data.reshape(
                    [len(u) for u in uniques]+
                    [sorted_data.shape[-2]]+
                    [sorted_data.shape[-1]])
                coord_names = coordinate_names
                coord_values = uniques+[data[0][coordinate_names[-2]].values]+\
                               [data[0][coordinate_names[-1]].values]
            # If the reshape wasn't successful
            except ValueError:
                shaped_data = sorted_data.reshape(
                    [-1]+
                    [len(u) for u in uniques]+
                    [sorted_data.shape[-2]]+
                    [sorted_data.shape[-1]])
                coord_names = ['unknown']+coordinate_names
                coord_values = [np.arange(shaped_data.shape[0])]+uniques+\
                               [data[0][coordinate_names[-2]].values]+\
                               [data[0][coordinate_names[-1]].values]
            coords = list(zip(coord_names, coord_values))
            logger.debug('Start merging')
            extracted_data = xr.DataArray(
                data=shaped_data,
                coords=coords)
            logger.debug('Start attribute setting')
            extracted_data.attrs = data[0].attrs
        logger.info('Start contruction of SpatialData')
        logger.debug(extracted_data.attrs)
        logger.debug('Trying to get the grid')
        grid = self.get_grid(var_name)
        logger.debug(grid)
        sp_data = SpatialData(extracted_data, grid=grid, data_origin=self)
        sp_data.set_data_coordinates()
        return sp_data
