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
import pandas as pd
import numpy as np

# Internal modules
from pymepps.accessor.series import SeriesAccessor


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

    def test_update_data_updates_unnamed_series(self):
        test_series = self.series.copy()
        test_series[:] = 0
        self.series = self.series.pp.update(test_series)
        self.assertTrue(np.all(np.equal(self.series.values, 0)))

    def test_update_updates_same_names_series(self):
        test_series = self.series.copy()
        test_series[:] = 0
        test_series.name = 'test_series'
        self.series.name = 'test_series'
        self.series = self.series.pp.update(test_series)
        self.assertTrue(np.all(np.equal(self.series.values, 0)))

    def test_update_updates_unnamed_named_series(self):
        test_series = self.series.copy()
        test_series[:] = 0
        test_series.name = 'test_series'
        returned_series = self.series.pp.update(test_series)
        self.assertTrue(np.all(np.equal(self.series.values, 0)))
        self.assertTrue(self.series.name, test_series.name)

    def test_update_updates_named_unnamed_series(self):
        test_series = self.series.copy()
        test_series[:] = 0
        self.series.name = 'test_series'
        self.series = self.series.pp.update(test_series)
        self.assertTrue(np.all(np.equal(self.series.values, 0)))

    def test_update_transforms_different_named_series_to_frame(self):
        test_series = self.series.copy()
        test_series[:] = 0
        test_series.name = 'test_series'
        self.series.name = 'test_series2'
        self.series = self.series.pp.update(test_series)
        self.assertTrue(np.all(np.equal(self.series.values, 0)))




if __name__ == '__main__':
    unittest.main()
