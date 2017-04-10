#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 10.04.17
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
import re

# External modules

# Internal modules
from .lonlat import LonLatGrid
from .gaussian import GaussianGrid
from .projection import ProjectionGrid
from .curvilinear import CurvilinearGrid
from .unstructured import UnstructuredGrid


logger = logging.getLogger(__name__)


available_grids = {
    'lonlat': LonLatGrid,
    'gaussian': GaussianGrid,
    'projection': ProjectionGrid,
    'curvilinear': CurvilinearGrid,
    'unstructured': UnstructuredGrid
}


class GridBuilder(object):
    def __init__(self, griddes):
        """
        Class representing horizontal grids of grid based files. This class is
        based on the grid description files of cdo [cdo]_. With this grid
        description is is possible to remap grid based arrays and to interpolate
        for a given latitude and longitude. Internally the grids are transformed
        to latitude and longitude points.
        
        .. [cdo] https://code.zmaw.de/projects/cdo

        Parameters
        ----------
        griddes : str or dict(str, str/float)
            The grid description. This could be a path to a cdo conform grid
            description file. Another possibility is to use a cdo conform grid
            description within a str or a dict. The latitude and longitude
            values are calculated based on this parameter.
        
        Attributes
        ----------
        decoded
        """
        self._latlon = None
        self._grid_dict = {}
        self.griddes = griddes
        self._grid_handler = None

    @property
    def griddes(self):
        return self._grid_dict

    @griddes.setter
    def griddes(self, description):
        if isinstance(description, str):
            grid_str = self.open_string(description)
            grid_dict = self.decode_str(grid_str)
        elif isinstance(description, list):
            grid_dict = self.decode_str(description)
        elif isinstance(description, dict):
            grid_dict = description
        else:
            raise TypeError('The given grid description has to be a string, a '
                            'dict or None!')
        logger.debug('Decoded griddes, now set _latlon_decoder')
        self._set_grid_handler(grid_dict)
        self._grid_dict = grid_dict

    def _set_grid_handler(self, grid_dict):
        if 'gridtype' not in grid_dict:
            raise KeyError('There is no gridtype defined. Griddes is no '
                             'valid cdo grid definition!')
        if grid_dict['gridtype'] not in available_grids:
            raise ValueError('The given gridtype "{0:s}" has no defined '
                             'decoder yet, please use one of the available '
                             'gridtypes!'.format(grid_dict['gridtype']))
        self._grid_handler = available_grids[grid_dict['gridtype']]
        logger.debug('Set _latlon_decoder to {0:s}'.format(
            self._grid_handler.__name__))

    @staticmethod
    def open_string(path_str):
        """
        This method is used to check if the given str is a path or a grid
        string.

        Parameters
        ----------
        path_str : str
            This string is checked and if it is a path it will be read.

        Returns
        -------
        grid_str : str
            The given str or the read str.
        
        Raises
        ------
        TypeError
            If path_str is not a str type.
        """
        try:
            with open(path_str, 'r') as gf:
                grid_str = gf.read()
        except FileNotFoundError:
            grid_str = path_str
        return grid_str

    @staticmethod
    def decode_str(grid_str):
        """
        Method to clean the given grid str and to get a python dict.

        Parameters
        ----------
        grid_str : str or list(str)
            The given grid_str which should be decoded. If this is a string the
            string will be splitten by new line into a list. It is necessary
            that every list entry has only one key = value entry.

        Returns
        -------
        grid_dict : dict(str, str or float)
            The decoded grid dict from the str.
        """
        grid_str_lines = None
        if isinstance(grid_str, str):
            grid_str_lines = list(grid_str.split('\n'))
        elif isinstance(grid_str, list):
            grid_str_lines = grid_str
        else:
            raise TypeError('The given grid_str has to be a str or a list of '
                            'str!')
        grid_dict = {}
        logger.debug(grid_str_lines)
        for gs in grid_str_lines:
            gs = re.sub('[^0-9a-zA-Z=#-\.]+', '', gs).lower()
            logger.debug(gs)
            if len(gs) > 0 and gs[0] != '#':
                key_value_str = gs.split('=')
                try:
                    grid_dict[key_value_str[0]] = float(key_value_str[1])
                except ValueError:
                    grid_dict[key_value_str[0]] = key_value_str[1]
                except IndexError:
                    logger.warning('The given key value string "{0:s}" is not '
                                   'a valid key value string, it will be '
                                   'skipped. The syntax has to be '
                                   'key=value!'.format(gs))
        return grid_dict

    def build_grid(self):
        """
        This method build up the grid with the griddes attribute.

        Returns
        -------
        grid : child instance of Grid
            The built grid. The class of the grid is defined by the gridtype.
            The values of the grid are calculated with griddes.
        """
        grid = self._grid_handler(self._grid_dict)
        return grid