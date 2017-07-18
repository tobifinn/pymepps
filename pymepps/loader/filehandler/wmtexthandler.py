#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 30.06.17
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
import datetime
from io import StringIO

# External modules
import pandas as pd

# Internal modules
from .filehandler import FileHandler


logger = logging.getLogger(__name__)


class WMTextHandler(FileHandler):
    def open(self):
        if self.ds is None:
            self.ds = open(self.file, 'rb')
        return self

    def close(self):
        if self.ds is not None:
            self.ds.close()
        self.ds = None

    def is_type(self):
        try:
            self.open()
            self._decode_file()
            return_value = True
            self.close()
        except (OSError, FileNotFoundError, KeyError):
            return_value = False
        return return_value

    @property
    def lon_lat(self):
        return {}

    def _get_varnames(self):
        header, _ = self._decode_file()
        names = [name for name in header['Names']
                 if name not in ['DATE', 'TIME']]
        return names

    def _decode_file(self):
        self.ds.seek(0, 0)
        data = self.ds.read().decode('UTF-8').split('\n')
        data = [line.strip() for line in data]
        header = data[:7]
        data = data[7:]
        header = [line[1:].split('=') for line in header]
        header = {line[0]: line[1] for line in header}
        header['Samples'] = header.pop('', None)
        header['Names'] = header['Names'].split(';')
        header = {key: (datetime.datetime.strptime(val, '%d.%m.%Y %H:%M:%S')
                  if 'DateTime' in key else val)
                  for key, val in header.items()}
        return header, data

    def get_timeseries(self, var_name, **kwargs):
        """
        Method to get the time series from a WettermastTextFile.

        Parameters
        ----------
        var_name : str
            The variable name, which should be extracted.

        Returns
        -------
        data : dict with pandas series
            The selected variable is extracted as dict with pandas series as
            values.
        """
        header, data = self._decode_file()
        data = '\n'.join(data)
        wm_df = pd.read_csv(StringIO(data), sep=';', names=header['Names'],
                            parse_dates=[['DATE', 'TIME'], ], dayfirst=True,
                            na_values=float(header['DefaultValue']))
        wm_df = wm_df.set_index('DATE_TIME')
        # The time is always set to european winter time
        wm_df.index = wm_df.index - pd.to_timedelta('1 hour')
        wm_df.index.tz_localize('UTC')
        variable = pd.DataFrame(wm_df[var_name], columns=[var_name])
        variable.name = var_name
        return variable
