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

# External modules
import pandas as pd

# Internal modules
from .pandas import PandasAccessor
from .utilities import register_series_accessor


logger = logging.getLogger(__name__)


@register_series_accessor('pp')
class SeriesAccessor(PandasAccessor):
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
