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
from copy import deepcopy
import logging

# External modules
import matplotlib.pyplot as plt
import matplotlib.gridspec

# Internal modules
from .subplot import Subplot


logger = logging.getLogger(__name__)


class BasePlot(object):
    def __init__(self, nrows=None, ncols=None, *args, **kwargs):
        """
        BasePlot is base class as wrapper around matplotlib
        """
        self._gs = None
        self._active_sp_id = None

        self.subplot_type = Subplot
        self.FIG = plt.figure(*args, **kwargs)
        self.active_subplot = None
        self.subplots = []
        self.gs = (nrows, ncols)

    def __getattr__(self, item):
        try:
            return getattr(self.FIG, item)
        except AttributeError:
            return getattr(self.active_subplot, item)

    @property
    def active_subplot(self):
        if isinstance(self._active_sp_id, int):
            return self.subplots[self._active_sp_id]
        else:
            return None

    @active_subplot.setter
    def active_subplot(self, id):
        if id is None:
            self._active_sp_id = None
        elif id not in range(len(self.subplots)):
            raise ValueError('The chosen active subplot is not available. '
                             'The last available subplot id is {0:d}'.
                             format(len(self.subplots)-1))
        else:
            self._active_sp_id = id

    @property
    def gs(self):
        return self._gs

    @gs.setter
    def gs(self, gs_shape):
        if all([shp is None for shp in gs_shape]):
            self._gs = None
            self.add_subplot()
        else:
            self._gs = matplotlib.gridspec.GridSpec(nrows=gs_shape[0],
                                                    ncols=gs_shape[1])

    def add_subplot(self):
        self.subplots.append(deepcopy(self.subplot_type)())
        self.active_subplot = len(self.subplots)-1
        return self
