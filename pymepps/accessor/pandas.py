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
    An accessor as extension to pandas data structures. This accessor is a base
    for a SeriesAccessor and FrameAccessor.
    """
    def __init__(self, data):
        super().__init__(data)

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
        updated_array.pp.lonlat = self.lonlat
        return updated_array
