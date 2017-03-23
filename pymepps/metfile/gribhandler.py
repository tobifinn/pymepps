#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 09.12.16

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
import collections
import getpass
import logging

# External modules
import numpy as np
import datetime as dt
try:
    import pyproj
except ImportError:
    try:
        from mpl_toolkits.basemap import pyproj
    except:
        raise ImportError("either pyproj or basemap required")

import pygrib
import xarray
import numpy as np

# Internal modules
from .filehandler import FileHandler


logger = logging.getLogger(__name__)


class GribHandler(FileHandler):
    def open(self):
        self.ds = pygrib.open(self.file)
        return self

    def close(self):
        self.ds.close()

    def is_type(self):
        if len(self.ds[:])==0:
            return_value = False
        else:
            return_value = True
        return return_value

    def _get_varnames(self):
        var_names = []
        for msg in self.ds:
            var_names.append(msg.name)
        return set(var_names)

    def get_messages(self, var_name):
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
        logger.debug('Trying to select {0:s} from file {1:s}'.format(
            var_name,
             self.file))
        msgs = self.ds.select(name=var_name)
        logger.debug('Selected {0:s} from file {1:s}'.format(var_name,
                                                             self.file))
        data = []
        logger.debug('Starting decoding of messages')
        for msg in msgs:
            logger.debug('Decoding of message: {0:s}'.format(str(msg)))
            array_data = msg.values
            logger.debug('The type of array data is: {0:s}'.format(
                str(type(array_data))))
            if isinstance(array_data, float):
                array_data = np.array(array_data).reshape((1, 1, 1, 1, 1, 1))
            elif isinstance(array_data, np.ndarray):
                array_data = array_data[
                         np.newaxis, np.newaxis, np.newaxis, np.newaxis, :, :]
            else:
                raise ValueError(
                    'The type of array data is {0:s}. Array data has to be a '
                    'float or a numpy array.'.format(str(type(array_data))))
            logger.debug('Got array data')
            anal_date = [msg.analDate,]
            logger.debug('Got analysis date')
            try:
                ens_type = msg['typeOfEnsembleForecast']
                if ens_type in [2,3,4]:
                    ens = [msg['perturbationNumber'],]
            except RuntimeError:
                ens = ['det',]
            logger.debug('Got ensemble forecast number')
            valid_date = [msg.validDate-msg.analDate,]
            level = [":".join(str(msg).split(':')[4:6]),]
            logger.debug('Decoded levels')
            # Check if grid is in lat/lon
            dimensions = {}
            if 'iDirectionIncrementInDegrees' in msg.keys():
                y_0 = msg['latitudeOfFirstGridPointInDegrees']
                y_end = msg['latitudeOfLastGridPointInDegrees']
                x_0 = msg['longitudeOfFirstGridPointInDegrees']
                x_end = msg['longitudeOfLastGridPointInDegrees']
                logger.debug('Found lon/lat')
            # Unknown grid
            else:
                y_0 = 0
                y_end = array_data.shape[-2]-1
                x_0 = 0
                x_end = array_data.shape[-1]-1
                logger.debug('No lon/lat available')
            dimensions['y'] = np.linspace(y_0, y_end, array_data.shape[-2])
            dimensions['x'] = np.linspace(x_0, x_end, array_data.shape[-1])
            xr_data = xarray.DataArray(
                data=array_data,
                coords=[
                    ('analysis', anal_date), ('ensemble', ens),
                    ('time', valid_date), ('level', level),
                    ('y', dimensions['y']), ('x', dimensions['x'])])
            logger.debug('Combines everything into one xr DataArray')
            xr_data.name = msg['cfName']
            xr_data.attrs['unit'] = msg['units']
            try:
                xr_data.attrs['projection'] = pyproj.Proj(**msg.projparams)
            except RuntimeError:
                pass
            ecmf_gen = [k for k in msg.keys() if 'ECMF' in k]
            for k in ecmf_gen:
                xr_data.attrs[k] = msg[k]
            xr_data.attrs['short_name'] = msg['shortName']
            xr_data.attrs['long_name'] = msg.name
            xr_data.attrs['name'] = msg['cfName']
            xr_data.attrs['scale_factor'] = msg['scaleValuesBy']
            xr_data.attrs['add_offset'] = msg['offsetValuesBy']
            xr_data.attrs['missing_value'] = msg['missingValue']
            xr_data.attrs['history'] = "{0:s}, {1:s}, Python:pymepps:" \
                                       "GribHandler:get_messages('{2:s}')".\
                format(
                    dt.datetime.utcnow().strftime("%Y%m%d %H:%Mz"),
                    getpass.getuser(),
                    var_name)
            logger.debug('Set DataArray attributes')
            data.append(xr_data)
        logger.debug('Finished messages decoding')
        return data
