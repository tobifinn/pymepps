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
from pymepps.grid.grid import Grid


logging.basicConfig(level=logging.DEBUG)

BASE_PATH = os.path.dirname(os.path.realpath(__file__))


class TestGrid(unittest.TestCase):
    def setUp(self):
        grids_path = os.path.join(BASE_PATH, 'test_grids', '*')
        self.available_grids = glob.glob(grids_path)
        self.grid = Grid()

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
        test_str = 'lat=10, lon=11\n'
        returned_str = self.grid.open_string(test_str)
        self.assertEqual(returned_str, test_str)

    def test_decode_str_return_key_value_from_mapping(self):
        test_str = 'key=value'
        returned_dict = self.grid.decode_str(test_str)
        self.assertIsInstance(returned_dict, dict)
        self.assertEqual(returned_dict, dict(key='value'))

    def test_decode_str_return_key_value_with_new_line(self):
        test_str = 'key=value\nkey1=value'
        returned_dict = self.grid.decode_str(test_str)
        self.assertEqual(returned_dict, dict(key='value', key1='value'))

    def test_decode_str_skips_comment_lines(self):
        test_str = '# I\'m a comment line\n# Second comment line = key value ' \
                   'test\nkey=value'
        returned_dict = self.grid.decode_str(test_str)
        self.assertEqual(returned_dict, dict(key='value'))

    def test_decode_str_removes_spaces_and_special_characters(self):
        test_str = 'key1=value\n # Second comment line = "key" value test\n ' \
                   'key  =[value]! '
        returned_dict = self.grid.decode_str(test_str)
        self.assertEqual(returned_dict, dict(key1='value', key='value'))

    def test_decode_str_lowers_caps(self):
        test_str = 'Key=VaLue'
        returned_dict = self.grid.decode_str(test_str)
        self.assertEqual(returned_dict, dict(key='value'))

    def test_decode_str_raises_loggerwarning_if_no_key_value(self):
        test_str = 'Key\nkey=value'
        returned_dict = self.grid.decode_str(test_str)
        self.assertEqual(returned_dict, dict(key='value'))

    def test_decode_str_decodes_to_float(self):
        test_str = 'Key\nkey=value\nkey2=2.0'
        returned_dict = self.grid.decode_str(test_str)
        self.assertEqual(returned_dict, dict(key='value', key2=2.0))

    @staticmethod
    def decode_grid_file(grid_str):
        lined_grid_str = grid_str.split('\n')
        cleaned_lines = [re.sub('[^0-9a-zA-Z=#-\.]+', '', gs).lower()
                         for gs in lined_grid_str]
        grid_dict = dict(gs.split('=')for gs in cleaned_lines
                         if len(gs) > 0
                         and gs[0] != '#'
                         and len(gs.split('=')) > 1)
        for k in grid_dict:
            try:
                grid_dict[k] = float(grid_dict[k])
            except ValueError:
                pass
        return grid_dict

    def test_decode_grid_file_str(self):
        for grid_path in self.available_grids:
            grid_str = self.grid.open_string(grid_path)
            returned_dict = self.grid.decode_str(grid_str)
            grid_dict = self.decode_grid_file(grid_str)
            self.assertEqual(returned_dict, grid_dict)

    def test_griddes_decodes_str_to_grid_des(self):
        for grid_path in self.available_grids:
            self.grid.griddes = grid_path
            decoded_grid = self.grid.decode_str(
                self.grid.open_string(grid_path))
            self.assertEqual(self.grid.griddes, decoded_grid)

    def test_griddes_raises_typeerror_if_no_str_none_dict(self):
        test = [2124,46386586,'bla']
        with self.assertRaises(TypeError):
            self.grid.griddes = test


if __name__ == '__main__':
    unittest.main()
