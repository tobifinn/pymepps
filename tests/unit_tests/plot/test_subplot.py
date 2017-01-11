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
import unittest

# External modules
import matplotlib.pyplot as plt
import matplotlib.gridspec

import numpy.testing

# Internal modules
from pymepps.plot.subplot import Subplot
from pymepps.utilities.testcase import TestCase


class TestSubplot(TestCase):
    def setUp(self):
        self.subplot_type = Subplot

    def tearDown(self):
        plt.close('all')

    def test_axes_is_plt_subplot(self):
        sp = self.subplot_type()
        self.assertIsInstance(sp.ax, type(plt.subplot()))

    def test_attributes_from_mpl_axes(self):
        sp = self.subplot_type()
        self.assertAttribute(sp, 'set_xlim')

    def test_gridspec_as_parameter(self):
        sp = self.subplot_type()
        gs = matplotlib.gridspec.GridSpec(4,4)
        sp_gs = self.subplot_type(None, gs[3])
        self.assertNotEqual(sp.get_subplotspec().get_geometry(),
                            sp_gs.get_subplotspec().get_geometry())

    def test_plot_method_return_self(self):
        sp = self.subplot_type()
        after_sp = sp.plot_method(data=(range(10), range(10)))
        self.assertEqual(sp, after_sp)

    def test_plot_method_not_empty(self):
        sp = self.subplot_type()
        self.assertGreaterEqual(len(sp._plot_methods), 1)

    def test_plot_method(self):
        sp = self.subplot_type()
        sp.plot(data=(range(10), range(10)))
        plot_data = sp.ax.lines[0].get_data()
        sp = self.subplot_type()
        sp.plot_method(data=(range(10), range(10)), method='plot')
        method_data = sp.ax.lines[0].get_data()
        numpy.testing.assert_array_equal(plot_data, method_data)

    def test_not_available_plot_method_raises(self):
        sp = self.subplot_type()
        with self.assertRaises(ValueError):
            sp.plot_method(data=(range(10), range(10)), method='plot12')

    def test_not_available_stylesheet_raises_error(self):
        with self.assertRaises(ValueError):
            self.subplot_type(stylesheets=['fivethirtyeight32'])

    def test_stylesheets_none_basis_stylesheet(self):
        sp = self.subplot_type()
        numpy.testing.assert_array_equal(sp.stylesheets, ['default'])

if __name__ == '__main__':
    unittest.main()