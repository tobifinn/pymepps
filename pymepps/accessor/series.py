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
from .base import MetData
from .pandas_accessor import register_series_accessor
from .pandas_accessor import register_dataframe_accessor


logger = logging.getLogger(__name__)


@register_dataframe_accessor('pp')
@register_series_accessor('pp')
class SeriesAccessor(MetData):
    """
    This accessor is an extension for pandas data structures. The intention for
    this accessor is the use of pandas data structures for processing of
    meteorological station data, .e.g. station observations or forecasts.

    Attributes
    ----------
    data : pandas.DataFrame or pandas.Series
        The data of this time series based data structure.
    lonlat : tuple(float, float) or None, optional
        The data of this instance is valid for this coordinates
        (longitude, latitude). If this is None the coordinates are not set
        and not all features could be used. Default is None.

    Parameters
    ----------
    data : pandas.DataFrame or pandas.Series
        The data of this time series based data structure.
    lonlat: tuple(float, float) or None
        The data is valid for these coordinates.
    """
    def __init__(self, data, lonlat=None):
        super().__init__(data)
        self.lonlat = lonlat

    def __repr__(self):
        return '{0:s}(lonlat: {1:s})'.format(
            self.data.__class__.__name__, str(self.lonlat))

    def update(self, *items):
        update_data = [self.data.copy(), ]
        for item in items:
            if isinstance(item, (pd.Series, pd.DataFrame)):
                update_data.append(item)
            else:
                raise TypeError(
                    'The given item {0} need to be in a pandas conform data '
                    'type!'.format(item))
        concatenated_data = pd.concat(update_data, axis=1)
        dup_cols = concatenated_data.columns.duplicated(keep='last')
        columned_data = concatenated_data.loc[:, ~dup_cols].sort_index(axis=1)
        for name, val in concatenated_data.loc[:, dup_cols][::-1].iteritems():
            columned_data[name] = columned_data[name].fillna(val)
        columned_data = columned_data.squeeze()
        dup_rows = columned_data.index.duplicated(keep='last')
        updated_array = columned_data.loc[~dup_rows].sort_index(axis=0)
        for ind, val in concatenated_data.loc[dup_rows][::-1].T.iteritems():
            updated_array.loc[ind] = updated_array.loc[ind].fillna(val)
        return updated_array

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
