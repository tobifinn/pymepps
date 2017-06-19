#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 19.06.17
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
import logging

# External modules
import xarray as xr


# Internal modules
from .netcdfhandler import NetCDFHandler


logger = logging.getLogger(__name__)


class OpendapHandler(NetCDFHandler):
    def open(self):
        if self.ds is None:
            try:
                self.ds = xr.open_dataset(self.file, engine='pydap')
            except (ImportError, ModuleNotFoundError):
                raise ImportError(
                    'The pydap package is not installed, please use instead '
                    'the NetCDFHandler if netCDF4 is installed!')
        return self

    def is_type(self):
        try:
            self.open()
            self.close()
            return True
        except (OSError, ImportError, ModuleNotFoundError):
            return False
