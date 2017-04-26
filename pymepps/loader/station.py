#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 21.04.17
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

# External modules

# Internal modules
from .base import BaseLoader
from pymepps.metfile import NetCDFHandler
from pymepps.metdata import TSDataset


logger = logging.getLogger(__name__)


class StationLoader(BaseLoader):
    """
    A simplified way to load weather model data into a SpatialDataset.
    Technically this class is a helper and wrapper around the file handlers and
    SpatialDataset.

    Parameters
    ----------
    data_path: str
        The path to the files. This path could have a glob-conform path pattern.
        Every file found within this pattern will be used to determine the file
        type and to generate the SpatialDataset.
    file_type: str or None, optional
        The file type determines which file handler will be used to load the
        data. If the file type is None it will be determined automatically based
        on given files. All the files with the majority file type will be used 
        to generate the SpatialDataset.
    lonlat: tuple(float, float), optional
        The lonlat coordinate tuple describes the position of the station in
        degrees. If this is None the position is unknown. Default is None.
    """
    def __init__(self, data_path, file_type=None, lonlat=None, processes=1):
        super().__init__(data_path, file_type, processes)
        self.lonlat = lonlat
        self._available_file_type = {
            'nc': NetCDFHandler,
        }

    def lon_lat(self):
        return self.lonlat

    def _convert_filehandlers_to_dataset(self, file_handlers):
        ds = TSDataset(file_handlers, data_origin=self)
        return ds

def open_station_dataset(data_path, file_type=None, lonlat=None, processes=1):
    loader = StationLoader(data_path, file_type, lonlat, processes)
    return loader.load_data()
