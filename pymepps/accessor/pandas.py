#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 07.07.17
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
import abc

# External modules
import json
import pandas as pd

# Internal modules
from .base import MetData
from .utilities import register_dataframe_accessor, register_series_accessor


logger = logging.getLogger(__name__)


@register_series_accessor('pp')
@register_dataframe_accessor('pp')
class PandasAccessor(MetData):
    """
    An accessor to extend the pandas data structure. This could be used more
    actively in the  future to add more post-processing specific features to
    pandas.
    """
    def __init__(self, data):
        super().__init__(data)
        self.lonlat = None

    def update(self, *items):
        """
        Update the data.
        """
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
        updated_array.pp.lonlat = self.lonlat
        return updated_array

    def save(self, save_path):
        """
        The data is saved as json file. The pandas to_json method is used to
        generate convert the data to json. If lonlat was given it will be saved
        under a lonlat key. Json is used instead of HDF5 due to possible
        corruption problems.

        Parameters
        ----------
        save_path: str
            Path where the json file should be saved.
        """
        save_dict = dict(data=self.data.to_json(orient='split',
                                                date_format='iso'),
                         lonlat=self.lonlat)
        with open(save_path, mode='w+') as fp:
            json.dump(save_dict, fp)

    @staticmethod
    def load(load_path):
        """
        Load the given json file and return a TSData instance with the loaded
        file. The loader uses tries to locate the lonlat and the data keys
        within the json file. If there are not these keys the loader tries to
        load the whole json file into pandas.

        Parameters
        ----------
        load_path: str
            Path to the json file which should be loaded. It is recommended to
            load only previously saved TSData instances.

        Returns
        -------
        load_data: pandas object
            The loaded pandas object.
        """
        if isinstance(load_path, str):
            fp = open(load_path, mode='r')
        elif getattr(load_path, 'read'):
            fp = load_path
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
        if 'data' in list(saved_json_instance.keys()):
            pd_data_json = saved_json_instance['data']

        else:
            pd_data_json = saved_json_instance
        try:
            load_data = pd.read_json(pd_data_json, orient='split',
                                     typ='frame')
        except ValueError:
            load_data = pd.read_json(pd_data_json, orient='split',
                                     typ='series')
        if isinstance(load_data.index, pd.DatetimeIndex):
            load_data.index = load_data.index.tz_localize('UTC')
        load_data.pp.lonlat = lonlat
        return load_data
