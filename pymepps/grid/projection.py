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
import pyproj

# Internal modules
from .lonlat import LonLatGrid


logger = logging.getLogger(__name__)


class ProjectionGrid(LonLatGrid):
    """
    A projection grid could be defined by a evenly distributed grid. The grid
    could be translated to a longitude and latitude grid by a predefined
    projection. At the moment only projections defined by a proj4 string or a 
    rotated latitude and longitude are supported.
    """
    def __init__(self, grid_dict):
        super().__init__(grid_dict)
        self._grid_dict = {
            'gridtype': 'projection',
            'xlongname': 'longitude',
            'xname': 'lon',
            'xunits': 'degrees',
            'ylongname': 'latitude',
            'yname': 'lat',
            'yunits': 'degrees',
            'proj4': None,
        }
        self._grid_dict.update(grid_dict)
        self.proj = self.get_projection()

    def get_projection(self):
        if self._grid_dict['proj4'] is not None:
            projection = pyproj.Proj(self._grid_dict['proj4'])
        elif self._grid_dict['grid_mapping'] == 'rotated_pole':
            proj__dict = {
                'proj': 'ob_tran',
                'o_proj': 'longlat',
                'o_lon_p': self._grid_dict['grid_north_pole_longitude'],
                'o_lat_p': self._grid_dict['grid_north_pole_latitude'],
                'lon_0': 180,
            }
            projection = pyproj.Proj(**proj__dict)
        else:
            raise ValueError(
                'The given projection grid isn\'t supported yet, please use a'
                'valid proj4 string or a rotated lonlat grid!')
        return projection

    def _calc_lat_lon(self):
        y, x = self._construct_dim()
        y, x = np.meshgrid(y, x)
        lon, lat = self.proj(x.transpose(), y.transpose(), inverse=True)
        return lat, lon