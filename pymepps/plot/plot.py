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
import collections
import itertools
import logging

# External modules
import matplotlib.pyplot as plt
import matplotlib.gridspec

import numpy as np

# Internal modules
from .subplot import Subplot


logger = logging.getLogger(__name__)


class BasePlot(object):
    def __init__(self, nrows=1, ncols=1, stylesheets=None, *args, **kwargs):
        """
        BasePlot is base class as wrapper around matplotlib
        """
        self._gs = None
        self._active_sp_id = None
        self._stylesheets = ['ggplot', ]

        self.stylesheets = stylesheets
        self.subplot_type = Subplot
        with plt.style.context(self.stylesheets):
            self.FIG = plt.figure(*args, **kwargs)
        self.active_subplot = None
        self.subplots = []
        self.gs = (nrows, ncols)
        self.available_gs = list(np.ndindex(nrows, ncols))

    def __getattr__(self, item):
        try:
            return getattr(self.FIG, item)
        except AttributeError:
            return getattr(self.active_subplot, item)

    @property
    def stylesheets(self):
        return self._stylesheets

    @stylesheets.setter
    def stylesheets(self, sheets):
        if hasattr(sheets, '__iter__'):
            new_stylesheets = []
            for s in sheets:
                if s not in plt.style.available:
                    raise ValueError('The stylesheet {0:s} is not available, '
                                     'please select one of the following {1:s}'.
                                     format(s, '\n'.join(plt.style.available)))
                else:
                    new_stylesheets.append(s)
            self._stylesheets = new_stylesheets

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
        self._gs = matplotlib.gridspec.GridSpec(nrows=gs_shape[0],
                                                ncols=gs_shape[1])

    def _slice_gs(self, gs_nr=None):
        if gs_nr is None:
            subplot_spec = self.gs[
                self.available_gs[0][0], self.available_gs[0][1]]
            selected_gs = [self.available_gs[0]]
        elif isinstance(gs_nr, int):
            subplot_spec = self.gs[gs_nr]
            geom = subplot_spec.get_geometry()
            selected_gs = [list(
                itertools.product(range(geom[0]), range(geom[1])))\
                [geom[2]]]
        elif isinstance(gs_nr, collections.Iterable) and not \
                isinstance(gs_nr, str):
            subplot_spec = self.gs[gs_nr[0]:gs_nr[2], gs_nr[1]:gs_nr[3]]
            selected_gs = list(itertools.product(range(gs_nr[0],gs_nr[2]),
                                                 range(gs_nr[1],gs_nr[3])))
        else:
            raise ValueError('The subplot spec couldn\'t be set. gs_nr should '
                             'be None, an integer or a tuple with 4 entries!')
        return subplot_spec, selected_gs

    def add_subplot(self, gs_nr=None, *args, **kwargs):
        subplot_spec, selected_gs = self._slice_gs(gs_nr)
        self.available_gs = [gs for gs in self.available_gs
                             if gs not in selected_gs]
        self.subplots.append(self.subplot_type(self.stylesheets, subplot_spec))
        self.active_subplot = len(self.subplots)-1
        return self
