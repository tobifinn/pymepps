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

# External modules
import pandas as pd

# Internal modules
from .metdataset import MetDataset
from .tsdata import TSData


logger = logging.getLogger(__name__)


class TSDataset(MetDataset):
    def __init__(self, file_handlers, data_origin=None):
        """
        TSDataset is a class for a pool of file handlers. Typically a
        time series dataset combines the files of a station, such that it
        is possible to select a variable and get a TSData instance. For
        memory reasons the data of a variable is only loaded if it is selected.

        Parameters
        ----------
        file_handlers : list of childs of FileHandler
            The spatial dataset is based on these files. The files should be
            either instances of NetCDFHandler, TextHandler.
        data_origin : optional
            The data origin. This parameter is important to trace the data
            flow. If this is None, there is no data origin and this
            dataset will be the starting point of the data flow. Default is
            None.

        Methods
        -------
        select
            Method to select a variable.
        """
        super().__init__(file_handlers, data_origin)

    @property
    def lon_lat(self):
        return self._get_lon_lat()

    def _get_lon_lat(self):
        if self.data_origin is not None:
            try:
                return self.data_origin.lon_lat()
            except Exception as e:
                logger.debug('Couldn\'t get lon/lat from data origin, due to '
                             '{0:s}'.format(str(e)))
        else:
            try:
                return self.file_handlers[0].lon_lat()
            except Exception as e:
                logger.debug('Couldn\'t get lon/lat from first file handler, '
                             'due to {0:s}'.format(str(e)))
                return None

    def _get_file_data(self, file, var_name):
        return file.get_timeseries(var_name)

    def data_merge(self, data):
        extracted_data = data[0]
        for d in data[1:]:
            for k in d:
                if k in extracted_data.keys():
                    extracted_data[k] = extracted_data[k].append(d[k])
                    extracted_data[k] = extracted_data[k].sort_index()
                else:
                    extracted_data.update({k:d[k]})
        if len(extracted_data.keys())>1:
            extracted_data = pd.DataFrame(extracted_data)
        else:
            extracted_data = pd.Series(list(extracted_data.values())[0])
        return TSData(extracted_data, self, lonlat=self.lon_lat)

