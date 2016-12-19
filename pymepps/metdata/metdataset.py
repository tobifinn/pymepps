#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 10.12.16

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
import abc

# External modules

# Internal modules


logger = logging.getLogger(__name__)


class MetDataset(object):
    def __init__(self, file_handlers, data_origin=None):
        """
        MetDataset is a base class for handling meteorolgical files. The normal
        workroutine would be:
        1) load the files (use of file handlers)
        2) select the important variables within the files (this object)
        3) post-process the variables (MetData/SpatialData/TSData object)

        Parameters
        ----------
        file_handlers : list of childs of FileHandler
            The loaded file handlers. This instance load the variables.
        data_origin : optional
            The class where the data comes from. Normally this would be a
            model or a measurement site. If this is None, this isn't set.
            Default is None.
        """
        self.file_handlers = file_handlers
        if not isinstance(self.file_handlers, list):
            self.file_handlers = [self.file_handlers,]
        self.data_origin = data_origin
        self.variables = {}
        for file in self.file_handlers:
            for var in file.var_names:
                if var not in self.variables.keys():
                    self.variables[var] = [file]
                else:
                    self.variables[var].append(file)

    @property
    def var_names(self):
        return list(self.variables.keys())

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
            file.open()
            logger.debug('Trying to get data from {0:s}'.format(file.file.path))
            file_data = self._get_file_data(file, var_name)
            logger.debug('Got file data from {0:s}'.format(file.file.path))
            if isinstance(file_data, (list, tuple)):
                data.extend(file_data)
            else:
                data.append(file_data)
        extracted_data = self.data_merge(data)
        for file in self.variables[var_name]:
            file.close()
        return extracted_data

    @abc.abstractmethod
    def _get_file_data(self, file, var_name):
        pass

    @abc.abstractmethod
    def data_merge(self, data):
        """
        Method to merge the given data by given metadata into one data
        structure.
        """
        pass

    @abc.abstractmethod
    def plot(self, variable, fashion, color, **kwargs):
        pass
