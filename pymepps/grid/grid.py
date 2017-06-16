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
import xarray as xr
from mpl_toolkits.basemap import interp
from scipy.interpolate import griddata

# Internal modules


logger = logging.getLogger(__name__)


known_units = {
    'deg': lambda x: x,
    'rad': lambda x: x*180/np.pi,
}


class Grid(object):
    def __init__(self, grid_dict):
        self._lat_lon = None
        self._grid_dict = None
        self.__nr_coords = 2

    @property
    def len_coords(self):
        """
        Get the number of coordinates for this grid.
        Returns
        -------
        int
            Number of coordinates for this grid.
        """
        return self.__nr_coords

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

    @property
    def raw_dim(self):
        return self._construct_dim()

    @property
    def lat_lon(self):
        if self._lat_lon is None:
            self._lat_lon = self._get_lat_lon()
        return self._lat_lon

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

    @staticmethod
    def normalize_lat_lon(lat, lon, data=None):
        """
        The given coordinates will be normalized and reorder into basemap
        conform coordinates. If the longitude values are between 0° and 360°,
        they will be normalized to values between -180° and 180°. Then the
        coordinates will be reorder, such that they are in an increasing order.

        Parameters
        ----------
        lat : numpy.ndarray
            The latitude values. They are representing the first data dimension.
        lon : numpy.ndarray
            The longitude values. They are representing the second data
            dimension.
        data : numpy.ndarray or None, optional
            The data values. They will be also reordered by lat and lon. If this
            is None, only lat and lon will be reordered and returned. Default is
            None.

        Returns
        -------
        lat : numpy.ndarray
            Ordered latitude values.
        lon : numpy.ndarray
            Ordered and normalized longitude values.
        data : numpy.ndarray or None
            The orderd data based on given latitudes and longitudes. This is
            None if no other data was given as parameter.
        """
        while np.any(lon>180):
            lon[lon>180] -= 360
        sort_order_lat = np.argsort(lat, 0)
        sort_order_lon = np.argsort(lon, 1)
        if data is None:
            return_data = None
        else:
            return_data = data[..., sort_order_lat, sort_order_lon]
        return lat[sort_order_lat, sort_order_lon], \
               lon[sort_order_lat, sort_order_lon], \
               return_data

    def get_coord_names(self):
        """
        Returns the name of the coordinates.

        Returns
        -------
        yname : str
            The name of the y-dimension.
        xname : str
            The name of the x-dimension
        """
        return self._grid_dict['yname'], self._grid_dict['xname']

    def _interpolate_unstructured(self, data, src_lat, src_lon,
                                  trg_lat, trg_lon, order=0):
        """
        The interpolation is done with scipy.interpolate.griddata.
        """
        if order==1:
            method='linear'
        else:
            method='nearest'
        reshaped_data = data.reshape((-1, src_lat.size))
        unravel_shape = data.shape[:-self.len_coords]
        src_lat = src_lat.ravel()
        src_lon = src_lon.ravel()
        src_coords = np.concatenate((src_lat, src_lon), axis=1)
        unravel_shape = tuple(list(unravel_shape)+list(trg_lat.shape))
        remapped_data = np.zeros((reshaped_data.shape[0], trg_lat.size))
        trg_lat = trg_lat.ravel()
        trg_lon = trg_lon.ravel()
        trg_coords = np.concatenate((trg_lat, trg_lon), axis=1)
        for i in range(reshaped_data.shape[0]):
            sliced_array = reshaped_data[i, :]
            remapped_data[i, :] = griddata(src_coords, sliced_array, trg_coords,
                                           method=method)
        remapped_data = remapped_data.reshape(unravel_shape)
        remapped_data = np.atleast_1d(remapped_data)
        return remapped_data

    def _interpolate_structured(self, data, src_lat, src_lon,
                                trg_lat, trg_lon, order=0):
        reshaped_data = data.reshape((-1, data.shape[-2], data.shape[-1]))
        remapped_data = np.zeros(
            (reshaped_data.shape[0], trg_lat.shape[-2], trg_lat.shape[-1]))
        for i in range(reshaped_data.shape[0]):
            sliced_array = reshaped_data[i, :, :]
            remapped_data[i, :, :] = interp(sliced_array.T, src_lat, src_lon,
                                            trg_lat, trg_lon, order=order)
        remapped_shape = list(data.shape[:-2])+list(remapped_data.shape[-2:])
        remapped_data = remapped_data.reshape(remapped_shape)
        remapped_data = np.atleast_2d(remapped_data)
        return remapped_data

    def remapnn(self, data, other_grid):
        """
        The given data will be remapped via nearest neighbour to the given other
        grid.

        Parameters
        ----------
        data : numpy.ndarray
            The data which should be remapped. There have to be at least two 
            dimensions. If the data has more than two dimensions we suppose that
            the last two dimensions are the horizontal grid dimensions.
        other_grid : child instance of Grid
            The data will be remapped to this grid.

        Returns
        -------
        remapped_data : numpy.ndarray
            The remapped data. The shape of the last two dimensions is now the
            shape of the other_grid coordinates.
        
        Notes
        -----
        Technically basemap's interp with order=0 is used to interpolate the
        data.
        """
        src_lat, src_lon = self._calc_lat_lon()
        if data.shape[-self.len_coords:] != src_lat.shape:
            raise ValueError(
                'The last {0:d} dimensions of the data needs the same shape as '
                'the coordinates of this grid!'.format())
        src_lat, src_lon, data = self.normalize_lat_lon(src_lat, src_lon, data)
        try:
            trg_lat, trg_lon = other_grid._calc_lat_lon()
        except AttributeError:
            raise TypeError('other_grid has to be a child instance of Grid!')
        trg_lat, trg_lon, _ = self.normalize_lat_lon(trg_lat, trg_lon)
        if min((self.len_coords, other_grid.len_coords))==1:
            remapped_data = self._interpolate_unstructured(
                data, src_lat, src_lon, trg_lat, trg_lon, order=0)
        else:
            remapped_data = self._interpolate_structured(
                data, src_lat[:, 0], src_lon[0, :], trg_lat, trg_lon, order=0)
        return remapped_data

    def remapbil(self, data, other_grid):
        """
        The given data will be remapped via bilinear interpolation to the given
        other grid.

        Parameters
        ----------
        data : numpy.ndarray
            The data which should be remapped. There have to be at least two 
            dimensions. If the data has more than two dimensions we suppose that
            the last two dimensions are the horizontal grid dimensions.
        other_grid : child instance of Grid
            The data will be remapped to this grid.

        Returns
        -------
        remapped_data : numpy.ndarray
            The remapped data. The shape of the last two dimensions is now the
            shape of the other_grid coordinates.
        
        Notes
        -----
        Technically basemap's interp with order=1 is used to interpolate the
        data.
        """
        src_lat, src_lon = self._calc_lat_lon()
        if data.shape[-self.len_coords:] != src_lat.shape:
            raise ValueError(
                'The last dimensions of the data needs the same shape as '
                'the coordinates of this grid!')
        src_lat, src_lon, data = self.normalize_lat_lon(src_lat, src_lon, data)
        try:
            trg_lat, trg_lon = other_grid._calc_lat_lon()
        except AttributeError:
            raise TypeError('other_grid has to be a child instance of Grid!')
        trg_lat, trg_lon, _ = self.normalize_lat_lon(trg_lat, trg_lon)
        if min((self.len_coords, other_grid.len_coords))==1:
            remapped_data = self._interpolate_unstructured(
                data, src_lat, src_lon, trg_lat, trg_lon, order=0)
        else:
            remapped_data = self._interpolate_structured(
                data, src_lat[:, 0], src_lon[0, :], trg_lat, trg_lon, order=0)
        return remapped_data

    def get_nearest_point(self, data, coord):
        """
        Get the nearest neighbour grid point for a given coordinate. The
        distance between the grid points and the given coordinates is calculated
        with the haversine formula.

        Parameters
        ----------
        coord : tuple(float, float)
            The data of the nearest grid point to this coordinate
            (latitude, longitude) will be returned. The coordinate should be in
            degree.
        data : numpy.array
            The return value is extracted from this array. The array should have
            at least two dimensions. If the array has more than two dimensions 
            the last two dimensions will be used as horizontal grid dimensions.

        Returns
        -------
        nearest_data : numpy.array
            The extracted data for the nearest neighbour grid point. The
            dimensions of this array are the same as the input data array
            without the horizontal coordinate dimensions. There is at least one
            dimension.
        """
        src_lat, src_lon = self._calc_lat_lon()
        if data.shape[-self.len_coords:] != src_lat.shape:
            raise ValueError(
                'The last two dimension of the data needs the same shape as '
                'the coordinates of this grid!')
        calc_distance = distance_haversine(
            coord,
            (src_lat.flatten(), src_lon.flatten()))
        nearest_ind = np.unravel_index(calc_distance.argmin(), src_lat.shape)
        if self.len_coords==1:
            nearest_data = data[..., nearest_ind[0]]
        else:
            nearest_data = data[..., nearest_ind[0], nearest_ind[1]]
        return np.atleast_1d(nearest_data)

    @staticmethod
    def convert_to_deg(field, unit):
        """
        Method to convert given field with given unit into degree.

        Parameters
        ----------
        field
        unit

        Returns
        -------

        """
        try:
            calculated_field = [known_units[known](field)
                                for known in known_units
                                if known in unit.lower()][0]
        except IndexError:
            raise ValueError('There is no calculating rule for the given unit '
                             '{0:s} defined yet!'.format(unit))
        return calculated_field

def distance_haversine(p1, p2):
    """
    Calculate the great circle distance between two points 
    on the earth. The formula is based on the haversine formula [1]_.

    Parameters
    ----------
    p1 : tuple (array_like, array_like)
        The coordinates (latitude, longitude) of the first point in degrees.
    p2 : tuple (array_like, array_like)
        The coordinates (latitude, longitude) of the second point in degrees.
        
    Returns
    -------
    d : float
        The calculated haversine distance in meters.
    
    Notes
    -----
    Script based on: http://stackoverflow.com/a/29546836
    
    References
    ----------
    .. [1] de Mendoza y Ríos, Memoria sobre algunos métodos nuevos de calcular
       la longitud por las distancias lunares: y aplication de su teórica á la
       solucion de otros problemas de navegacion, 1795.
    """
    lat1, lon1 = p1
    lat2, lon2 = p2
    R = 6371E3
    lat1, lon1, lat2, lon2 = map(np.deg2rad, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    d = R * c
    return d
