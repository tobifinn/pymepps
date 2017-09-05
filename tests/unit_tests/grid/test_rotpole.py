#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 20.04.17

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
import os
import unittest
import logging

# External modules
import numpy as np

# Internal modules
from pymepps.grid.projection import RotPoleProj


BASE_PATH = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.realpath(__file__))))),
    'data')

logging.basicConfig(level=logging.DEBUG)


class TestRotPole(unittest.TestCase):
    def setUp(self):
        self.proj = RotPoleProj(npole_lat=36, npole_lon=-170)
        self.lat_lon = [
            (10, 54),
            (111.30919915667666, 40.106264596208376),
            (10, -6)
        ]
        self.rot_lat_lon = [
            (0, 0),
            (60, 30),
            (0, -60)
        ]

    def test_transform_to_lat_lon(self):
        for k, v in enumerate(self.rot_lat_lon):
            returned = self.proj.transform_to_lonlat(*v)
            np.testing.assert_almost_equal(returned, self.lat_lon[k])

    def test_transform_from_lat_lon(self):
        for k, v in enumerate(self.lat_lon):
            returned = self.proj.transform_from_lonlat(*v)
            np.testing.assert_almost_equal(returned, self.rot_lat_lon[k])

    def test_transform_with_normal_pole(self):
        proj = RotPoleProj(90, 0)
        for k, v in enumerate(self.rot_lat_lon+self.lat_lon):
            returned_ll = proj.transform_to_lonlat(*v)
            np.testing.assert_almost_equal(returned_ll, v)
            returned_rotll = proj.transform_from_lonlat(*v)
            np.testing.assert_almost_equal(returned_ll, returned_rotll)

    def test_call_inverse_transform_to_lat_lon(self):
        for k, v in enumerate(self.rot_lat_lon):
            returned = self.proj(*v, inverse=True)
            np.testing.assert_almost_equal(returned, self.lat_lon[k])

    def test_call_transform_to_rot_lat_lon(self):
        for k, v in enumerate(self.lat_lon):
            returned = self.proj(*v)
            np.testing.assert_almost_equal(returned, self.rot_lat_lon[k])


if __name__ == '__main__':
    unittest.main()
