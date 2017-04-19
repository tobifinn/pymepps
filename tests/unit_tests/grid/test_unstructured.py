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

# Internal modules
from pymepps.grid import GridBuilder


logging.basicConfig(level=logging.DEBUG)

BASE_PATH = os.path.dirname(os.path.realpath(__file__))


class TestLatLonGrid(unittest.TestCase):
    def setUp(self):
        file = os.path.join(BASE_PATH, 'test_grids', 'unstructured')
        builder = GridBuilder(file)
        self.grid_dict = builder.griddes
        self.grid = builder.build_grid()

    def test_construct_dim_calcs_dim_lat_lon(self):
        calculated_lat_lon = self.grid._construct_dim()
        lon = self.grid_dict['xvals']
        lat = self.grid_dict['yvals']
        np.testing.assert_array_equal(
            lat,
            calculated_lat_lon[0])
        np.testing.assert_array_equal(
            lon,
            calculated_lat_lon[1])

if __name__ == '__main__':
    unittest.main()