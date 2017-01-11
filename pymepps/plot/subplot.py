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
import abc
import logging

# External modules
import matplotlib.pyplot as plt

# Internal modules


logger = logging.getLogger(__name__)


class Subplot(object):
    def __init__(self, stylesheets=None, *args, **kwargs):
        self._stylesheets = ['default', ]
        self.stylesheets = stylesheets
        with plt.style.context(self.stylesheets):
            self.ax = plt.subplot(*args, **kwargs)
        self._plot_methods = ['plot']

    @property
    def stylesheets(self):
        return self._stylesheets

    @stylesheets.setter
    def stylesheets(self, sheets):
        if hasattr(sheets, '__iter__'):
            new_stylesheets = []
            for s in sheets:
                if s not in plt.style.available:
                    raise ValueError(
                        'The stylesheet {0:s} is not available, '
                        'please select one of the following {1:s}'.
                        format(s, '\n'.join(plt.style.available)))
                else:
                    new_stylesheets.append(s)
            self._stylesheets = new_stylesheets

    def __getattr__(self, item):
        plot_func = self._check_plot_method(item)
        if plot_func is None:
            return getattr(self.ax, item)
        else:
            return plot_func

    def _check_plot_method(self, method):
        if method in self._plot_methods:
            def plotting_function(data, *args, **kwargs):
                return self.plot_method(data, method, *args, **kwargs)
            return plotting_function
        else:
            return None

    def _extract_data(self, data):
        return data

    def plot_method(self, data, method='plot', *args, **kwargs):
        if method not in self._plot_methods:
            raise ValueError('The selected plot method {0:s} isn\'t a valid '
                             'plot method. The valid plot methods are: {1:s}'.
                             format(method, '\n'.join(self._plot_methods)))
        extracted_data = self._extract_data(data)
        with plt.style.context(self.stylesheets):
            getattr(self.ax, method)(*extracted_data, *args, **kwargs)
        return self
