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

# Internal modules
from .metdata import MetData


logger = logging.getLogger(__name__)


class TSData(MetData):
    def __init__(self, data_base, data_origin=None,
                 encoder=None, lonlat=None, save_type='json'):
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
        encoder : child of StationDataEncoder
            For several different saved station data type, we need an encoder.
            E.g. the data of the Wettermast Hamburg is saved as txt file in a
            non-common data form.
        save_type : 'json' or 'hdf'
            The string to determine the file type in which the data is saved.
        lonlat : tuple(float, float) or None, optional
            The data of this instance is valid for this coordinates
            (longitude, latitude). If this is None the coordiantes are not set
            and not all features could be used. Default is None.

        Parameters
        ----------
        data_base : pandas.dataframe
            The data of this time series based data structure.
        data_origin : object of pymepps
            The origin of this data.This could be a model run, a station, a
            database or something else.
        encoder : child of StationDataEncoder or None
            For several different saved station data type, we need an encoder.
            E.g. the data of the Wettermast Hamburg is saved as txt file in a
            non-common data form. If there is no need of an encoder this is
            None. Default is None.
        fixed_dims : dict or None, optional
            The DataFrameData is valid for this fixed dimensions. The could be
            for example the coordinates of a weather station. The name of the
            fixed dimension is the key, while the value are the fixed values.
            If they are None, there are no fixed dimensions. Default is None.
        save_type : 'json' or 'hdf', optional
            The string to determine the file type in which the data is saved.
            The DataFrame is saved with the save methods of a pandas.DataFrame.
            There are different advantages and disadvantages for each file
            type.
            Json:
                + : Human readable,
                    easy to import, it's like a python dict
                - : File size
            HDF:
                + : File compression,
                    efficient save format,
                    standard save format for such data
                - : Not human readable,
                    error prone (make sure that you make backups!)
            Default is json.
        """
        self._save_types = {
            'json': (self._load_json, self._save_json),
            'hdf': (self._load_hdf, self._save_hdf)
        }
        self.load, self.save = self._save_types[save_type]
        self.encoder = encoder
        self.lonlat = lonlat
        super().__init__(data_base, data_origin)

    def plot(self, variable, type, color):
        pass

    def _load_json(self):
        pass

    def _save_json(self):
        pass

    def _load_hdf(self):
        pass

    def _save_hdf(self):
        pass
