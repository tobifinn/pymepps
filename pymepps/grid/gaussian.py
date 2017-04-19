#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 10.04.17
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

# Internal modules
from .lonlat import LonLatGrid


logger = logging.getLogger(__name__)


class GaussianGrid(LonLatGrid):
    """
    The gaussian grid is similar to the lonlat grid. This is the right grid if
    longitude and/or latitude could be described with a non-evenly distributed
    list of values. 
    """
    def _construct_dim(self):
        lonlat = []
        for dim in ('y', 'x'):
            vals = self._grid_dict.get("{0:s}vals".format(dim), None)
            if vals is None:
                try:
                    vals = self._calc_single_dim(dim)
                except KeyError as e:
                    raise KeyError(
                        'It is necessary to deliver either {0:s}vals or'
                        '({0:s}first, {0:s}size and {0:s}inc)'.format(dim))
            lonlat.append(vals)
        return lonlat[0], lonlat[1]
