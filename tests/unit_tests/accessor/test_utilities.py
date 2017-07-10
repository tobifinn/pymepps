#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 06.07.17

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
import pandas as pd
import pandas.util.testing

# Internal modules
from pymepps.accessor.utilities import register_dataframe_accessor
from pymepps.accessor.utilities import register_series_accessor


logging.basicConfig(level=logging.DEBUG)

BASE_PATH = os.path.dirname(os.path.realpath(__file__))


class TestPandasAccessor(unittest.TestCase):
    def tearDown(self):
        try:
            del pd.DataFrame.pp
        except AttributeError:
            pass
        try:
            del pd.Series.pp
        except AttributeError:
            pass

    def test_series_accessor(self):
        @register_series_accessor('pp')
        class PostProcessing(object):
            def __init__(self, data):
                self.data = data
                self.test = 'test'

        test_series = pd.Series([1, 2, 3, 4])
        self.assertTrue(hasattr(test_series, 'pp'))
        self.assertEqual('test', test_series.pp.test)
        pd.util.testing.assert_series_equal(test_series.pp.data, test_series)
        test_dataframe = pd.DataFrame([1, 2, 3, 4])
        self.assertFalse(hasattr(test_dataframe, 'pp'))

    def test_dataframe_accessor(self):
        @register_dataframe_accessor('pp')
        class PostProcessing(object):
            def __init__(self, data):
                self.data = data
                self.test = 'test'

        test_dataframe = pd.DataFrame([1, 2, 3, 4])
        self.assertTrue(hasattr(test_dataframe, 'pp'))
        self.assertEqual('test', test_dataframe.pp.test)
        pd.util.testing.assert_frame_equal(
            test_dataframe.pp.data, test_dataframe)
        test_series = pd.Series([1, 2, 3, 4])
        self.assertFalse(hasattr(test_series, 'pp'))


if __name__ == '__main__':
    unittest.main()
