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
from .lonlat import LonLatGrid
from .unstructured import UnstructuredGrid


logger = logging.getLogger(__name__)


class CurvilinearGrid(LonLatGrid):
    """
    A curvilinear grid could be described as special case of a lonlat grid
    where the number of vertices is 4. The raw grid values are calculated based
    on the given grid rules. At the moment the lon lat values had to be
    precomputed.
    """
    def __init__(self, grid_dict):
        super().__init__(grid_dict)
        self._grid_dict = {
            'gridtype': 'curvilinear',
            'xlongname': 'longitude',
            'xname': 'lon',
            'xunits': 'degrees',
            'ylongname': 'latitude',
            'yname': 'lat',
            'yunits': 'degrees',
            'nvertex': 4,
        }
        self._grid_dict.update(grid_dict)

    def _calc_lat_lon(self):
        return self._grid_dict['yvals'], self._grid_dict['xvals']

    def lonlatbox(self, data, ll_box):
        """
        The data is sliced with given lonlat box to a unstructured grid.

        Parameters
        ----------
        data : numpy.ndarray
            The data which should be sliced. The shape of the last two
            dimensions should be the same as the  grid dimensions.
        ll_box : tuple(float)
            The longitude and latitude box with four entries as degree. The
            entries are handled in the following way:
                (left/west, top/north, right/east, bottom/south)

        Returns
        -------
        sliced_data : numpy.ndarray
            The sliced data. The last two dimensions are flattened and sliced.
        grid : UnstructuredGrid
            A new instance of UnstructuredGrid with the sliced coordinates as
            values.
        """
        sliced_data, new_grid_dict = self._unstructured_box(data, ll_box)
        grid = UnstructuredGrid(new_grid_dict)
        return sliced_data, grid
