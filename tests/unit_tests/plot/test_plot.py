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
import itertools
import unittest

# External modules
import matplotlib.pyplot as plt
import matplotlib.figure
import matplotlib.gridspec

import numpy as np
import numpy.testing

# Internal modules
from pymepps.plot.plot import BasePlot
from pymepps.plot.subplot import Subplot
from pymepps.utilities.testcase import TestCase


class TestPlot(TestCase):
    def setUp(self):
        self.plot_class = BasePlot
        self.subplot_type = Subplot

    def tearDown(self):
        plt.close("all")

    def test_baseplot_could_created(self):
        sp = self.plot_class()
        self.assertIsInstance(sp, self.plot_class)

    def test_figure_is_pyplot_figure(self):
        sp = self.plot_class()
        self.assertIsInstance(sp.FIG, matplotlib.figure.Figure)

    def test_subplots_list(self):
        p = self.plot_class()
        self.assertIsInstance(p.subplots, list)

    def test_gridspec_could_create(self):
        p = self.plot_class(nrows=3, ncols=4)
        self.assertEqual(type(p.gs), matplotlib.gridspec.GridSpec)

    def test_gridspec_is_parameter(self):
        p = self.plot_class(nrows=3, ncols=4)
        self.assertEqual((3,4), p.gs.get_geometry())

    def test_add_subplot_returns_baseplot_instance(self):
        p = self.plot_class(1,1)
        p_after = p.add_subplot()
        self.assertEqual(p, p_after)

    def test_subplot_could_be_added(self):
        p = self.plot_class(1,1)
        p.add_subplot()
        self.assertEqual(len(p.subplots), 1)
        self.assertTrue(any([isinstance(sub, self.subplot_type)
                             for sub in p.subplots]),
                    'Not all subplots are a Subplot instance')

    def test_subplot_type_could_be_set(self):
        p = self.plot_class(1,1)
        self.assertAttribute(p, 'subplot_type')
        p.subplot_type = Subplot
        p.add_subplot()
        self.assertIsInstance(p.subplots[0], Subplot)

    def test_active_subplot_with_gs_is_none(self):
        p = self.plot_class(1,1)
        self.assertIsNone(p.active_subplot)

    def test_active_subplot_set_automatically_to_last_added_subplot(self):
        p = self.plot_class(1,1)
        p.add_subplot()
        self.assertEqual(p.active_subplot, p.subplots[-1])

    def test_active_subplot_could_be_set(self):
        p = self.plot_class(2,1)
        p.add_subplot()
        p.add_subplot()
        last_active_sp = p.active_subplot
        p.active_subplot = 0
        self.assertNotEqual(p.active_subplot, last_active_sp)

    def test_active_subplot_only_allows_avail_int(self):
        p = self.plot_class()
        p.add_subplot()
        with self.assertRaises(ValueError):
            p.active_subplot = 42

    def test_active_subplot_only_allows_int_none(self):
        p = self.plot_class()
        p.add_subplot()
        with self.assertRaises(ValueError):
            p.active_subplot = 'tdd is cool'

    def test_args_and_kwargs_in_init_to_figure(self):
        figsize = (4,2)
        fignum = 42

        p = self.plot_class(1, 1, None, fignum, figsize=figsize)
        numpy.testing.assert_array_equal(p.FIG.get_size_inches(), figsize)
        self.assertEqual(p.FIG.number, fignum)

    def test_attributes_in_figure(self):
        p = self.plot_class()
        self.assertAttribute(p, 'number')

    def test_attributes_in_active_subplot(self):
        p = self.plot_class()
        p.add_subplot()
        self.assertAttribute(p, 'ax')

    def test_available_gs_has_all_possible_gs(self):
        p = self.plot_class(5, 4)
        self.assertEqual(p.available_gs, list(np.ndindex(5, 4)))

    def test_add_subplot_gs_information(self):
        gs_size = (4,3)
        subplot_bounds = (0, -2, 1, -1)
        p = self.plot_class(*gs_size)
        p.add_subplot(subplot_bounds)

        test_gs = matplotlib.gridspec.GridSpec(*gs_size)
        test_subplot_spec = test_gs[
                            subplot_bounds[0]:subplot_bounds[2],
                            subplot_bounds[1]:subplot_bounds[3]]
        self.assertEqual(test_subplot_spec.get_geometry(),
                         p.get_subplotspec().get_geometry())

    def test_add_subplot_gs_none_next_gs(self):
        p = self.plot_class(4,3)
        p.add_subplot()
        np.testing.assert_array_equal(p.get_subplotspec().get_geometry()[-2:],
                                      (0,0))

    def test_add_subplot_deletes_used_gs_none(self):
        size = (4,3)
        p = self.plot_class(*size)
        p.add_subplot()
        gs_list = list(np.ndindex(*size))
        gs_list.pop(0)
        np.testing.assert_array_equal(gs_list,
                                      p.available_gs)

    def test_add_subplot_deletes_used_gs_int(self):
        size = (4,3)
        p = self.plot_class(*size)
        p.add_subplot(3)
        gs_list = list(np.ndindex(*size))
        gs_list.pop(3)
        np.testing.assert_array_equal(gs_list,
                                      p.available_gs)

    def test_add_subplot_deletes_used_gs_tuple(self):
        size = (4,3)
        subplot_bounds = (0, -2, 1, -1)
        p = self.plot_class(*size)
        p.add_subplot(subplot_bounds)
        gs_list = list(np.ndindex(*size))
        selected_gs = list(
            itertools.product(range(subplot_bounds[0], subplot_bounds[2]),
                              range(subplot_bounds[1], subplot_bounds[3])))
        gs_list = [gs for gs in gs_list if gs not in selected_gs]
        np.testing.assert_array_equal(gs_list,
                                      p.available_gs)

    def test_add_subplot_wrong_gs_nr_raises(self):
        p = self.plot_class(4,3)
        with self.assertRaises(ValueError):
            p.add_subplot('bla')

    def test_add_subplot_deletes_used_gs_tuple_nonw(self):
        size = (4,3)
        subplot_bounds = (0, -2, 1, -1)
        p = self.plot_class(*size)
        p.add_subplot(subplot_bounds)
        gs_list = list(np.ndindex(*size))
        selected_gs = list(
            itertools.product(range(subplot_bounds[0], subplot_bounds[2]),
                              range(subplot_bounds[1], subplot_bounds[3])))
        gs_list = [gs for gs in gs_list if gs not in selected_gs]
        p.add_subplot()
        gs_list.pop(0)
        np.testing.assert_array_equal(gs_list,
                                      p.available_gs)

    def test_set_default_stylesheet_if_none(self):
        p = self.plot_class()
        self.assertEqual(p.stylesheets, ['ggplot'])

    def test_set_stylesheets(self):
        p = self.plot_class(stylesheets=['fivethirtyeight', 'ggplot'])
        self.assertEqual(p.stylesheets, ['fivethirtyeight', 'ggplot'])

    def test_stylesheets_valueerror_not_available(self):
        with self.assertRaises(ValueError):
            p = self.plot_class(stylesheets=['fivethirtyeight12', 'ggplot'])


if __name__ == '__main__':
    unittest.main()