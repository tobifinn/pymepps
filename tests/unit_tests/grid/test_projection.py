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
import pyproj

# Internal modules
from pymepps.grid import GridBuilder
from pymepps.grid.projection import ProjectionGrid
from pymepps.grid.projection import RotPoleProj


logging.basicConfig(level=logging.DEBUG)

BASE_PATH = os.path.dirname(os.path.realpath(__file__))


class TestProjectionGrid(unittest.TestCase):
    def setUp(self):
        file = os.path.join(BASE_PATH, 'test_grids', 'llc')
        builder = GridBuilder(file)
        self.grid_dict = builder.griddes
        self.grid = builder.build_grid()

    def const_lat_lon(self, first, steps, width):
        return np.arange(
            first,
            first+ steps * width,
            width
        )

    def test_construct_dim_calcs_dim_y_x(self):
        calculated_y_x = self.grid._construct_dim()
        x = self.const_lat_lon(
            self.grid_dict['xfirst'],
            self.grid_dict['xsize'],
            self.grid_dict['xinc']
        )
        y = self.const_lat_lon(
            self.grid_dict['yfirst'],
            self.grid_dict['ysize'],
            self.grid_dict['yinc']
        )
        np.testing.assert_array_equal(
            y,
            calculated_y_x[0])
        np.testing.assert_array_equal(
            x,
            calculated_y_x[1])

    def test_calc_lat_lon_calc_lat_lon(self):
        calculated_lat_lon = self.grid._calc_lat_lon()
        x = self.const_lat_lon(
            self.grid_dict['xfirst'],
            self.grid_dict['xsize'],
            self.grid_dict['xinc']
        )
        y = self.const_lat_lon(
            self.grid_dict['yfirst'],
            self.grid_dict['ysize'],
            self.grid_dict['yinc']
        )
        y, x = np.meshgrid(y, x)
        p = pyproj.Proj(self.grid_dict['proj4'])
        lon, lat = p(x.transpose(), y.transpose(), inverse=True)
        np.testing.assert_array_equal(
            lat,
            calculated_lat_lon[0])
        np.testing.assert_array_equal(
            lon,
            calculated_lat_lon[1])

    def test_get_projection_accepts_proj4(self):
        grid_dict = {
            'proj4': '+proj=lcc +lat_0=63 +lon_0=15 +lat_1=63 +lat_2=63 '
                     '+no_defs +R=6.371e+06',
        }
        grid = ProjectionGrid(grid_dict)
        test_proj = pyproj.Proj(grid_dict['proj4'])
        returned_proj = grid.get_projection()
        lon, lat = 10, 53.5
        np.testing.assert_array_equal(
            test_proj(lon, lat), returned_proj(lon, lat))

    def test_get_projection_accepts_rotated_pole(self):
        grid_dict = {
            'grid_mapping': 'rotated_pole',
            'grid_north_pole_longitude': -170.415,
            'grid_north_pole_latitude': 36.0625,
        }
        grid = ProjectionGrid(grid_dict)
        returned_proj = grid.get_projection()
        self.assertIsInstance(returned_proj, RotPoleProj)
        self.assertEqual(returned_proj.north_pole['lat'], 36.0625)
        self.assertEqual(returned_proj.north_pole['lon'], -170.415)



if __name__ == '__main__':
    unittest.main()