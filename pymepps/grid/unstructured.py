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
import numpy as np

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
        self.__nr_coords = 1
        self._grid_dict.update(grid_dict)

    @property
    def len_coords(self):
        """
        Get the number of coordinates for this grid.

        Returns
        -------
        len_coords: int
            Number of coordinates for this grid.
        """
        return self.__nr_coords

    def _construct_dim(self):
        constructed_dim = np.arange(0, self._grid_dict['gridsize'], 1)
        return constructed_dim

    def get_coord_names(self):
        """
        Returns the name of the coordinates.

        Returns
        -------
        coord_names: list(str)
            The coordinate name for this unstructured grid. This is always a
            list, with only one entry: ncells.
        """
        return ['ncells',]

    def _calc_lat_lon(self):
        return np.array(self._grid_dict['yvals']),\
               np.array(self._grid_dict['xvals'])

    def lonlatbox(self, data, ll_box):
        """
        The data is sliced as unstructured grid with given lonlat box.

        Parameters
        ----------
        data : numpy.ndarray or xarray.DataArray
            The data which should be sliced. The shape of the last two
            dimensions should be the same as the grid dimensions.
        ll_box : tuple(float)
            The longitude and latitude box with four entries as degree. The
            entries are handled in the following way:
                (left/west, top/north, right/east, bottom/south)

        Returns
        -------
        sliced_data : numpy.ndarray or xarray.DataArray
            The sliced data with the same type as the input data. If the input
            data is a xarray.DataArray the output data will use the same
            attributes and non-grid dimensions as the input data.
        sliced_grid : UnstructuredGrid
            A new UnstructuredGrid with the sliced coordinates as values.
        """
        return self._lonlatbox(data, ll_box, unstructured=True)
