#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 19.12.16

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

# Internal modules
from .system_handler import SystemHandler


logger = logging.getLogger(__name__)


class ConfigHandler(SystemHandler):
    def __init__(self):
        """
        Class for handling config files for an operational post-processing
        system. This class could open a main config file and sub config files.
        """
        pass
