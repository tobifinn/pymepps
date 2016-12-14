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
import datetime as dt
import operator

# External modules
import numpy as np

import xarray as xr

# Internal modules
from .metdataset import MetDataset
from .spatialdata import SpatialData


logger = logging.getLogger(__name__)


class SpatialDataset(MetDataset):
    def __init__(self, file_handlers, data_origin=None):
        """
        SpatialDataset is a class for a pool of file handlers. Typically a
        spatial dataset combines the files of one model run, such that it is
        possible to select a variable and get a SpatialData instance. For
        memory reasons the data of a variable is only loaded if it is selected.

        Parameters
        ----------
        file_handlers : list of childs of FileHandler
            The spatial dataset is based on these files. The files should be
            either instances of GribHandler or NetCDFHandler.
        data_origin : optional
            The data origin. This parameter is important to trace the data
            flow. If this is None, there is no data origin and this
            dataset will be the starting point of the data flow. Default is
            None.

        Methods
        -------
        select
            Method to select a variable.

        Example Usage
        -------------
        >>> model = DynamicalModel('GFS_0_25')
        >>> modelrun = ModelRun(model,
        >>>                     dt.datetime.strptime('25.12.1992', '%d.%m.%Y'))
        >>> file_handlers = [GribHandler(…), GribHandler(…), GribHandler(…)]
        >>> ds = SpatialDataset(file_handlers, modelrun)
        >>> data = ds.select('t2m')[10:100, 10:100, 1]
        The selected variable is t2m.
        The dimensions longitude and latitude and time are sliced.
        >>> data.plot(method='contourf', c='red').save('t2m.png')
        The data is plotted as contourf plot in red.
        The plot is saved at the path: ~/t2m.png
        >>> data.dataflow
        GFS_0_25:Init-25.12.1992 00:00 UTC:Grib:T2m:
        sliced(longitude, latitude, time)
        """
        super().__init__(file_handlers, data_origin)

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
        extracted_data : SpatialData or None
            A SpatialData instance with the data of the selected variable as
            data. If None is returned the variable wasn't found within the
            list with possible variable names.
        """
        return super().select(var_name)

    def data_merge(self, data):
        """
        Method to merge instances of xarray.DataArray into a SpatialData
        instance. The merge method of xarray is used.

        Parameters
        ----------
        data : list of xarray.DataArray
            The data list.

        Returns
        -------
        SpatialData
        """
        if len(data) == 1:
            return SpatialData(data[0], self)
        else:
            uniques = []
            for dim in ['analysis', 'ensemble', 'time', 'level']:
                if dim in data[0].coords:
                    dim_gen = [d[dim].values for d in data]
                else:
                    dim_gen = [None,]
                uniques.append(list(np.unique(dim_gen)))
            if np.product([len(u) for u in uniques]) != len(data):
                logger.warning(
                    'The number of possible split elements isn\'t '
                    'the same as the number of elements within the data list. '
                    'So the assumption of same-sized clusters is violated and '
                    'it isn\'t possible to combine the data into one data '
                    'array completely.')
                extracted_data = xr.concat(data)
            else:
                indexes = []
                for d in data:
                    d_ind = [d.values]
                    for key, dim in enumerate(['analysis', 'ensemble', 'time', 'level']):
                        if dim in d.coords:
                            d_ind.append(uniques[key].index(d[dim].values))
                        else:
                            d_ind.append(0)
                    indexes.append(d_ind)
                sorted_data = zip(*sorted(indexes, key=operator.itemgetter(1,2,3,4)))
                sorted_data = np.array(list(sorted_data)[0])
                shaped_data = sorted_data.reshape(
                    [len(u) for u in uniques]+
                    [sorted_data.shape[-2]]+
                    [sorted_data.shape[-1]])
                coords = list(zip(['analysis', 'ensemble', 'time', 'level', 'x', 'y'],
                             uniques+[data[0]['x'].values]+[data[0]['y'].values]))
                extracted_data = xr.DataArray(
                    data=shaped_data,
                    coords=coords)
                extracted_data.attrs = data[0].attrs
        return SpatialData(extracted_data, self)
