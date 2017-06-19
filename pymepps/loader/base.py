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
from functools import partial
from collections import Counter

# External modules
from tqdm import tqdm

# Internal modules
from pymepps.utilities.multiproc_util import MultiThread


logger = logging.getLogger(__name__)


class BaseLoader(object):
    def __init__(self, data_path, file_type=None, processes=1):
        self.data_path = data_path
        self.file_type = file_type
        self.processes = processes
        self._available_file_type = {}

    @staticmethod
    def _check_file_handler(file_path, base_handler):
        handler = base_handler(file_path)
        if handler.is_type():
            return handler
        else:
            return None

    def _get_specific_type_handlers(self, files, file_type):
        base_handler = self._available_file_type[file_type]
        logger.info('Started file handler checking for file type: {0:s}'.format(
            file_type))
        check_fh = partial(self._check_file_handler, base_handler=base_handler)
        mt = MultiThread(processes=self.processes)
        file_handlers = mt.map(check_fh, files)
        return file_handlers

    def _get_file_handlers(self, files):
        try:
            file_handlers = self._get_specific_type_handlers(
                files, self.file_type)
        except KeyError:
            file_handlers = self._determine_file_handler(files)
        return file_handlers

    def _determine_file_handler(self, files):
        all_file_handlers = {
            type: self._get_specific_type_handlers(files, type)
            for type in self._available_file_type}
        file_handlers = all_file_handlers[
            max(all_file_handlers,
                key=lambda k: len(all_file_handlers[k]))]
        return file_handlers

    def _convert_filehandlers_to_dataset(self, file_handlers):
        pass

    def load_data(self):
        if self.data_path[:4] == 'http':
            files = [self.data_path, ]
        elif isinstance(self.data_path, str):
            files = [f for f in glob.glob(self.data_path)
                     if not os.path.isdir(f)]
        elif getattr(self.data_path, 'read'):
            files = [self.data_path]
        else:
            raise TypeError('The data path needs to be either a string '
                            'or an opened file!')
        file_handlers = self._get_file_handlers(files)
        if not file_handlers:
            raise ValueError('Found no suitable FileHandler')
        dataset = self._convert_filehandlers_to_dataset(file_handlers)
        return dataset
