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
import collections
import getpass
import logging

# External modules
import datetime as dt
import pyproj

import pygrib
import xarray as xr
import numpy as np

# Internal modules
import pymepps
from .filehandler import FileHandler


logger = logging.getLogger(__name__)


class GribHandler(FileHandler):
    def open(self):
        if self.ds is None:
            self.ds = pygrib.open(self.file)
        return self

    def close(self):
        if self.ds is not None:
            self.ds.close()
        self.ds = None

    def is_type(self):
        try:
            self.open()
            if len(self.ds[:])==0:
                return_value = False
            else:
                return_value = True
            self.close()
        except OSError:
            return_value = False
        return return_value

    def _get_varnames(self):
        var_names = [msg['cfVarNameECMF'] for msg in self.ds]
        for msg in self.ds:
            var_names.append(msg['cfVarNameECMF'])
        return set(var_names)

    def get_messages(self, var_name, **kwargs):
        """
        Method to get message-wise the data for a given variable as
        xr.DataArray.

        Parameters
        ----------
        var_name : str
            The name of the variable which should be extracted.

        Returns
        -------
        data : list of xr.DataArray
            The list with the message-wise data as DataArray. The DataArray
            have six coordinates (analysis, ensemble, time, level, y, x).
            The shape of DataArray are normally (1,1,1,1,y_size,x_size).
        """
        msgs = self.ds.select(cfVarNameECMF=var_name)
        logger.debug('Selected {0:s} from file {1:s}'.format(var_name,
                                                             self.file))
        data = []
        logger.debug('Starting decoding of messages')
        for msg in msgs:
            logger.debug('Decoding of message: {0:s}'.format(str(msg)))
            array_data = np.atleast_1d(msg.values)
            if len(array_data.shape) == 1:
                logger.debug('Found unstructured grid')
                grid_coords = {
                    'grid_coords': np.arange(0, array_data.shape[-1])
                }
                dims = ('grid_coords', )
            else:
                logger.debug('Found structured grid')
                grid_coords = {
                    'y': np.arange(0, array_data.shape[-2]),
                    'x': np.arange(0, array_data.shape[-1])
                }
                dims = ['y', 'x']
            constructed_array = xr.DataArray(
                data=array_data,
                coords=grid_coords,
                dims=dims
            )
            ana_date = msg.analDate,
            try:
                ens = [msg['perturbationNumber'], ]
            except RuntimeError:
                ens = ['det', ]
            valid_date = msg.validDate
            level = [":".join(str(msg).split(':')[4:6]).replace(' ', '_'), ]
            normalized_array = constructed_array.pp.normalize_coordinates(
                height=level,
                validtime=valid_date,
                ensemble=ens,
                runtime=ana_date)
            normalized_array.name = msg['cfName']
            normalized_array.attrs['unit'] = msg['units']
            try:
                normalized_array.attrs['projection'] = pyproj.Proj(
                    **msg.projparams)
            except (RuntimeError, TypeError):
                pass
            ecmf_gen = [k for k in msg.keys() if 'ECMF' in k]
            for k in ecmf_gen:
                normalized_array.attrs[k] = msg[k]
            normalized_array.attrs['short_name'] = msg['shortName']
            normalized_array.attrs['long_name'] = msg.name
            normalized_array.attrs['name'] = msg['cfName']
            normalized_array.attrs['scale_factor'] = msg['scaleValuesBy']
            normalized_array.attrs['add_offset'] = msg['offsetValuesBy']
            normalized_array.attrs['missing_value'] = msg['missingValue']
            data.append(normalized_array)
        logger.debug('Finished messages decoding')
        return data
