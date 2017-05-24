#!/bin/env python
# -*- coding: utf-8 -*-
# """
# Created on 09.12.16
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
import io

# External modules
import json
import pandas as pd

# Internal modules
from .metdata import MetData


logger = logging.getLogger(__name__)


class TSData(MetData):
    """
    TSData is a data structure for time series based data. This
    class is for meteorological measurement station observations and
    forecasts. Its instances are based on pandas.dataframe. So it's
    possible to use every operation on this structure specified in the
    documentation of pandas [1]. This structure has usually only one
    dimension. This data type has only one flexible dimension and
    the other dimensions are fixed in comparison to ArrayBasedData.

    [1] (http://pandas.pydata.org/pandas-docs/stable/)

    Attributes
    ----------
    data : pandas.dataframe
        The data of this time series based data structure.
    data_origin : object of pymepps
        The origin of this data.This could be a model run, a station, a
        database or something else.
    lonlat : tuple(float, float) or None, optional
        The data of this instance is valid for this coordinates
        (longitude, latitude). If this is None the coordiantes are not set
        and not all features could be used. Default is None.

    Parameters
    ----------
    data : pandas.dataframe
        The data of this time series based data structure.
    data_origin : object of pymepps
        The origin of this data.This could be a model run, a station, a
        database or something else.
    lonlat: tuple(float, float) or None
        The data is valid for these coordinates.
    """
    def __init__(self, data, data_origin=None, lonlat=None):
        super().__init__(data, data_origin)
        self.lonlat = lonlat

    def __str__(self):
        name = self.__class__.__name__
        return '{0:s}\n{1:s}\n{2:s}\nlonlat:{3:s}'.format(
            name, '-'*len(name), str(self.data.describe()), str(self.lonlat)
        )

    def copy(self):
        copied_self = super().copy()
        copied_self.lonlat = self.lonlat
        return copied_self

    def slice_index(self, start='', end='', inplace=False):
        """
        inplace: bool, optional
            If the new data should be replacing the data of this TSData
            instance or if the instance should be copied. Default is None.

        Returns
        -------
        tsdata: TSData
            The TSData instance with the sliced index.
        """
        if inplace:
            tsdata = self
        else:
            tsdata = self.copy()
        tsdata.data = tsdata.data.loc[start:end]
        return tsdata

    def plot(self, variable, type, color):
        pass

    def save(self, path):
        """
        The data is saved as json file. The pandas to_json method is used to 
        generate convert the data to json. If lonlat was given it will be saved
        under a lonlat key. Json is used instead of HDF5 due to possible
        corruption problems.

        Parameters
        ----------
        path: str
            Path where the json file should be saved.
        """
        # self.data.to_json(path, orient='split')
        save_dict = dict(pd_data=self.data.to_json(orient='split'),
                         lonlat=self.lonlat)
        with open(path, mode='w+') as fp:
            json.dump(save_dict, fp)

    @staticmethod
    def load(path):
        """
        Load the given json file and return a TSData instance with the loaded 
        file. The loader uses tries to locate the lonlat and the data keys
        within the json file. If there are not these keys the loader tries to 
        load the whole json file into pandas.

        Parameters
        ----------
        path: str
            Path to the json file which should be loaded. It is recommended to 
            load only previously saved TSData instances.


        Returns
        -------
        tsdata: TSData
            The loaded TSData instance.
        """
        if isinstance(path, str):
            fp = open(path, mode='r')
        elif getattr(path, 'read'):
            fp = path
        else:
            raise TypeError('Path needs to be either a string '
                            'or an opened file!')
        json_str = fp.read()
        if not isinstance(json_str, str):
            json_str = json_str.decode()
        saved_json_instance = json.loads(json_str)
        fp.close()
        if 'lonlat' in list(saved_json_instance.keys()) and \
                saved_json_instance['lonlat'] is not None:
            lonlat = tuple(saved_json_instance['lonlat'])
        else:
            lonlat = None
        if 'pd_data' in list(saved_json_instance.keys()):
            pd_data_json = saved_json_instance['pd_data']

        else:
            pd_data_json = saved_json_instance
        try:
            pd_data = pd.read_json(pd_data_json, orient='split',
                                   typ='frame')
        except ValueError:
            pd_data = pd.read_json(pd_data_json, orient='split',
                                   typ='series')
        tsdata = TSData(data=pd_data, data_origin=path, lonlat=lonlat)
        return tsdata
