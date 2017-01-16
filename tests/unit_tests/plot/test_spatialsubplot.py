#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 10.01.17

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
import os.path
import pickle
import unittest

# External modules
import numpy as np
import numpy.testing

# Internal modules
from pymepps.plot.spatial.spatialsubplot import SpatialSubplot
from .test_subplot import TestSubplot


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                __file__))))


RandomState = np.random.RandomState(42)


class TestSpatialSubplotPlot(TestSubplot):
    def setUp(self):
        super().setUp()
        self.subplot_type = SpatialSubplot
        self.test_data = (range(10), range(10),
                          RandomState.uniform(0, 1, (10,10)))

    def test_plot_method(self):
        pass

    def test_plot_method_return_self(self):
        sp = self.subplot_type()
        after_sp = sp.plot_method(data=self.test_data, method='contourf')
        self.assertEqual(sp, after_sp)

    def test_rendered_data_equals_line_data(self):
        sp = self.subplot_type()
        sp.plot_method(data=self.test_data, method='contourf')
        numpy.testing.assert_array_equal(
            self.test_data[2], sp.rendered_data[0][2])

    def test_extract_data_raises_error(self):
        sp = self.subplot_type()
        with self.assertRaises(ValueError):
            sp._extract_data(self.subplot_type())

    def test_extract_data_extracts_dataarray(self):
        file = os.path.join(BASE_DIR, 'test_data', 'spatial',
                            'test_spatialdata_dataarray.pk')
        test_data = pickle.load(open(file, mode='rb'))
        sp = self.subplot_type()
        x, y, plot_data = sp._extract_data(test_data)
        numpy.testing.assert_array_equal(test_data['lat'], x)
        numpy.testing.assert_array_equal(test_data['lon'], y)
        numpy.testing.assert_array_equal(test_data.values.squeeze(), plot_data)



if __name__ == '__main__':
    unittest.main()