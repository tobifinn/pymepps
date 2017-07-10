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
import numpy as np
import numpy.testing

# Internal modules
from pymepps.plot.spatial.spatialplot import SpatialPlot
from pymepps.plot.spatial.spatialsubplot import SpatialSubplot
from .test_plot import TestPlot


RandomState = np.random.RandomState(42)


class TestSpatialPlot(TestPlot):
    def setUp(self):
        super().setUp()
        self.plot_class = SpatialPlot
        self.subplot_type = SpatialSubplot
        self.testing_data = (range(10), range(10),
                          RandomState.uniform(0, 1, (10,10)))

    def test_rendered_data_subplots(self):
        pass


if __name__ == '__main__':
    unittest.main()