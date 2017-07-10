#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 01.05.17
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
import numpy as np

# Internal modules
from pymepps.metfile import NetCDFHandler


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__))))

logging.basicConfig(level=logging.DEBUG)


class TestNCHandler(unittest.TestCase):
    def setUp(self):
        self.file = '/home/tfinn/Data/master_thesis/test_data/nc/20160607_' \
                    '0000/det/lfff00000000.nc'
        self.handler = NetCDFHandler(self.file)
        self.xr_ds = xr.open_dataset(self.file)

    def tearDown(self):
        self.handler.close()
        self.xr_ds.close()

    def test_get_var_names_returns_var_names(self):
        returned_var_names = self.handler._get_varnames()
        np.testing.assert_array_equal(list(self.xr_ds.data_vars),
                                      returned_var_names)

    def test_is_type_returns_true_if_type(self):
        self.assertTrue(self.handler.is_type())

    def test_is_type_returns_false_if_not_type(self):
        handler = NetCDFHandler(os.path.join(BASE_DIR, 'README.rst'))
        self.assertFalse(handler.is_type())

    def test_open_open_xr_dataset(self):
        self.assertIsNone(self.handler.ds)
        self.handler.open()
        xr.testing.assert_equal(self.xr_ds, self.handler.ds)
        self.handler.close()

    def test_close_closes_dataset(self):
        self.handler.open()
        self.assertIsInstance(str(self.handler.ds), str)
        self.handler.close()
        with self.assertRaises(AssertionError):
            str(self.handler.ds)

    def test_close_raises_no_attribute_error(self):
        self.handler.ds = None
        self.handler.close()

    def test_load_cube_loads_cube(self):
        self.handler.open()
        loaded_var = self.handler.load_cube('T')
        xr.testing.assert_equal(self.xr_ds['T'], loaded_var)

    def test_get_messages_splits_messages(self):
        self.handler.open()
        returned_cubes = self.handler.get_messages('T')
        testing_cube = self.xr_ds['T'].squeeze()[0, :, :]
        returned_cube = returned_cubes[0].squeeze()
        xr.testing.assert_equal(returned_cube, testing_cube)

if __name__ == '__main__':
    unittest.main()
