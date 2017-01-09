#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 29.11.16

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

# External modules
import pandas as pd

# Internal modules
from ..data_structures import filetypes_dict

logger = logging.getLogger(__name__)


class Station(object):
    def __init__(self, identifier, in_data_store=None, data_path=None,
                 file_type=None, encoder=None, save_type='json'):
        """
        Station is a class for a meteorological measurement site.
        The data is saved/loaded as save_type file within given data_path.

        Parameters
        ----------
        identifier : str
            Every station gets an unique identifier. This could be a name,
            the wmo identifier etc.
        file_type : str
        in_data_store : child of DataServer or None, optional
            The input data store, where the downloadable files are saved.
            Default None, so there is no data store defined and the file
            download is skipped.
        data_path : str or None, optional
            The path where the files should be/are saved. Default is None, so
            the path is determined automatically by the data folder within the
            system config file. If the system has no config file, a data folder
            is created within the pymepps folder.
        encoder : child of StationDataEncoder, optional
            The encoder to encode the downloaded raw station files.
        """
        self.identifier = identifier
        self.in_data_store = in_data_store
        self.data_path = data_path
        self.encoder = encoder
        try:
            self.file_type = filetypes_dict[file_type.lower()]
        except:
            logger.error(
                'The specified file type {0:s} isn\'t available '
                'yet.\n The possible file types are: {1:s}'.format(file_type,
                    '\n'.join(
                    ['{0:s}'.format(key) for
                     key, value in filetypes_dict.items()])))
