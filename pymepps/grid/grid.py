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


logger = logging.getLogger(__name__)


class Grid(object):
    def __init__(self, griddes=None):
        self.griddes = griddes
        self._grid_dict = None

    @property
    def griddes(self):
        return self._grid_dict

    @griddes.setter
    def griddes(self, description):
        if isinstance(description, str):
            grid_str = self.open_string(description)
            grid_dict = self.decode_str(grid_str)
        elif isinstance(description, dict) or description is None:
            grid_dict = description
        else:
            raise TypeError('The given grid description has to be a string, a '
                            'dict or None!')
        self._grid_dict = grid_dict

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
        grid_str : str
            The given grid_str which should be decoded.

        Returns
        -------
        grid_dict : dict(str, str/float)
            The decoded grid dict from the str.
        """
        grid_str_lines = list(grid_str.split('\n'))
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
        logger.debug(grid_dict)
        return grid_dict
