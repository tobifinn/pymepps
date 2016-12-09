#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 05.12.16

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
import os
import logging

# External modules

# Internal modules


logger = logging.getLogger(__name__)


class ModelRun(object):
    def __init__(self, model, init_date):
        """
        A model run for a given model and given initialization date.

        Attributes
        ----------
        model : Model
            This model run is created for this Model instance
        init_date : datetime.datetime
            The initialization time point of this model run.
        data_path : str
            The data path were the downloaded files are stored.
            The path structure is:
                model.data_path/init_date (date format: YYYYmmdd_hh).

        Parameters
        ----------
        model : Model
            This model run is for the given Model.
        init_date : datetime.datetime
            The initialization time point of this model run.

        Methods
        -------
        get_data()
            Method to get the data.
        download_data()
            Method to download the data from model's in_data_store.
        """
        self.model = model
        self.init_date = init_date
        self.data_path = os.path.join(model.data_path,
                                      self.init_date.strftime("YYYYmmdd_HH"))

    def get_data(self):
        """
        This includes the chain to download and
        save the data from in_data_store defined within the model class if
        it isn't available yet at model's data_path. If the data is available
        a the path will be loaded within a SpatialForecast instance.

        Returns
        -------
        spatial_forecast : GridBasedData or None
            If the run data is available a GridBasedData instance is
            returned. If the return value is None, the data isn't available and
            downloadable.
        """
        spatial_forecast = self.get_spatial_fcst()
        if spatial_forecast is not None:
            logger.debug('Model run {0:s} was already downloaded'.format(
                self.init_date.strftime("%Y%m%d_%H")))
            return spatial_forecast
        files_path = self.download_data()
        if not files_path:
            logger.info('Model run {0:s} couldn\'t downloaded'.format(
                self.init_date.strftime("%Y%m%d_%H")))
            return None
        spatial_forecast = self.get_spatial_fcst(files_path)
        if spatial_forecast is not None:
            logger.debug('Model run {0:s} is converted into one nc file'.format(
                self.init_date.strftime("%Y%m%d_%H")))
            return spatial_forecast
        logger.error('The data of model run {0:s} couldn\'t be concated'.format(
            self.init_date.strftime("%Y%m%d_%H")))
        return None

    def download_data(self):
        """
        Method to download the data from defined model's in_data_store to
        self.data_path.

        Returns
        -------
        output_files : list of str
            The paths were the files are saved. If the list is empty the files
            couldn't be downloaded.
        """
        output_files = self.model.in_data_store.get_data(
            self.data_path,
            self.model.inits,
            self.model.leads)
        return output_files

    def get_spatial_fcst(self, files=None):
        """
        Method to get saved data as SpatialForecast instance.

        Parameters
        ----------
        files : list of str, optional
            The files which are the base of the SpatialForecast instance.
            Default is None, so all appropriate files within self.data_path are
            loaded.

        Returns
        -------
        GridBasedData or None
            GridBasedData instance with the loaded files and this model run as
            base. If this is None, there was no file given or found within the
            data path.
        """
        # TODO: Needs to be written
        pass
