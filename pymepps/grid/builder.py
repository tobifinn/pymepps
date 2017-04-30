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
import numpy as np

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
        griddes : dict(str, str/float)
            The grid description as dict.
        """
        self._grid_handler = None
        self._latlon = None
        self._grid_dict = {}
        self.griddes = griddes

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
        Key and value are separated with =. Every new key value pair needs a new
        line delimiter. Only alphanumeric characters are allowed as key and
        value. To delimit a value list use spaces and new lines. Lines with #
        are used as comment lines.
        
        Steps to decode the grid string:
            1) String splitting by new line delimiter
            2) Clean the lines from unallowed characters
            3) Split the non-comment lines to key, value pairs
            4) Append elements where no key, value pair is available to the
               previous value
            5) Clean and split the key, value elements from spaces
            6) Convert the values to float numbers

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
        if isinstance(grid_str, str):
            grid_str_lines = list(grid_str.split('\n'))
        elif isinstance(grid_str, list):
            grid_str_lines = grid_str
        else:
            raise TypeError('The given grid_str has to be a str or a list of '
                            'str!')
        logger.debug(grid_str_lines)
        cleaned_lines = [re.sub('[^0-9a-zA-Z=#"\_\.\-\+ ]+', '', gs)
                         for gs in grid_str_lines]
        splitted_lines = [line.split('=', 1) for line in cleaned_lines
                          if len(line) > 0 and '#' not in line]
        logger.debug(splitted_lines)
        for i in np.arange(len(splitted_lines)-1, -1, -1):
            if len(splitted_lines[i])==1 and i!=0:
                splitted_lines[i-1][-1] = "{0:s} {1:s}".format(
                    splitted_lines[i - 1][-1], splitted_lines[i][-1])
        logger.debug(splitted_lines)
        grid_dict = {}
        for line in splitted_lines:
            if len(line) == 2:
                if '"' in line[1]:
                    val = [line[1].replace('"', '').strip(), ]
                else:
                    val = list(filter(None, line[1].split(' ')))
                grid_dict[line[0].strip()] = val
        for k in grid_dict:
            try:
                grid_dict[k] = [float(val) for val in grid_dict[k]]
            except ValueError:
                pass
            if len(grid_dict[k])==1:
                grid_dict[k] = grid_dict[k][0]
        logger.debug(grid_dict)
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
        logger.debug(self._grid_handler)
        grid = self._grid_handler(self._grid_dict)
        return grid