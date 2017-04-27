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
from pymepps.metdata import SpatialDataset
from pymepps.metfile import NetCDFHandler, GribHandler


logger = logging.getLogger(__name__)


class ModelLoader(BaseLoader):
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
    grid : str or Grid or None, optional
        The grid describes the horizontal grid of the spatial data. The given 
        grid will be forwarded to the given SpatialDataset instance. Default is
        None.
    """
    def __init__(self, data_path, file_type=None, grid=None, processes=1):
        super().__init__(data_path, file_type, processes)
        self.grid = grid
        self._available_file_type = {
            'nc': NetCDFHandler,
            'grib2': GribHandler,
            'grib1': GribHandler,
        }

    def _convert_filehandlers_to_dataset(self, file_handlers):
        ds = SpatialDataset(file_handlers, self.grid, data_origin=self)
        return ds

def open_model_dataset(data_path, file_type=None, grid=None, processes=1):
    loader = ModelLoader(data_path, file_type, grid, processes)
    return loader.load_data()
