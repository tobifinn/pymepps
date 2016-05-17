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

# External modules

# Internal modules
from ..base import BaseComponent

__version__ = "0.1"


class Model(BaseComponent):
    def __init__(self, name="", inits=[], leads=[], base_url="", data_path=""):
        self.name = name
        self.inits = inits
        self.leads = leads
        self.base_url = base_url
        self.data_path = data_path

    def getData(self):
        pass

    def processData(self):
        pass

    def writeData(self):
        pass

