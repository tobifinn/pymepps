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
from functools import partial
import getpass
import datetime as dt

# External modules
import xarray as xr

# Internal modules
from pymepps.grid import GridBuilder
import pymepps.utilities.cdo_funcs as cdo
from .metdataset import MetDataset
from .spatialdata import SpatialData


logger = logging.getLogger(__name__)


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

    def get_grid(self, var_name, data_array=None):
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
        data_array: xarray.DataArray or None, optional
            If the data array is given the method will try to load the grid from
            the data array's attributes. If None the DataArray method will be
            skipped. Default is None.

        Returns
        -------
        grid: Instance of child of grid or None
            The returned grid. If the returned grid is None, the grid could not
            be read.
        """
        grid = self._get_grid_from_dataarray(data_array)
        if grid is None:
            if isinstance(self.grid, str):
                grid = self._get_grid_from_str(self.grid)
            elif hasattr(self.grid, 'get_coords'):
                grid = self.grid
            if grid is None:
                grid = self._get_grid_from_cdo(var_name)
        return grid

    @staticmethod
    def _get_grid_from_dataarray(data_array):
        try:
            grid_builder = GridBuilder(data_array.attrs)
            grid = grid_builder.build_grid()
            logger.debug('Got the grid from the data array')
        except (KeyError, ValueError, AttributeError):
            grid = None
        return grid

    def _get_grid_from_cdo(self, var_name):
        grid = None
        file = self.variables[var_name][0].file
        try:
            grid_str = cdo.griddes(
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
        except (KeyError, ValueError):
            grid = None
        return grid

    def _get_file_data(self, file, var_name):
        file.open()
        data = file.get_messages(var_name)
        file.close()
        return data

    @staticmethod
    def _stack_ele(ele, coordinate_names):
        return ele.stack(merge=coordinate_names)

    def data_merge(self, data, var_name):
        """
        Method to merge instances of xarray.DataArray into a SpatialData
        instance. Also the grid is read and inserted into the SpatialData
        instance.

        Parameters
        ----------
        data : list of xarray.DataArray
            The data list.
        var_name : str
            The name of the variable which is selected within the data list.

        Returns
        -------
        SpatialData
            The SpatialData instance with the extracted data and the extracted
            grid.
        """
        logger.debug('Input length of data_merge: {0:d}'.format(len(data)))
        logger.debug('Data coordinates {0}'.format(data[0].coords))
        logger.debug('Data dimensions {0}'.format(data[0].dims))
        logger.debug('Trying to get the grid')
        grid = self.get_grid(var_name, data[0])
        spdata = SpatialData(data[0], grid=grid, data_origin=self)
        if len(data)>1:
            spdata.update(*data[1:])
        history_message = \
            "{0:s}, {1:s}, Python:pymepps:SpatialDataset:select" \
            "('{2:s}')".format(
                    dt.datetime.utcnow().strftime("%Y%m%d %H:%Mz"),
                    getpass.getuser(),
                    var_name)
        if 'history' in spdata.data.attrs:
            spdata.data.attrs['history'] += '\n{0:s}'.format(history_message)
        else:
            spdata.data.attrs['history'] = history_message
        spdata.data.attrs['name'] = spdata.data._name = var_name
        return spdata
