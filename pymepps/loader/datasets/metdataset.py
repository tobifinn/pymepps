#!/bin/env python
# -*- coding: utf-8 -*-
# """
# Created on 10.12.16
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
import abc
from functools import partial

# External modules
from tqdm import tqdm

# Internal modules
from pymepps.utilities import MultiThread

logger = logging.getLogger(__name__)


class MetDataset(object):
    """
    MetDataset is a base class for handling meteorolgical files.
    
    The normal workroutine would be:
        1) load the files (use of file handlers)
        2) select the important variables within the files (this object)
        3) post-process the variables (MetData/SpatialData/TSData object)

    Parameters
    ----------
    file_handlers : list of childs of FileHandler or None.
        The loaded file handlers. This instance load the variables. If the 
        file handlers are None then the dataset is used for conversion
        between Spatial and TSData.
    data_origin : optional
        The class where the data comes from. Normally this would be a
        model or a measurement site. If this is None, this isn't set.
        Default is None.
    processes : int, optional
        This number of processes is used to calculate time-consuming functions.
        For time-consuming functions a progress bar is shown. If the number of 
        processes is one the functions will be processed sequential. For more
        processes than one the multiprocessing module will be used.
        Default is 1.
    """
    def __init__(self, file_handlers, data_origin=None, processes=1):
        self._file_handlers = None
        self._multiproc = None
        self._processes = 1
        self.data_origin = data_origin
        self.file_handlers = file_handlers
        self.processes = processes
        self.__variables = self._initialize_variables()

    def __repr__(self):
        file_handlers = len(self.file_handlers)
        return '{0:s}({1:d})'.format(self.__class__.__name__, file_handlers)

    def __str__(self):
        file_handlers = len(self.file_handlers)
        var_names = self.var_names
        return '{0:s}\n{1:s}\nFile handlers: {2:d}\nVariables: {3:s}'.format(
            self.__class__.__name__, '-'*len(self.__class__.__name__),
            file_handlers, str(var_names))

    @property
    def processes(self):
        return self._processes

    @processes.setter
    def processes(self, nr_proc):
        self._multiproc = MultiThread(nr_proc)
        self._processes = nr_proc

    @staticmethod
    def _get_variables(file_handler):
        file_handler.open()
        var_names = list(file_handler.var_names)
        file_handler.close()
        return var_names

    def _initialize_variables(self):
        new_variables = {}
        mt = MultiThread(processes=self.processes)
        var_names_list = mt.map(self._get_variables, self._file_handlers,
                                flatten=False)
        for key, var_names in enumerate(var_names_list):
            for var_name in var_names:
                try:
                    new_variables[var_name].append(self._file_handlers[key])
                except KeyError:
                    new_variables[var_name] = [self._file_handlers[key], ]
        return new_variables

    @property
    def variables(self):
        """
        Return the variable names and the corresponding file handlers.
        """
        return self.__variables

    @property
    def file_handlers(self):
        if self._file_handlers is None:
            raise ValueError(
                'Do you really want to get a attribute, which is None?')
        return self._file_handlers

    @file_handlers.setter
    def file_handlers(self, handlers):
        if not isinstance(handlers, list) and handlers is not None:
            self._file_handlers = [handlers, ]
        else:
            self._file_handlers = handlers

    @property
    def var_names(self):
        """
        Get the available variable names.
        """
        return sorted(self.variables.keys())

    def select_by_pattern(self, pattern, return_list=True, **kwargs):
        """
        Method to select variables from this dataset by keywords. This method
        uses list comprehension to extract the variable names where the var_name
        pattern is within the variable name. If the variable names are found the
        variable is selected with the select method.

        Parameters
        ----------
        pattern : str
            The pattern for which should be searched.
        return_list : bool
            If the return value should be a list or a dictionary.
        kwargs : dict
            Additional parameters that are passed to the file handlers.

        Returns
        -------
        data_list : dict(str, SpatialData or TSData) or
                    list(SpatialData or TSData) or None
            The return value is a dict/list with SpatialData instances, one
            entry for every found variable name. If return_list is False, are
            the keys the variable names. If None is returned no variable with
            this pattern was found.
        """
        found_variables = [var for var in self.var_names if pattern in var]
        if not found_variables:
            logger.error('The pattern {0:s} is not found within the variable '
                         'names of this dataset. The available variable names'
                         ' are: {1:s}'.format(pattern, str(self.var_names)))
            return None
        else:
            if return_list:
                data_list = []
            else:
                data_list = {}
            logger.info(
                'Started to extract variables from file handlers with pattern '
                '{0:s}'.format(pattern))
            for var in found_variables:
                data = self.select(var, **kwargs)
                if return_list:
                    data_list.append(data)
                else:
                    data_list[var] = data
            return data_list

    def select(self, var_name, **kwargs):
        """
        Method to select a variable from this dataset. If the variable is find
        in more than one file or message, the method tries to find similarities
        within the metadata and to combine the data into one array, with
        several dimensions. This method could have a long running time, due to
        data loading and combination.

        Parameters
        ----------
        var_name : str
            The variable which should be extracted. If the variable is not
            found within the dataset there would be a value error exception.
        kwargs : dict
            Additional parameters that are passed to the file handlers.

        Returns
        -------
        extracted_data : SpatialData, TSData or None
            A child instance of MetData with the data of the selected
            variable as data. If None is returned the variable wasn't found
            within the list with possible variable names.
        """
        if var_name not in self.var_names:
            logger.error("The variable {0:s} is not in the available variable "
                         "names list. The possible variables are: {1:s}".
                         format(var_name, str(self.var_names)))
            return None
        num_file_handlers = len(self.variables[var_name])
        logger.info('Started select {0:s} from {1:d} files'.format(
            var_name, num_file_handlers))
        single_func = partial(self._get_file_data, var_name=var_name, **kwargs)
        data = self._multiproc.map(single_func, self.variables[var_name],
                                   flatten=True)
        logger.info('Extracted the data, now merge the data!')
        extracted_data = self.data_merge(data, var_name)
        return extracted_data

    def select_ds(self, include=None, exclude=None, **kwargs):
        """
        Extract the dataset data into a MetData instance. The include list is
        handled superior to the exclude list. If both lists are None all
        available variables are used.

        Parameters
        ----------
        include: iterable or None
            Within the include iterable are all variable names, which should be
            included into the MetData data. The list will be filtered for
            available  variable names. If no variable name is available a
            ValueError will be raised. If this is None, the include will be
            skipped and the exclude list will be used. Default is None.
        exclude: iterable or None
            If no include iterable is given, this exclude iterable is used.
            In this case, any available variable name, which is not within this
            list is used. If this iterable is also None, all available data
            variables are used to construct the MetData instance. Default is
            None.
        kwargs : dict
            Additional parameters that are passed to the file handlers.

        Returns
        -------
        extracted_data: TSData or SpatialData
            The extracted data instance.

        Raises
        ------
        ValueError:
            A ValueError is raised if no variable was selected from the dataset.
        """
        if isinstance(include, (tuple, list, set,)):
            extract_vars = [var for var in include if var in self.var_names]
            logger.debug(extract_vars)
            logger.info(
                'Filtered out the following variables, they are not within the '
                'dataset! {0:s}'.format(
                    str([var for var in include if var not in extract_vars])))
        else:
            if isinstance(exclude, (tuple, list, set,)):
                extract_vars = [var for var in self.var_names
                                if var not in exclude]
                logger.info(
                    'Filtered out the following variables, they are not within '
                    'the dataset! {0:s}'.format(str(
                        [var for var in self.var_names
                         if var not in extract_vars])))
            else:
                extract_vars = self.var_names
                logger.info('Used all available variables within this dataset')

        raw_data = []
        for var_name in extract_vars:
            num_file_handlers = len(self.variables[var_name])
            logger.info('Started select {0:s} from {1:d} files'.format(
                var_name, num_file_handlers))
            single_func = partial(self._get_file_data, var_name=var_name,
                                  **kwargs)
            data = self._multiproc.map(single_func, self.variables[var_name],
                                       flatten=True)
            raw_data.extend(self._multi_select_var(data, var_name))
            logger.info('Finished variable {0:s}'.format(var_name))
        logger.info('Extracted the data, now merge the data!')
        extracted_data = self.data_merge(raw_data, self.var_names[0])
        return extracted_data

    @abc.abstractmethod
    def _multi_select_var(self, data, var_name):
        pass

    @abc.abstractmethod
    def _get_file_data(self, file, var_name, **kwargs):
        pass

    @abc.abstractmethod
    def data_merge(self, data, var_name):
        """
        Method to merge the given data by given metadata into one data
        structure.
        """
        pass
