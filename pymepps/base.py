# -*- coding: utf-8 -*-
"""
Created on 23.04.16
Created for FcstSystem

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
import abc

# External modules

# Internal modules


__version__ = "0.1"


class BaseComponent(object):
    def __init__(self, name="", logger=None):
        self.name = name
        self.logger = logger
        self.data = None

    @abc.abstractmethod
    def getData(self):
        pass

    @abc.abstractmethod
    def processData(self):
        pass

    @abc.abstractmeth
    def writeData(self):
        pass
