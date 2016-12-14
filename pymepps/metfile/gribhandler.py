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

# Internal modules
from .filehandler import FileHandler


class GribHandler(FileHandler):
    def _get_varnames(self):
        grb = pygrib.open(self.file.path)
        var_names = []
        for msg in grb:
            var_names.append(msg.name)
        grb.close()
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
        grb = pygrib.open(self.file.path)
        msgs = grb.select(name=var_name)
        grb.close()
        data = []
        for msg in msgs:
            array_data = np.array(msg.data()[0])
            array_data = array_data[
                         np.newaxis, np.newaxis, np.newaxis, np.newaxis, :, :]
            anal_date = [msg.analDate,]
            try:
                ens_type = msg['typeOfEnsembleForecast']
                if ens_type in [2,3,4]:
                    ens = [msg['perturbationNumber'],]
            except RuntimeError:
                ens = ['det',]
            valid_date = [msg.validDate,]
            level = [":".join(str(msg).split(':')[4:6]),]
            # Check if grid is in lat/lon
            dimensions = []
            if 'iDirectionIncrementInDegrees' in msg.keys():
                y_0 = msg['latitudeOfFirstGridPointInDegrees']
                y_end = msg['latitudeOfLastGridPointInDegrees']
                y_inc = msg['jDirectionIncrementInDegrees']*(-1)**(float(y_end<y_0))
                x_0 = msg['longitudeOfFirstGridPointInDegrees']
                x_inc = msg['iDirectionIncrementInDegrees']
                x_end = msg['longitudeOfLastGridPointInDegrees']
                dimensions.append(np.arange(y_0, y_end+y_inc, y_inc))
                dimensions.append(np.arange(x_0, x_end + x_inc, x_inc))
            # Unknown grid
            else:
                dimensions.append(np.arange(0, array_data.shape[-2]))
                dimensions.append(np.arange(0, array_data.shape[-1]))
            xr_data = xarray.DataArray(
                data=array_data,
                coords=[
                    ('analysis', anal_date), ('ensemble', ens),
                    ('time', valid_date), ('level', level),
                    ('y', dimensions[0]), ('x', dimensions[1])])
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
            data.append(xr_data)
        return data
