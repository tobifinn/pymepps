#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 10.04.17

Created for pymepps

@author: Tobias Sebastian Finn, tobias.sebastian.finn@studium.uni-hamburg.de

    Copyright (C) {2017}  {Tobias Sebastian Finn}

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
# System modules
import unittest
import logging
import os

# External modules
import numpy as np
import xarray as xr

from mpl_toolkits.basemap import interp

# Internal modules
from pymepps.grid import GridBuilder
from pymepps.grid.lonlat import LonLatGrid


logging.basicConfig(level=logging.DEBUG)

BASE_PATH = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.realpath(__file__)))),
    'data')


class TestLatLonGrid(unittest.TestCase):
    def setUp(self):
        file = os.path.join(BASE_PATH, 'grids', 'lon_lat')
        builder = GridBuilder(file)
        self.grid_dict = builder.griddes
        self.grid = builder.build_grid()

    def const_lat_lon(self, first, steps, width):
        return np.arange(
            first,
            first+ steps * width,
            width
        )

    def test_construct_dim_calcs_dim_lat_lon(self):
        calculated_lat_lon = self.grid._construct_dim()
        lon = self.const_lat_lon(
            self.grid_dict['xfirst'],
            self.grid_dict['xsize'],
            self.grid_dict['xinc']
        )
        lat = self.const_lat_lon(
            self.grid_dict['yfirst'],
            self.grid_dict['ysize'],
            self.grid_dict['yinc']
        )
        np.testing.assert_array_equal(
            lat,
            calculated_lat_lon[0])
        np.testing.assert_array_equal(
            lon,
            calculated_lat_lon[1])

    def test_calc_lat_lon_calc_lat_lon(self):
        calculated_lat_lon = self.grid._calc_lat_lon()
        lon = self.const_lat_lon(
            self.grid_dict['xfirst'],
            self.grid_dict['xsize'],
            self.grid_dict['xinc']
        )
        lat = self.const_lat_lon(
            self.grid_dict['yfirst'],
            self.grid_dict['ysize'],
            self.grid_dict['yinc']
        )
        lat, lon = np.meshgrid(lat, lon)
        np.testing.assert_array_equal(
            lat.transpose(),
            calculated_lat_lon[0])
        np.testing.assert_array_equal(
            lon.transpose(),
            calculated_lat_lon[1])

    def test_calc_lat_lon_calc_radian_to_deg(self):
        self.grid._grid_dict['xunits'] = 'radian'
        self.grid._grid_dict['yunits'] = 'radian'
        calculated_lat_lon = self.grid._calc_lat_lon()
        lon = self.const_lat_lon(
            self.grid_dict['xfirst'],
            self.grid_dict['xsize'],
            self.grid_dict['xinc']
        ) * 180 / np.pi
        lat = self.const_lat_lon(
            self.grid_dict['yfirst'],
            self.grid_dict['ysize'],
            self.grid_dict['yinc']
        ) * 180 / np.pi
        lat, lon = np.meshgrid(lat, lon)
        np.testing.assert_array_equal(
            lat.transpose(),
            calculated_lat_lon[0])
        np.testing.assert_array_equal(
            lon.transpose(),
            calculated_lat_lon[1])

    def test_convert_to_degree_radian_to_deg(self):
        lon = self.const_lat_lon(
            self.grid_dict['xfirst'],
            self.grid_dict['xsize'],
            self.grid_dict['xinc']
        )
        returned_lon = self.grid.convert_to_deg(field=lon, unit='radian')
        np.testing.assert_array_equal(lon*180/np.pi, returned_lon)

    def test_convert_to_degree_raises_error_if_unknown_unit(self):
        lon = self.const_lat_lon(
            self.grid_dict['xfirst'],
            self.grid_dict['xsize'],
            self.grid_dict['xinc']
        )
        with self.assertRaises(ValueError):
            self.grid.convert_to_deg(field=lon, unit='m84174bihaf')

    def test_get_lat_lon_returns_xarray(self):
        calculated_lat_lon = self.grid._get_lat_lon()
        self.assertIsInstance(calculated_lat_lon, xr.Dataset)
        lat, lon = self.grid._calc_lat_lon()
        lat1, lon1 = self.grid._construct_dim()
        test_ds = xr.Dataset(
            {
                'lat': (('lat1', 'lon1'), lat),
                'lon': (('lat1', 'lon1'), lon)},
            coords={
                'lat1': (('lat1'), lat1),
                'lon1': (('lon1'), lon1),
            })
        np.testing.assert_array_equal(
            calculated_lat_lon['latitude'].values,
            test_ds['lat'].values)
        np.testing.assert_array_equal(
            calculated_lat_lon['longitude'].values,
            test_ds['lon'].values)

    def test_get_coords_returns_xr_conform_coords(self):
        returned_coords = self.grid.get_coords()
        self.assertIn(
            self.grid_dict['xname'], returned_coords
        )
        self.assertIn(
            self.grid_dict['yname'], returned_coords
        )

    def test_normalize_grid_sorts_data(self):
        lat = np.arange(90, -90, -30)
        lon = np.arange(-180, 180, 30)
        lat, lon = np.meshgrid(lat, lon)
        lat = lat.transpose()
        lon = lon.transpose()
        data = np.random.normal(size=lat.shape)
        normalized_output = self.grid.normalize_lat_lon(lat, lon, data)
        sort_order_lat = np.argsort(lat, 0)
        sort_order_lon = np.argsort(lon, 1)
        lat = lat[sort_order_lat, sort_order_lon]
        lon = lon[sort_order_lat, sort_order_lon]
        data = data[sort_order_lat, sort_order_lon]
        np.testing.assert_array_equal(lat, normalized_output[0])
        np.testing.assert_array_equal(lon, normalized_output[1])
        np.testing.assert_array_equal(data, normalized_output[2])

    def test_normalize_grid_normalize_lon(self):
        lat = np.arange(90, -90, -30)
        lon = np.arange(0, 360, 30)
        lat, lon = np.meshgrid(lat, lon)
        lat = lat.transpose()
        lon = lon.transpose()
        data = np.random.normal(size=lat.shape)
        normalized_output = self.grid.normalize_lat_lon(lat, lon, data)
        lon[lon>180] -= 360
        sort_order_lat = np.argsort(lat, 0)
        sort_order_lon = np.argsort(lon, 1)
        lon = lon[sort_order_lat, sort_order_lon]
        np.testing.assert_array_equal(lon, normalized_output[1])

    def test_interpolate_with_nearest_neighbour(self):
        ll_lat, ll_lon = self.grid._calc_lat_lon()
        data = np.arange(ll_lat.size).reshape(ll_lat.shape)
        logging.debug(data.shape)
        file = os.path.join(BASE_PATH, 'grids', 'gaussian_y')
        builder = GridBuilder(file)
        gaussian_grid = builder.build_grid()
        remapped_values = self.grid.interpolate(data, gaussian_grid, 0)
        g_lat, g_lon = gaussian_grid._calc_lat_lon()
        ll_lat, ll_lon, data = self.grid.normalize_lat_lon(ll_lat, ll_lon, data)
        g_lat, g_lon, _ = self.grid.normalize_lat_lon(g_lat, g_lon)
        interpolated_values = interp(data.T, ll_lat[:, 0], ll_lon[0, :],
                                     g_lat, g_lon, order=0)
        np.testing.assert_array_equal(remapped_values, interpolated_values)

    def test_interpolate_with_bilinear(self):
        ll_lat, ll_lon = self.grid._calc_lat_lon()
        data = np.arange(ll_lat.size).reshape(ll_lat.shape)
        file = os.path.join(BASE_PATH, 'grids', 'gaussian_y')
        builder = GridBuilder(file)
        gaussian_grid = builder.build_grid()
        remapped_values = self.grid.interpolate(data, gaussian_grid, 1)
        g_lat, g_lon = gaussian_grid._calc_lat_lon()
        ll_lat, ll_lon, data = self.grid.normalize_lat_lon(ll_lat, ll_lon, data)
        g_lat, g_lon, _ = self.grid.normalize_lat_lon(g_lat, g_lon)
        interpolated_values = interp(data.T, ll_lat[:, 0], ll_lon[0, :],
                                     g_lat, g_lon, order=1)
        np.testing.assert_array_equal(remapped_values, interpolated_values)

    def test_get_nearest_point(self):
        ll_lat, ll_lon = self.grid._calc_lat_lon()
        data = np.random.normal(size=ll_lat.shape)
        target_point = (53.45, 10.05)
        trg_lat = (np.abs(ll_lat[:,0] - target_point[0])).argmin()
        trg_lon = (np.abs(ll_lon[0,:] - target_point[1])).argmin()
        target_data = data[trg_lat, trg_lon].squeeze()
        extracted_data = self.grid.get_nearest_point(data, target_point)
        np.testing.assert_array_equal(target_data, extracted_data)

    def test_get_nearest_point_multi_dim(self):
        ll_lat, ll_lon = self.grid._calc_lat_lon()
        data = np.random.normal(size=[5,]+list(ll_lat.shape))
        target_point = (53.45, 10.05)
        trg_lat = (np.abs(ll_lat[:,0] - target_point[0])).argmin()
        trg_lon = (np.abs(ll_lon[0,:] - target_point[1])).argmin()
        target_data = data[..., trg_lat, trg_lon]
        extracted_data = self.grid.get_nearest_point(data, target_point)
        np.testing.assert_array_equal(target_data, extracted_data)

    def test_lonlatbox_returns_array(self):
        ll_lat, ll_lon = self.grid._calc_lat_lon()
        data = np.random.normal(size=[5,]+list(ll_lat.shape))
        target_box = (0, 10, 10, 0)
        extracted_data, _ = self.grid.lonlatbox(data, target_box)
        self.assertIsInstance(extracted_data, np.ndarray)

    def test_lonlatbox_raises_error_if_dim_shape_is_not_same(self):
        ll_lat, ll_lon = self.grid._calc_lat_lon()
        data = np.random.normal(size=[5, 4, 4])
        target_box = (0, 10, 10, 0)
        with self.assertRaises(ValueError):
            self.grid.lonlatbox(data, target_box)

    def test_lonlatbox_returns_new_grid_as_second(self):
        ll_lat, ll_lon = self.grid._calc_lat_lon()
        data = np.random.normal(size=[5,]+list(ll_lat.shape))
        target_box = (0, 10, 10, 0)
        _, new_grid = self.grid.lonlatbox(data, target_box)
        self.assertIsInstance(new_grid, LonLatGrid)
        self.assertNotEqual(id(self.grid), id(new_grid))

    def test_lonlatbox_raises_error_if_target_box_has_wrong_size(self):
        ll_lat, ll_lon = self.grid._calc_lat_lon()
        data = np.random.normal(size=[5,]+list(ll_lat.shape))
        with self.assertRaises(ValueError):
            self.grid.lonlatbox(data, (0, 10, 10))
            self.grid.lonlatbox(data, (0, 10, 10, 0, 0))

    def test_lonlatbox_slices_lon_lat_from_data(self):
        calc_lat, calc_lon = self.grid._construct_dim()
        ll_lat, ll_lon = self.grid._calc_lat_lon()
        data = np.random.normal(size=[5,]+list(ll_lat.shape))
        target_box = (0, 10, 10, 0)
        lat_bound = np.logical_and(calc_lat >= target_box[3],
                                   calc_lat <= target_box[1])
        lon_bound = np.logical_and(calc_lon >= target_box[0],
                                   calc_lon <= target_box[2])
        extracted_data, _ = self.grid.lonlatbox(data, target_box)
        target_data = data[..., lat_bound, lon_bound]
        np.testing.assert_array_equal(extracted_data, target_data)

    def test_lonlatbox_returns_new_grid_with_right_values(self):
        calc_lat, calc_lon = self.grid._construct_dim()
        ll_lat, ll_lon = self.grid._calc_lat_lon()
        data = np.random.normal(size=[5,]+list(ll_lat.shape))
        target_box = (0, 10, 10, 0)
        _, new_grid = self.grid.lonlatbox(data, target_box)
        lat_bound = np.logical_and(calc_lat >= target_box[3],
                                   calc_lat <= target_box[1])
        lon_bound = np.logical_and(calc_lon >= target_box[0],
                                   calc_lon <= target_box[2])
        new_lat = calc_lat[lat_bound]
        new_lon = calc_lon[lon_bound]
        self.assertEqual(new_grid._grid_dict['ysize'], len(new_lat))
        self.assertEqual(new_grid._grid_dict['xsize'], len(new_lon))
        np.testing.assert_array_equal(
            new_grid._grid_dict['yvals'], new_lat
        )
        np.testing.assert_array_equal(
            new_grid._grid_dict['xvals'], new_lon
        )
        self.assertNotIn('xfirst', new_grid._grid_dict)
        self.assertNotIn('yfirst', new_grid._grid_dict)


if __name__ == '__main__':
    unittest.main()
