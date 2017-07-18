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

BASE_PATH = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.realpath(__file__)))),
    'data')


class TestUnstructuredGrid(unittest.TestCase):
    def setUp(self):
        file = os.path.join(BASE_PATH, 'grids', 'unstructured')
        builder = GridBuilder(file)
        self.grid_dict = builder.griddes
        self.grid = builder.build_grid()

    def test_construct_dim_calcs_dim_lat_lon(self):
        constructed_dim = self.grid._construct_dim()
        np.testing.assert_array_equal(
            np.arange(self.grid._grid_dict['gridsize']),
            constructed_dim)

    def test__calc_lat_lon_gets_lat_lon(self):
        returned_lat, returned_lon = self.grid._calc_lat_lon()
        np.testing.assert_array_equal(
            returned_lat,
            self.grid._grid_dict['yvals']
        )
        np.testing.assert_array_equal(
            returned_lon,
            self.grid._grid_dict['xvals']
        )

if __name__ == '__main__':
    unittest.main()