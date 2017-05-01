#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 01.05.17
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
import xarray as xr
import numpy as np

# Internal modules
from pymepps.metdata import SpatialDataset
from pymepps.metfile import NetCDFHandler


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

logging.basicConfig(level=logging.DEBUG)


class TestSpatialDS(unittest.TestCase):
    def setUp(self):
        self.file = '/home/tfinn/Data/master_thesis/test_data/nc/20160607_' \
                    '0000/det/lfff00000000.nc'
        self.handler = NetCDFHandler(self.file)
        self.ds = SpatialDataset([self.handler,])
        self.xr_ds = xr.open_dataset(self.file)

    def tearDown(self):
        self.handler.close()

    def test_data_merge(self):
        self.handler.open()
        messages = self.handler.get_messages('T')
        self.ds.data_merge(messages, 'T')


if __name__ == '__main__':
    unittest.main()
