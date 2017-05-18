#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 18.05.17
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
from tqdm import tqdm
from multiprocessing import Pool
import types

# External modules

# Internal modules
from .tqdm_logging import tqdm_handler


logger = logging.getLogger(__name__)
logger.addHandler(tqdm_handler)


class MultiProcessing(object):
    def __init__(self, processes):
        self._processes = None
        self.processes = processes
        self.map = None

    @property
    def processes(self):
        return self._processes

    @processes.setter
    def processes(self, nr_proc):
        if not isinstance(nr_proc, int):
            raise TypeError('The number of processes needs to be an integer!')
        self._processes = nr_proc
        if self._processes>1:
            self.map = self._multiprocess_map
        else:
            self.map = self._sequential_map

    def _add_return_value_to_list(self, return_val, adding_list):
        is_iter = hasattr(return_val, '__iter__') and \
                  not isinstance(return_val, (str, bytes))
        if is_iter:
            adding_list = adding_list + list(return_val)
        else:
            adding_list.append(return_val)
        return adding_list

    def _sequential_map(self, single_func, iter_obj):
        return_data = []
        for d in tqdm(iter_obj):
            d_ind = single_func(d)
            return_data = self._add_return_value_to_list(d_ind, return_data)
        return return_data

    def _multiprocess_map(self, single_func, iter_obj):
        return_data = []
        p = Pool(processes=self.processes)
        with tqdm(total=len(iter_obj)) as pbar:
            for d_ind in p.imap_unordered(single_func, iter_obj):
                return_data = self._add_return_value_to_list(d_ind, return_data)
                pbar.update()
        p.close()
        return return_data
