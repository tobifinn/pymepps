#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 06.07.17
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
import os
import unittest
import logging

# External modules
import xarray as xr

# Internal modules
import pymepps.accessor


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

logging.basicConfig(level=logging.DEBUG)


class TestSpatial(unittest.TestCase):
    def setUp(self):
        file = os.path.join(os.path.dirname(BASE_DIR), 'data', 'spatial',
                            'saved', 't2m.nc')
        self.array = xr.open_dataarray(file)

    def test_array_has_accessor(self):
        self.assertTrue(hasattr(self.array, 'pp'))

    def test_accessor_has_array_as_data(self):
        self.assertEqual(id(self.array.pp.data), id(self.array))

if __name__ == '__main__':
    unittest.main()
