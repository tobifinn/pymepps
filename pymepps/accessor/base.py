#!/bin/env python
# -*- coding: utf-8 -*-
# """
# Created on 03.12.16
#
# Created for pymepps
#
# @author: Tobias Sebastian Finn, tobias.sebastian.finn@studium.uni-hamburg.de
#
#     Copyright (C) {2016}  {Tobias Sebastian Finn}
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
# """
# System modules
import logging
from copy import deepcopy
import abc

# External modules

# Internal modules


logger = logging.getLogger(__name__)


class MetData(object):
    """
    MetData is the base class for meteorological data, like station data,
    nwp forecast data etc.
    """
    def __init__(self, data):
        self._data = None
        self.data = data

    def __repr__(self):
        return "{0:s}".format(str(self.__class__.__name__))

    @abc.abstractmethod
    def update(self, *items):
        pass

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        if isinstance(data, str):
            data = self.load(data)
        if data is None:
            raise ValueError(
                '{0:s} needs data!'.format(self.__class__.__name__))
        self._data = data
