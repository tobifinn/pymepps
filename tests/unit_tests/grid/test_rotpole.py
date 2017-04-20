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


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

logging.basicConfig(level=logging.DEBUG)


class TestRotPole(unittest.TestCase):
    def setUp(self):
        self.proj = RotPoleProj(npole_lat=36, npole_lon=-170)

    def test_transform_to_lat_lon_pole(self):
        returned = self.proj.transform_to_latlon(90, 0)
        np.testing.assert_array_equal(returned, (36, -170))

    def test_transform_from_lat_lon_pole(self):
        returned = self.proj.transform_from_latlon(36, -170)
        np.testing.assert_array_equal(returned, (90, 0))

    #
    # def test_transform_from_lat_lon(self):
    #     transformed = self.proj.transform_from_latlon(36, -170)
    #     np.testing.assert_array_equal(transformed, (90, 0))
    #     returned = self.proj.transform_to_latlon(transformed[0], transformed[1])
    #     np.testing.assert_array_equal(returned, (36, -170))


if __name__ == '__main__':
    unittest.main()
