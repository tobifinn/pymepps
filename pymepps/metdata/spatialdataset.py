#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 10.12.16

Created for pymepps

@author: Tobias Sebastian Finn, tobias.sebastian.finn@studium.uni-hamburg.de

    Copyright (C) {2016}  {Tobias Sebastian Finn}

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
# System modules
import logging
import datetime as dt
import operator
import os.path

# External modules
import numpy as np
import xarray as xr
import cdo

# Internal modules
from pymepps.data_structures import File
from pymepps.grid import GridBuilder
from .metdataset import MetDataset
from .spatialdata import SpatialData


CDO = cdo.Cdo()
logger = logging.getLogger(__name__)


class SpatialDataset(MetDataset):
    def __init__(self, file_handlers, grid=None, data_origin=None, processes=1):
        """
        SpatialDataset is a class for a pool of file handlers. Typically a
        spatial dataset combines the files of one model run, such that it is
        possible to select a variable and get a SpatialData instance. For
        memory reasons the data of a variable is only loaded if it is selected.

        Parameters
        ----------
        file_handlers : list of childs of FileHandler
            The spatial dataset is based on these files. The files should be
            either instances of GribHandler or NetCDFHandler.
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

        Methods
        -------
        select
            Method to select a variable.
        selnearest
            Method to select the nearest grid point for given coordinates.
        sellonlatbox
            Method to slice a box with the given coordinates.
        """
        super().__init__(file_handlers, data_origin, processes)
        self.grid = grid

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
        file = self.variables[var_name][0].file
        grid_str = CDO.griddes(
            input='-selvar,{0:s} {1:s}'.format(var_name, file))
        grid = self._get_grid_from_str(grid_str)
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

    def _cdo_path_helper(self, file_handler, new_path=None, inplace=False):
        file_obj = File(file_handler.file)
        in_file = file_obj.path
        if inplace:
            out_file = in_file
        else:
            file_name = file_obj.get_basename()
            if file_obj.get_dir == new_path:
                file_name = '{0:s}_{1:s}'.format(file_name, 'sliced')
            if new_path is not None:
                out_file = os.path.join(new_path, file_name)
            else:
                out_file = os.path.join(file_obj.get_dir(), file_name)
        logger.debug(
            'Set output path to {0:s} for file {1:s}'.format(out_file, in_file))
        return in_file, out_file

    def selnearest(self, lonlat, new_path=None, inplace=False, in_opt=None,
                   options=None):
        """
        Method to the nearest grid point to a given latitude/longitude
        coordinate pair. This method is based on the cdo command remapnn.
        For more informations see [1]_.

        Parameters
        ----------
        lonlat : Tuple of floats
            The lonlat, which should be extracted. This lonlat has two
            entries (lon, lat).
        new_path : str or None, optional
            If a new path is given as string the new file is saved at this path
            with the same file name as the input file. If this is None the new
            file will be saved in the same directory as the input file. Default
            is None.
        inplace : bool, optional
            If True the files would be overridden. If False a '_sliced' will be
            appended to the file name. Default is True.
        in_opt : str or None, optional
            If the input options are given as string, the string will be used as
            input to the cdo method. %FILE% is a placeholder and will be
            replaced by the file path. If this is None the file path will be
            used as input. Default is None.

        Returns
        -------
        self
        
        References
        ----------
        [1] https://code.zmaw.de/boards/2/topics/301
        """
        new_file_handlers = []
        for file_handler in self.file_handlers:
            in_file, out_file = self._cdo_path_helper(file_handler=file_handler,
                                                      new_path=new_path,
                                                      inplace=inplace)
            options_str = ''
            if isinstance(options, str):
                options_str = options
            input_str = in_file
            if isinstance(in_opt, str):
                input_str = in_opt.replace('%FILE%', in_file)
            if not os.path.isfile(out_file) and in_file!=out_file:
                CDO.remapnn(
                    'lon={0:.4f}_lat={1:.4f}'.format(lonlat[0], lonlat[1]),
                    input=input_str,
                    output=out_file,
                    options=options_str)
                logger.debug('Finished CDO remapnn, set new file_handler')
            else:
                logger.debug('File already exists. It\'s assumed, that this is '
                             'the already sliced file.')
            new_file_handlers.append(type(file_handler)(out_file))
        logger.debug('Finished selnearest, set new file_handlers.')
        self.file_handlers = new_file_handlers
        return self


    def sellonlatbox(self, lonlatbox, new_path=None, inplace=False,
                     in_opt=None, options=None):
        """
        Method to select a longitude/latitude box and slice the FileHandlers.
        This method is based on the cdo command sellonlatbox.
        Parameters
        ----------
        lonlatbox : Tuple of floats
            The lonlatbox, which should be sliced. This lonlatbox has four
            entries (left, top, right, bottom).
        new_path : str or None, optional
            If a new path is given as string the new file is saved at this path
            with the same file name as the input file. If this is None the new
            file will be saved in the same directory as the input file. Default
            is None.
        inplace : bool, optional
            If True the files would be overridden. If False a '_sliced' will be
            appended to the file name. Default is True.
        in_opt : str or None, optional
            If the input options are given as string, the string will be used as
            input to the cdo method. %FILE% is a placeholder and will be
            replaced by the file path. If this is None the file path will be
            used as input. Default is None.

        Returns
        -------
        self
        """
        new_file_handlers = []
        for file_handler in self.file_handlers:
            in_file, out_file = self._cdo_path_helper(file_handler=file_handler,
                                                      new_path=new_path,
                                                      inplace=inplace)
            options_str = ''
            if isinstance(options, str):
                options_str = options
            input_str = in_file
            if isinstance(in_opt, str):
                input_str = in_opt.replace('%FILE%', in_file)
            if not os.path.isfile(out_file) and in_file!=out_file:
                CDO.sellonlatbox(lonlatbox[0],lonlatbox[2],lonlatbox[3],
                                 lonlatbox[1],
                                 input=input_str,
                                 options=options_str)
                logger.debug('Finished CDO sellonlatbox, set new file_handler')
            else:
                logger.debug('File already exists. It\'s assumed, that this is '
                             'the already sliced file.')
            new_file_handlers.append(type(file_handler)(out_file))
        logger.debug('Finished sellonlatbox, set new file_handlers.')
        self.file_handlers = new_file_handlers
        return self

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
            logger.debug('Found only one message')
            extracted_data = data[0]
        else:
            coordinate_names = list(data[0].dims)
            uniques = []
            logger.debug(coordinate_names)
            for dim in coordinate_names[:-2]:
                dim_gen = [d[dim].values for d in data]
                uniques.append(list(np.unique(dim_gen)))
            logger.debug('Got unique coordinates')
            indexes = []
            logger.debug('Start coordinates indexing')
            for d in data:
                d_ind = [d.values]
                for key, dim in enumerate(coordinate_names[:-2]):
                    if dim in d.coords:
                        d_ind.append(uniques[key].index(d[dim].values))
                    else:
                        d_ind.append(0)
                logger.debug(
                    'Finished coordinates indexing for {0:s}'.format(
                        str(d_ind[1:])))
                indexes.append(d_ind)
            logger.debug('Start data sorting')
            n_dims = len(coordinate_names[:-2])
            sort_dims = tuple(range(1, n_dims+1))
            sorted_data = zip(*sorted(
                indexes, key=operator.itemgetter(*sort_dims)))
            logger.debug('Start data reordering')
            sorted_data = np.array(list(sorted_data)[0])
            logger.debug('Start data reshaping and coordinates setting')
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
            logger.debug('Finished data merging')
        logger.debug(extracted_data.attrs)
        logger.debug('Trying to get the grid')
        grid = self.get_grid(var_name)
        logger.debug(grid)
        return SpatialData(extracted_data, grid=grid, data_origin=self)
