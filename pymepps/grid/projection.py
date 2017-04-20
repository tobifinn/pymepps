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


class BaseProj(object):
    def __call__(self, y, x, inverse=False):
        if inverse:
            return self.transform_to_latlon(y, x)
        else:
            return self.transform_from_latlon(y, x)

    @abc.abstractmethod
    def transform_to_latlon(self, y, x):
        pass

    @abc.abstractmethod
    def transform_from_latlon(self, lat, lon):
        pass

    @staticmethod
    def _check_lat(lat):
        if not np.all(-90<=lat<=90):
            raise ValueError(
                'The given latitude {0:.4f} is not between -90\° and '
                '90\°'.format(lat))
        return lat

    @staticmethod
    def _check_lon(lon):
        if not np.all(-180<=lon<=360):
            raise ValueError(
                'The given longitude {0:.4f} is not between -180\° and '
                '360\°'.format(lon))
        elif np.all(180<lon):
            lon = 360 - lon
        return lon

    @staticmethod
    def _deg2rad(deg):
        return deg*np.pi/180

    @staticmethod
    def _rad2deg(rad):
        return rad*180/np.pi


class RotPoleProj(BaseProj):
    """
    Class for to calculate the transformation from rotated pole coordinates to 
    normal latitude and longitude coordinates. The rotated pole coordinates are
    calculated in a cf-conform manner, with a rotated north pole.
    
    Parameters
    ----------
    npole_lat: float
        The latitude of the rotated north pole in degrees.
    npole_lom: float
        The longitude of the rotated north pole in degrees.
    """
    def __init__(self, npole_lat, npole_lon):
        self._north_pole = None
        self.north_pole = (npole_lat, npole_lon)

    @property
    def north_pole(self):
        return {k: self._rad2deg(self._north_pole[k]) for k in self._north_pole}

    @north_pole.setter
    def north_pole(self, coords):
        self._north_pole = {
            'lat': self._deg2rad(self._check_lat(coords[0])),
            'lon': self._deg2rad(self._check_lon(coords[1]))
        }

    def rotate_coords(self, lat, lon, p_lat, p_lon):
        rot_lat = self._deg2rad(self._check_lat(lat))
        rot_lon = self._deg2rad(self._check_lon(lon))
        rot_x = np.cos(rot_lon)*np.cos(rot_lat)
        rot_y = np.sin(rot_lon)*np.cos(rot_lat)
        rot_z = np.sin(rot_lat)
        x = np.cos(p_lat)*\
            np.cos(p_lon)*\
            rot_x+np.sin(p_lon)*rot_y+\
            np.sin(p_lat)*np.cos(p_lon)*\
            rot_z
        y = -np.cos(p_lat)*\
            np.sin(p_lon)*\
            rot_x+np.cos(p_lon)*rot_y-\
            np.sin(p_lat)*np.sin(p_lon)*\
            rot_z
        z = -np.sin(p_lat)*rot_x+\
            np.cos(p_lat)*rot_z
        lat = self._rad2deg(np.arcsin(z))
        lon = self._rad2deg(np.arctan2(y, x))
        return lat, lon

    def transform_from_latlon(self, lat, lon):
        p_lat = self._north_pole['lat']
        p_lon = -self._north_pole['lon']
        return self.rotate_coords(lat, lon, p_lat, p_lon)

    def transform_to_latlon(self, y, x):
        p_lat, p_lon = np.pi/2-self._north_pole['lat'], -self._north_pole['lon']
        return self.rotate_coords(y, x, p_lat, p_lon)


