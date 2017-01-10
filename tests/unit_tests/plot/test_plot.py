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
import matplotlib.figure
import matplotlib.gridspec

import numpy.testing

# Internal modules
from pymepps.plot.plot import BasePlot
from pymepps.plot.subplot import Subplot
from pymepps.utilities.testcase import TestCase


class TestPlot(TestCase):
    def layers_list_test(self, p):
        ax_type = Subplot
        self.assertTrue(any([isinstance(sub, ax_type) for sub in p.subplots]),
                    'Not all subplots are a Subplot instance')

    def test_baseplot_could_created(self):
        sp = BasePlot()
        self.assertIsInstance(sp, BasePlot)

    def test_figure_is_pyplot_figure(self):
        sp = BasePlot()
        self.assertIsInstance(sp.FIG, matplotlib.figure.Figure)

    def test_subplots_list(self):
        p = BasePlot()
        self.assertIsInstance(p.subplots, list)

    def test_gridspec_could_create(self):
        p = BasePlot(nrows=3, ncols=4)
        self.assertEqual(type(p.gs), matplotlib.gridspec.GridSpec)

    def test_gridspec_is_parameter(self):
        p = BasePlot(nrows=3, ncols=4)
        self.assertEqual((3,4), p.gs.get_geometry())

    def test_no_gridspec_given_single_subplot(self):
        p = BasePlot()
        self.assertIsNone(p.gs)
        self.assertEqual(len(p.subplots), 1)
        self.layers_list_test(p)

    def test_add_subplot_returns_baseplot_instance(self):
        p = BasePlot(1,1)
        p_after = p.add_subplot()
        self.assertEqual(p, p_after)

    def test_subplot_could_be_added(self):
        p = BasePlot()
        p.add_subplot()
        self.assertEqual(len(p.subplots), 2)
        self.layers_list_test(p)

    def test_subplot_type_could_be_set(self):
        p = BasePlot(1,1)
        self.assertAttribute(p, 'subplot_type')
        p.subplot_type = BasePlot
        p.add_subplot()
        self.assertIsInstance(p.subplots[0], BasePlot)

    def test_active_subplot_with_gs_is_none(self):
        p = BasePlot(1,1)
        self.assertIsNone(p.active_subplot)

    def test_active_subplot_set_automatically_to_last_added_subplot(self):
        p = BasePlot(1,1)
        p.add_subplot()
        self.assertEqual(p.active_subplot, p.subplots[-1])

    def test_active_subplot_could_be_set(self):
        p = BasePlot()
        p.add_subplot()
        last_active_sp = p.active_subplot
        p.active_subplot = 0
        self.assertNotEqual(p.active_subplot, last_active_sp)

    def test_active_subplot_only_allows_avail_int(self):
        p = BasePlot()
        p.add_subplot()
        with self.assertRaises(ValueError):
            p.active_subplot = 42

    def test_active_subplot_only_allows_int_none(self):
        p = BasePlot()
        p.add_subplot()
        with self.assertRaises(ValueError):
            p.active_subplot = 'tdd is cool'

    def test_args_and_kwargs_in_init_to_figure(self):
        figsize = (4,2)
        fignum = 42

        p = BasePlot(None, None, fignum, figsize=figsize)
        numpy.testing.assert_array_equal(p.FIG.get_size_inches(), figsize)
        self.assertEqual(p.FIG.number, fignum)

    def test_attributes_in_figure(self):
        p = BasePlot()
        self.assertAttribute(p, 'number')

    def test_attributes_in_active_subplot(self):
        p = BasePlot()
        self.assertAttribute(p, 'bla_function')


if __name__ == '__main__':
    unittest.main()