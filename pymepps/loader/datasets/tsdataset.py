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

# External modules
import pandas as pd

# Internal modules
import pymepps
from .metdataset import MetDataset


logger = logging.getLogger(__name__)


class TSDataset(MetDataset):
    """
    TSDataset is a class for a pool of file handlers. Typically a
    time series dataset combines the files of a station, such that it
    is possible to select a variable and get a TSData instance. For
    memory reasons the data of a variable is only loaded if it is selected.

    Parameters
    ----------
    file_handlers : list of childs of FileHandler or None
        The spatial dataset is based on these files. The files should be
        either instances of NetCDFHandler or TextHandler. If file handlers
        is None then the dataset is used for conversion from SpatialData to
        TSData.
    data_origin : optional
        The data origin. This parameter is important to trace the data
        flow. If this is None, there is no data origin and this
        dataset will be the starting point of the data flow. Default is
        None.
    lonlat : tuple(float, float) or None
        The coordinates (longitude, latitude) where the data is valid. If 
        this is None the coordinates will be set based on data_origin or 
        based on the first file handler.

    Methods
    -------
    select
        Method to select a variable.
    """
    def __init__(self, file_handlers, data_origin=None, lonlat=None,
                 processes=1):
        super().__init__(file_handlers, data_origin, processes)
        self.lon_lat = lonlat

    def __str__(self):
        parent_str = super().__str__()
        return '{0:s}\nLonlat: {1}'.format(parent_str, self._get_lon_lat())

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

    def _get_file_data(self, file, var_name, **kwargs):
        file.open()
        try:
            ts_data = file.get_timeseries(var_name, **kwargs)
        finally:
            file.close()
        return ts_data

    def _multi_select_var(self, data, var_name):
        for d in data:
            df = pd.DataFrame(d)
            df.columns = ["{0:s}".format(var_name), ]
            yield df

    def select_by_pattern(self, pattern, return_list=False, **kwargs):
        return_list = super().select_by_pattern(pattern, return_list=True)
        return self.data_merge(
            [pd.DataFrame(l.data) for l in return_list], pattern)

    def data_merge(self, data, var_name):
        if isinstance(data, (list, tuple)):
            merged_data = data[0]
            merged_data = merged_data.pp.update(*data[1:])
        elif isinstance(data, (pd.Series, pd.DataFrame)):
            merged_data = data
        merged_data.name = var_name
        return merged_data
