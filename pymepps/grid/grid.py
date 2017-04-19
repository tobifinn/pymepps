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
import abc

# External modules
import xarray as xr

# Internal modules


logger = logging.getLogger(__name__)


class Grid(object):
    def __init__(self, grid_dict):
        self._lat_lon = None
        self._grid_dict = None

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
            self._lat_lon = self._get_lat_lon()
        return self._lat_lon

    def get_coords(self):
        dy, dx = self._construct_dim()
        coords = {
            self._grid_dict['yname']: ((self._grid_dict['yname'],), dy),
            self._grid_dict['xname']: ((self._grid_dict['xname'],), dx),
        }
        return coords

    @abc.abstractmethod
    def _construct_dim(self):
        pass

    def _get_lat_lon(self):
        coords = self.get_coords()
        lat, lon = self._calc_lat_lon()
        ds = xr.Dataset(
            {
                'latitude': (
                    (self._grid_dict['yname'], self._grid_dict['xname']), lat),
                'longitude': (
                    (self._grid_dict['yname'], self._grid_dict['xname']), lon),
            },
            coords=coords
        )
        return ds

    @abc.abstractmethod
    def _calc_lat_lon(self):
        pass
