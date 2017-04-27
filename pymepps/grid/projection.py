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
            projection = RotPoleProj(
                npole_lat=self._grid_dict['grid_north_pole_latitude'],
                npole_lon=self._grid_dict['grid_north_pole_longitude'])
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
    def __call__(self, x, y, inverse=False):
        if inverse:
            return self.transform_to_latlon(x, y)
        else:
            return self.transform_from_latlon(x, y)

    @abc.abstractmethod
    def transform_to_latlon(self, x, y):
        pass

    @abc.abstractmethod
    def transform_from_latlon(self, lon, lat):
        pass

    @staticmethod
    def _check_lat(lat):
        if not np.all(-90<=lat):
            raise ValueError(
                'The given latitude {0:.4f} is not between -90\° and '
                '90\°'.format(lat))
        elif not np.all(lat<=90):
            raise ValueError(
                'The given latitude {0:.4f} is not between -90\° and '
                '90\°'.format(lat))
        return lat

    @staticmethod
    def _check_lon(lon):
        if not np.all(-180<=lon):
            raise ValueError(
                'The given longitude {0:.4f} is not between -180\° and '
                '360\°'.format(lon))
        elif not np.all(lon<=360):
            raise ValueError(
                'The given longitude {0:.4f} is not between -180\° and '
                '360\°'.format(lon))
        elif np.any(180<lon):
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
    calculated in a cf-conform manner, with a rotated north pole. The
    calculations are based on [1]_. If the resulting latitude coordinate equals
    -90° or 90° the longitude coordinate will be set to 0°.
    
    Parameters
    ----------
    npole_lat: float
        The latitude of the rotated north pole in degrees.
    npole_lom: float
        The longitude of the rotated north pole in degrees.
    
    References
    ----------
    [1] http://de.mathworks.com/matlabcentral/fileexchange/
            43435-rotated-grid-transform
    """
    def __init__(self, npole_lat, npole_lon):
        self._north_pole = None
        self.north_pole = (npole_lat, npole_lon)

    def __call__(self, x, y, inverse=False):
        if inverse:
            return self.transform_to_lonlat(x, y)
        else:
            return self.transform_from_lonlat(x, y)

    @property
    def north_pole(self):
        return {k: self._rad2deg(self._north_pole[k]) for k in self._north_pole}

    @north_pole.setter
    def north_pole(self, coords):
        self._north_pole = {
            'lat': self._deg2rad(self._check_lat(coords[0])),
            'lon': self._deg2rad(self._check_lon(coords[1]))
        }

    def _prepare_rotation(self, lat, lon):
        lat = self._deg2rad(self._check_lat(lat))
        lon = self._deg2rad(self._check_lon(lon))
        x = np.cos(lon)*np.cos(lat)
        y = np.sin(lon)*np.cos(lat)
        z = np.sin(lat)
        theta = np.pi*1/2-self._north_pole['lat']
        phi = self._deg2rad(self._check_lon(
            self._rad2deg(self._north_pole['lon'])))
        if np.abs(self._north_pole['lat'])!=np.pi/2:
            phi = np.pi+phi
        return x, y, z, theta, phi

    def _rotate_coords(self, x, y, z, theta, phi):
        x_new = np.cos(theta)*np.cos(phi)*x\
                +np.cos(theta)*np.sin(phi)*y\
                +np.sin(theta)*z
        y_new = -np.sin(phi)*x\
                +np.cos(phi)*y
        z_new = -np.sin(theta)*np.cos(phi)*x\
                -np.sin(theta)*np.sin(phi)*y\
                +np.cos(theta)*z
        return x_new, y_new, z_new

    def _derotate_coords(self, x, y, z, theta, phi):
        phi = -phi
        theta = -theta
        x_new = np.cos(theta)*np.cos(phi)*x\
                +np.sin(phi)*y\
                +np.sin(theta)*np.cos(phi)*z
        y_new = -np.cos(theta)*np.sin(phi)*x\
                +np.cos(phi)*y\
                -np.sin(theta)*np.sin(phi)*z
        z_new = -np.sin(theta)*x\
                +np.cos(theta)*z
        return x_new, y_new, z_new

    def _post_rotation(self, x, y, z):
        lat = self._rad2deg(np.arcsin(z))
        lon = self._rad2deg(np.arctan2(y, x))
        if np.all(lat==np.pi/2):
            lon = 0
        return lat, lon

    def transform_from_lonlat(self, lon, lat):
        x, y, z, theta, phi = self._prepare_rotation(lat, lon)
        rot_x, rot_y, rot_z = self._rotate_coords(x, y, z, theta, phi)
        rot_lat, rot_lon = self._post_rotation(rot_x, rot_y, rot_z)
        return rot_lon, rot_lat

    def transform_to_lonlat(self, x, y):
        rot_x, rot_y, rot_z, theta, phi = self._prepare_rotation(y, x)
        x, y, z = self._derotate_coords(rot_x, rot_y, rot_z, theta, phi)
        lat, lon = self._post_rotation(x, y, z)
        return lon, lat
