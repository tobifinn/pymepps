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
import json

# External modules
import pandas as pd
import numpy as np

# Internal modules
from pymepps.accessor.pandas import PandasAccessor


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

logging.basicConfig(level=logging.DEBUG)

RandomState = np.random.RandomState(42)


class TestSeries(unittest.TestCase):
    def setUp(self):
        time_range = pd.date_range('2016-01-01', '2017-01-01', tz='UTC')
        series_data = RandomState.normal(size=(len(time_range),))
        self.series = pd.Series(data=series_data, index=time_range)
        frame_data = RandomState.normal(size=(len(time_range), 2))
        self.frame = pd.DataFrame(data=frame_data, index=time_range,
                                  columns=['test', 'bla'])

    def tearDown(self):
        if os.path.isfile('test.json'):
            os.remove('test.json')

    def test_data_is_data(self):
        self.assertEqual(id(self.series), id(self.series.pp.data))
        self.assertEqual(id(self.frame), id(self.frame.pp.data))

    def test_repr_includes_lonlat(self):
        lonlat = (10, 53.5)
        self.series.pp.lonlat = lonlat
        self.assertEqual(
            '{0:s}(lonlat: {1:s})'.format(self.series.__class__.__name__,
                                          str(lonlat)),
            repr(self.series.pp))
        self.frame.pp.lonlat = lonlat
        self.assertEqual(
            '{0:s}(lonlat: {1:s})'.format(self.frame.__class__.__name__,
                                          str(lonlat)),
            repr(self.frame.pp))

    def test_save_saves_creates_path(self):
        self.assertFalse(os.path.isfile('test.json'))
        self.series.pp.save('test.json')
        self.assertTrue(os.path.isfile('test.json'))

    def test_save_creates_valid_json(self):
        self.series.pp.save('test.json')
        with open('test.json', 'r') as fh:
            json_str = fh.read()
        decoded_dict = json.loads(json_str)
        self.assertIsInstance(decoded_dict, dict)

    def test_save_saves_data_and_lonlat(self):
        self.series.pp.save('test.json')
        with open('test.json', 'r') as fh:
            json_str = fh.read()
        decoded_dict = json.loads(json_str)
        self.assertIn('lonlat', decoded_dict.keys())
        self.assertIn('data', decoded_dict.keys())

    def test_save_saves_lonlat_as_tuple(self):
        self.series.pp.save('test.json')
        with open('test.json', 'r') as fh:
            json_str = fh.read()
        decoded_dict = json.loads(json_str)

if __name__ == '__main__':
    unittest.main()
