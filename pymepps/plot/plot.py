#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 02.12.16

Created for pymepps

@author: Tobias Sebastian Finn, tobias.sebastian.finn@studium.uni-hamburg.de

    Copyright (C) {2016}  {Tobias Sebastian Finn}

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
import logging

# External modules
import matplotlib.pyplot as plt

# Internal modules
from .subplot import Subplot


logger = logging.getLogger(__name__)


class Plot(object):
    def __init__(self, n_subplots=1, style=None, fig_size=(5,3), **kwargs):
        """
        Base class to plot meteorological data.
        """
        self.figure = plt.figure(figsize=fig_size, **kwargs)
        self.subplots = []
        self.active_subplot = None
        self.plot_style = style
        self._plot_style = None
        if n_subplots is not None:
            for n in range(n_subplots):
                self.subplots.append(self._new_subplot())
                self.active_subplot = self.subplots[-1]

    @property
    def plot_style(self):
        return self._plot_style

    @plot_style.setter
    def plot_style(self, styles):
        avail_styles = plt.style.available
        self._plot_style = None
        if isinstance(styles, str):
            if styles in avail_styles:
                self._plot_style = [styles,]
            else:
                logger.error('The selected style: {0:s} isn\'t available '
                             'within the styles. The plot style is set to '
                             'None.')
        elif hasattr(styles, '__iter__'):
            plot_styles = []
            for style in styles:
                if style in avail_styles:
                    plot_styles.append(style)
                else:
                    logger.error('The selected style: {0:s} isn\'t available '
                                 'within the styles. This plot style isn\'t '
                                 'append to the styles list.')
            if not plot_styles:
                logger.warning('The style list is empty. The plot style is '
                               'set to None.')
            else:
                self._plot_style = plot_styles

    def set_active_sub(self, n=0):
        """
        Method to set the active subplot.

        Parameters
        ----------
        n

        Returns
        -------
        self
        """
        self.active_subplot = self.subplots[n]
        return self

    def _run_subplots(self):
        for sub in self.subplots:
            sub.plot()
        return self

    def save(self, path, *args, **kwargs):
        """
        Method to save the plot at given path.

        Parameters
        ----------
        path

        Returns
        -------

        """
        self._run_subplots()
        self.figure.savefig(path, *args, **kwargs)

    def show(self):
        """
        Method to show the plot.

        Returns
        -------

        """
        self._run_subplots()
        self.figure.show()

    def title(self, title, **kwargs):
        """
        Method to plot a title into the title bar.

        Parameters
        ----------
        title : str
            The title for this plot.

        Returns
        -------
        self
        """
        self.figure.suptitle(title, **kwargs)
        return self

    def xlabel(self, label, **kwargs):
        self.active_subplot.xlabel(label, **kwargs)

    def ylabel(self, label, **kwargs):
        self.active_subplot.ylabel(label, **kwargs)

    def _new_subplot(self):
        """
        Method to create a new subplot within the data plotting area.

        Returns
        -------

        """
        try:
            return Subplot(axis_info=self._axis_info)
        except AttributeError:
            return Subplot(axis_info=None)