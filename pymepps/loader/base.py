#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 21.04.17
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
import glob
import os
from collections import Counter

# External modules

# Internal modules


logger = logging.getLogger(__name__)


class BaseLoader(object):
    def __init__(self, data_path, file_type=None):
        self.data_path = data_path
        self.file_type = file_type
        self._available_file_handler = {}

    def _get_file_handlers(self, files):
        pass

    def _convert_filehandlers_to_dataset(self, file_handlers):
        pass

    def load_data(self):
        files = [f for f in glob.glob(self.data_path) if not os.path.isdir(f)]
        file_handlers = self._get_file_handlers(files)
        dataset = self._convert_filehandlers_to_dataset(file_handlers)
        return dataset
