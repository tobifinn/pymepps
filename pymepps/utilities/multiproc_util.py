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

# External modules

# Internal modules


logger = logging.getLogger(__name__)


class MultiProcessing(object):
    def __init__(self, processes):
        self._processes = None
        self.map = None
        self.processes = processes

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

    def _add_return_value_to_list(self, return_val, adding_list, flatten=True):
        is_iter = hasattr(return_val, '__iter__') and \
                  not isinstance(return_val, (str, bytes))
        if not is_iter or not flatten:
            return_val = [return_val,]
        return adding_list + list(return_val)

    def _sequential_map(self, single_func, iter_obj, flatten=True):
        """
        Method to map an iterable object to a function with a single input. The
        mapping will be sequential processed. A progressbar is displayed with 
        the tqdm module.

        Parameters
        ----------
        single_func: python function
            The mapping is performed for this given function. The function ought 
            to have only one parameter. For a function with more than one
            parameter it's recommended to use the partial module to set the
            other parameters.
        iter_obj: iterable
            The iterable python object. The entries of this object are mapped to
            the function.

        Returns
        -------
        return_data: list(obj)
            The bundled return data for the mapping as list. If single_func has
            an iterable as return object, the iterable is converted to a list. 
            The return_data is a flatten list.
        """
        return_data = []
        for d in tqdm(iter_obj):
            d_ind = single_func(d)
            return_data = self._add_return_value_to_list(d_ind, return_data,
                                                         flatten)
        return return_data

    def _multiprocess_map(self, single_func, iter_obj, flatten=True):
        """
        Method to map an iterable object to a function with a single input. The
        mapping will be performed with a multiprocessing pool. A progressbar is
        displayed with the tqdm module.

        Parameters
        ----------
        single_func: python function
            The mapping is performed for this given function. The function ought 
            to have only one parameter. For a function with more than one
            parameter it's recommended to use the partial module to set the
            other parameters.
        iter_obj: iterable
            The iterable python object. The entries of this object are mapped to
            the function.

        Returns
        -------
        return_data: list(obj)
            The bundled return data for the mapping as list. If single_func has
            an iterable as return object, the iterable is converted to a list. 
            The return_data is a flatten list.
        """
        return_data = []
        p = Pool(processes=self.processes)
        with tqdm(total=len(iter_obj)) as pbar:
            for d_ind in p.imap_unordered(single_func, iter_obj):
                return_data = self._add_return_value_to_list(d_ind, return_data,
                                                             flatten)
                pbar.update()
        p.close()
        return return_data
