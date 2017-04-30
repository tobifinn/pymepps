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

# External modules

# Internal modules


logger = logging.getLogger(__name__)


class MetDataset(object):
    def __init__(self, file_handlers, data_origin=None, processes=1):
        """
        MetDataset is a base class for handling meteorolgical files. The normal
        workroutine would be:
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
        """
        self._file_handlers = None
        self.data_origin = data_origin
        self._variables = {}
        self.file_handlers = file_handlers
        self.processes = processes

    @property
    def variables(self):
        if not any(self._variables):
            new_variables = {}
            for file in self._file_handlers:
                file.open()
                for var in file.var_names:
                    if var not in new_variables.keys():
                        new_variables[var] = [file]
                    else:
                        new_variables[var].append(file)
                file.close()
            self._variables = new_variables
        return self._variables

    @property
    def file_handlers(self):
        if self._file_handlers is None:
            raise ValueError(
                'Do you really want to get a attribute, which is None?')
        return self._file_handlers

    @file_handlers.setter
    def file_handlers(self, handlers):
        self._file_handlers = handlers
        if not isinstance(self._file_handlers, list) and \
                        self._file_handlers is not None:
            self._file_handlers = [self._file_handlers, ]

    @property
    def var_names(self):
        return sorted(self.variables.keys())

    def select_by_pattern(self, pattern, return_list=True):
        """
        Method to select variables from this dataset by keywords. This method
        uses list comprehension to extract the variable names where the var_name
        pattern is within the variable name. If the variable names are found the
        variable is selected with the select method.

        Parameters
        ----------
        pattern : str
            The pattern fir which should be searched.
        return_list : bool
            If the return value should be a list or a dictionary.

        Returns
        -------
        data_list : dict/list with SpatialData instances or None
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
            for var in found_variables:
                data = self.select(var)
                if return_list:
                    data_list.append(data)
                else:
                    data_list[var] = data
            return data_list

    def select(self, var_name):
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

        Returns
        -------
        extracted_data : Child of MetData or None
            A child instance of MetData with the data of the selected variable
            as data. If None is returned the variable wasn't found within the
            list with possible variable names.
        """
        if var_name not in self.var_names:
            logger.error("The variable {0:s} is not in the available variable "
                         "names list. The possible variables are: {1:s}".
                         format(var_name, str(self.var_names)))
            return None
        data = []
        for file in self.variables[var_name]:
            logger.debug('Trying to get data from {0:s}'.format(file.file))
            file_data = self._get_file_data(file, var_name)
            logger.debug('Got file data from {0:s}'.format(file.file))
            try:
                data = data+file_data
            except TypeError:
                data = data+[file_data,]
            logger.debug('Added the file data to the dataset data')
        extracted_data = self.data_merge(data, var_name)
        return extracted_data

    @abc.abstractmethod
    def _get_file_data(self, file, var_name):
        pass

    @abc.abstractmethod
    def data_merge(self, data, var_name):
        """
        Method to merge the given data by given metadata into one data
        structure.
        """
        pass

    @abc.abstractmethod
    def plot(self, variable, fashion, color, **kwargs):
        pass
