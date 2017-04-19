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
import glob
import re

# External modules
import numpy as np
import xarray as xr

# Internal modules
from pymepps.grid.builder import GridBuilder
from pymepps.grid.curvilinear import CurvilinearGrid


logging.basicConfig(level=logging.DEBUG)

BASE_PATH = os.path.dirname(os.path.realpath(__file__))


class TestGridBuilder(unittest.TestCase):
    def setUp(self):
        grids_path = os.path.join(BASE_PATH, 'test_grids', '*')
        self.available_grids = glob.glob(grids_path)
        self.grid = GridBuilder

    def test_get_string_from_file_opens_file_return_string(self):
        for grid_path in self.available_grids:
            with open(grid_path, 'r') as gf:
                grid_string = gf.read()
            returned_string = self.grid.open_string(grid_path)
            self.assertEqual(grid_string, returned_string)

    def test_get_string_raises_type_error_if_no_str_or_dict(self):
        with self.assertRaises(TypeError):
            self.grid.open_string(None)

    def test_get_string_returns_str_if_could_not_opened(self):
        test_str = 'lat=10\nlon=11\ngridtype=lonlat'
        returned_str = self.grid.open_string(test_str)
        self.assertEqual(returned_str, test_str)

    def test_decode_str_return_key_value_from_mapping(self):
        test_str = 'gridtype=lonlat'
        returned_dict = self.grid.decode_str(test_str)
        self.assertIsInstance(returned_dict, dict)
        self.assertEqual(returned_dict, dict(gridtype='lonlat'))

    def test_decode_str_return_key_value_with_new_line(self):
        test_str = 'gridtype=lonlat\nkey1=value'
        returned_dict = self.grid.decode_str(test_str)
        self.assertEqual(returned_dict, dict(gridtype='lonlat', key1='value'))

    def test_decode_str_decodes_also_list_with_str(self):
        test_list = ['gridtype=lonlat', 'key1=value']
        returned_dict = self.grid.decode_str(test_list)
        self.assertEqual(returned_dict, dict(gridtype='lonlat', key1='value'))

    def test_decode_str_takes_only_str_and_list_raises_type_error(self):
        test_dict = None
        with self.assertRaises(TypeError):
            self.grid.decode_str(test_dict)

    def test_decode_str_skips_comment_lines(self):
        test_str = '# I\'m a comment line\n# Second comment line = key value ' \
                   'test\ngridtype=lonlat'
        returned_dict = self.grid.decode_str(test_str)
        self.assertEqual(returned_dict, dict(gridtype='lonlat'))

    def test_decode_str_removes_spaces_and_special_characters(self):
        test_str = 'key1=value\n # Second comment line = "key" value test\n ' \
                   'gridtype=[lonlat]! '
        returned_dict = self.grid.decode_str(test_str)
        self.assertEqual(returned_dict, dict(key1='value', gridtype='lonlat'))

    def test_decode_str_lowers_caps(self):
        test_str = 'GRidtype=LonlaT'
        returned_dict = self.grid.decode_str(test_str)
        self.assertEqual(returned_dict, dict(gridtype='lonlat'))

    def test_decode_str_raises_loggerwarning_if_no_key_value(self):
        test_str = 'Key\ngridtype=lonlat'
        returned_dict = self.grid.decode_str(test_str)
        self.assertEqual(returned_dict, dict(gridtype='lonlat'))

    def test_decode_str_decodes_to_float(self):
        test_str = 'Key\ngridtype=lonlat\nkey2=2.0'
        returned_dict = self.grid.decode_str(test_str)
        self.assertEqual(returned_dict, dict(gridtype='lonlat', key2=2.0))

    @staticmethod
    def decode_grid_file(grid_str):
        lined_grid_str = grid_str.split('\n')
        cleaned_lines = [re.sub('[^0-9a-zA-Z=#-\. ]+', '', gs).lower()
                         for gs in lined_grid_str]
        splitted_lines = [line.split('=') for line in cleaned_lines if len(line) > 0 and line[0] != '#']
        for i in np.arange(len(splitted_lines)-1, -1, -1):
            if len(splitted_lines[i])==1 and i!=0:
                splitted_lines[i-1][-1] = "{0:s} {1:s}".format(
                    splitted_lines[i - 1][-1], splitted_lines[i][-1])
        grid_dict = {line[0].replace(' ', ''): list(filter(None, line[1].split(' ')))
                     for line in splitted_lines if len(line)==2}
        for k in grid_dict:
            try:
                grid_dict[k] = [float(val) for val in grid_dict[k]]
            except ValueError:
                pass
            if len(grid_dict[k])==1:
                grid_dict[k] = grid_dict[k][0]
        return grid_dict

    def test_decode_grid_file_str(self):
        for grid_path in self.available_grids:
            grid_str = self.grid.open_string(grid_path)
            returned_dict = self.grid.decode_str(grid_str)
            grid_dict = self.decode_grid_file(grid_str)
            self.assertEqual(returned_dict, grid_dict)

    def test_griddes_decodes_str_to_grid_des(self):
        for grid_path in self.available_grids:
            grid = GridBuilder(griddes=grid_path)
            decoded_grid = self.grid.decode_str(
                self.grid.open_string(grid_path))
            self.assertEqual(grid.griddes, decoded_grid)

    def test_griddes_raises_typeerror_if_no_str_none_dict(self):
        grid = GridBuilder('gridtype=lonlat')
        test = [2124,46386586,'bla']
        with self.assertRaises(TypeError):
            grid.griddes = test
        self.assertEqual(grid._grid_dict, dict(gridtype='lonlat'))

    def test_griddes_set_dict_to_grid_dict(self):
        grid = GridBuilder('gridtype=lonlat')
        test_dict = dict(gridtype='lonlat', lon0=10.3)
        grid.griddes = test_dict
        self.assertEqual(grid._grid_dict, test_dict)

    def test_set_grid_handler_raises_keyerror_if_no_gridtype(self):
        grid = GridBuilder('gridtype=lonlat')
        with self.assertRaises(KeyError):
            grid._set_grid_handler({'key': 'value'})

    def test_set_grid_handler_raises_valueerror_if_wrong_gridtype(self):
        grid = GridBuilder('gridtype=lonlat')
        with self.assertRaises(ValueError):
            grid._set_grid_handler({'gridtype': 'gausslat'})

    def test_set_grid_handler_set_decoder(self):
        grid = GridBuilder('gridtype=lonlat')
        grid._set_grid_handler({'gridtype': 'curvilinear'})
        self.assertEqual(grid._grid_handler.__class__.__name__,
                         CurvilinearGrid.__class__.__name__)

    def test_build_grid(self):
        grid_builder = GridBuilder('gridtype=lonlat')
        grid_builder._set_grid_handler({'gridtype': 'curvilinear'})
        grid = grid_builder.build_grid()
        self.assertIsInstance(grid, CurvilinearGrid)


if __name__ == '__main__':
    unittest.main()
