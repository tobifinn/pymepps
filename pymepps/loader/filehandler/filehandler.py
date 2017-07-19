#!/bin/env python
# -*- coding: utf-8 -*-
# """
# Created on 16.11.16
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
import abc
import os
import dateutil.parser
import pytz
import logging
import datetime
import collections

# External modules
import xarray as xr

# Internal modules


logger = logging.getLogger(__name__)


class FileHandler(object):
    def __init__(self, file_path):
        """
        Base class for files with meteorological content. A FileHandler could
        extract the variables and metadata out of the files and could compress
        this data into one structure.

        Parameters
        ----------
        file_path : str
            The path to the file, which should be opened.
        """
        self.ds = None
        self.file = file_path
        self._var_names = None

    @property
    def var_names(self):
        if self._var_names is None:
            self._var_names = self._get_varnames()
        return self._var_names

    @abc.abstractmethod
    def get_messages(self, var_name, **kwargs):
        pass

    @abc.abstractmethod
    def get_timeseries(self, var_name, **kwargs):
        pass

    @abc.abstractmethod
    def _get_varnames(self):
        pass

    def _get_metadata(self):
        pass

    @staticmethod
    def _check_list_in_list(sublist, check_list):
        in_list = False
        for ele in check_list:
            if [sub for sub in sublist if sub in ele]:
                in_list = True
        return in_list

    def _get_runtime(self, **kwargs):
        if 'runtime' in kwargs:
            ana = kwargs['runtime']
        else:
            try:
                ana = self._get_dates_from_path(self.file)[0]
            except IndexError:
                ana = None
        return ana

    def _get_validtime(self, **kwargs):
        if 'validtime' in kwargs:
            time = kwargs['validtime']
        else:
            try:
                time = self._get_dates_from_path(self.file)[1]
            except IndexError:
                time = None
        return time

    def _get_ensemble(self, **kwargs):
        if 'ensemble' in kwargs:
            ens = kwargs['ensemble']
        else:
            ens = self._get_ensemble_from_path(self.file)
        return ens

    def _get_missing_coordinates(self, cube, grid_len=2, **kwargs):
        additional_coords = collections.OrderedDict()
        if not self._check_list_in_list(
                ['ana', 'runtime', 'referencetime'],
                list(cube.dims[:-grid_len])):
            additional_coords['runtime'] = self._get_runtime(**kwargs)
        if not self._check_list_in_list(
                ['ens', 'mem'], list(cube.dims[:-grid_len])):
            additional_coords['ensemble'] = self._get_ensemble(**kwargs)
        if not self._check_list_in_list(
                ['time', 'validtime'], list(cube.dims[:-2])):
            additional_coords['validtime'] = self._get_validtime(
                additional_coords, **kwargs)
        ds_coords = xr.Dataset(coords=additional_coords)
        cube.coords.update(ds_coords)
        cube = cube.expand_dims(list(additional_coords.keys()))
        return cube

    @staticmethod
    def _get_path_parts(path):
        base_path = os.path.normpath(path)
        base_path = os.path.splitext(base_path)[0]
        parts = base_path.split(os.sep)
        return parts

    def _get_ensemble_from_path(self, path):
        ens_member = None
        path_parts = self._get_path_parts(path)
        for part in reversed(path_parts):
            if part[:3]=='ens':
                ens_member = int(part[3:])
            elif part=='det':
                ens_member = 0
        if ens_member is None:
            ext = os.path.splitext(path)[1]
            try:
                ens_member = int(ext)
            except ValueError:
                ens_member = 0
        return ens_member

    def _get_dates_from_path(self, path):
        dates = []
        path_parts = self._get_path_parts(path)
        for part in path_parts:
            if len(part)>5:
                try:
                    date = dateutil.parser.parse(part, ignoretz=True)
                    date.replace(tzinfo=pytz.UTC)
                except ValueError:
                    date = None
                if date is None:
                    try:
                        date = datetime.datetime.strptime(part, '%Y%m%d_%H%M')
                    except ValueError:
                        date = -9999
                if date != -9999:
                    dates.append(date)
        return dates
