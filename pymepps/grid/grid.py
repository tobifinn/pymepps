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


logger = logging.getLogger(__name__)


class Grid(object):
    def __init__(self, grid_dict):
        self._lat_lon = None
        self.grid_dict = grid_dict

    def get_coordinates(self):
        """
        Method to get xarray conform coordinates for this grid type.

        Returns
        -------
        xr_coords : xarray.DataArray
        """
        pass

    @property
    def lat_lon(self):
        if self._lat_lon is None:
            self._calc_lat_lon()
        return self._lat_lon

    def _calc_lat_lon(self):
        pass
