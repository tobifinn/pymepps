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

# External modules

# Internal modules
from .lonlat import Grid


logger = logging.getLogger(__name__)


class UnstructuredGrid(Grid):
    """
    In an unstructured grid the grid could have any shape. A famous example is
    the triangulated ICON grid. At the moment the longitude and latitude values
    should have been precomputed. The grid could be calculated with the number
    of vertices and the coordinates of the boundary.
    """
    def __init__(self, grid_dict):
        super().__init__(grid_dict)
        self._grid_dict = {
            'gridtype': 'unstructured',
            'xlongname': 'longitude',
            'xname': 'lon',
            'xunits': 'degrees',
            'ylongname': 'latitude',
            'yname': 'lat',
            'yunits': 'degrees',
        }
        self._grid_dict.update(grid_dict)

    def _construct_dim(self):
        return self._grid_dict['yvals'], self._grid_dict['xvals']

    def _calc_lat_lon(self):
        return self._construct_dim()