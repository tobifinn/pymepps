# -*- coding: utf-8 -*-
"""
Created on 28.09.16

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
import datetime

# External modules
import numpy as np

# Internal modules
from ..data_structures import servers_dict
from ..metfile import file_handler_dict
from .run import ModelRun


logger = logging.getLogger(__name__)


class DynamicalModel(object):
    def __init__(self, name, in_data_store=None, data_path=None,
                 file_type=None, inits=None, leads=None):
        """
        A dynamical model is a class for grid based numerical weather models.
        The run method is the preferred method to run the model in a normal
        way. What is the normal way?
            1) Get forecast data
            2) Load the forecast data into a GridBasedData instance

        Attributes
        ----------
        See at the parameters section.

        Parameters
        ----------
        name : str
            The name of the model.
        in_data_store : str, optional
            The input data store, where the downloadable files are saved.
            Default None, so there is no data store defined and the file
            download is skipped.
        data_path : str, optional
            The path where the files should be/are saved. Default is None, so
            the path is determined automatically by the data folder within the
            system config file. If the system has no config file, a data folder
            is created within the pymepps folder.
        file_type : str, optional
            The file type of stored files. Default is None so every possible
            FileHandler is tried. If the file couldn't be opened there will be
            a value error.
        inits : list of int, optional
            List with integers. The integers are the initialization time points
            of the model. This initialization time points are used to determine
            the downloadable files for the model and to start a ModelRun. The
            unit of the inits is hours. Default is None so there is no
            initialization.
        leads : list of int, optional
            The lead times of the model. The lead times are used to determine
            the downloadable files within one initialization time point. The
            leads are also used to determine if all model files are available.
            Default is None so there is no lead time. This means that there is
            only one file for each model run or there is no systematic.

        Methods
        -------
        run(date)
            Run the model and create ModelRun instances automatically based on
            init.
        create_model_run(date)
            Create a ModelRun instance for this model based on given date.
        """
        self.name = name
        self.data_path = data_path
        try:
            self.in_data_store = servers_dict[in_data_store.lower()]
        except:
            logger.error(
                'The specified input data store {0:s} isn\'t available '
                'yet.\n The possible file types are: {1:s}'.format(
                    in_data_store,
                    '\n'.join(
                        ['{0:s}'.format(key) for
                         key, value in servers_dict.items()])))
        try:
            if isinstance(file_type, str):
                self.file_type = file_handler_dict[file_type.lower()]
            elif file_type is None:
                self.file_type = None
                logger.info('No file type is specified, the file type is '
                            'determined automatically!')

        except:
            logger.error(
                'The specified file type {0:s} isn\'t available '
                'yet.\n The possible file types are: {1:s}'.format(file_type,
                    '\n'.join(
                        ['{0:s}'.format(key) for
                         key, value in file_handler_dict.items()])))
        self.inits = inits
        self.leads = leads

    def get_historical_data(self, stop_date=None, n_fcsts=1000):
        """
        Method to download historical data, without the constrains in the run
        method. The constrains could be specified with a stop_date or a number
        of forecasts. One of the two constrains have to be specified.

        Parameters
        ----------
        stop_date : datetime.datetime, optional
            The available files are downloaded/opened up to this stop_date. The
            iteration is stopped if the date is older than this stop_date. If
            this is None, there is no date constrain. Default is
            01.01.2000, 00:00 UTC, to avoid a too long iteration.
        n_fcsts : int, optional
            Specifies how many forecasts should be downloaded/opened. If there
            are more than this number of forecasts, the newest n_fcsts
            forecasts are opened. If this is None, there is no constrain.
            Default is 1000, to avoid that to many forecasts are downloaded.

        Returns
        -------
        spatial_fcsts : list of SpatialData
            List with instances of GridBasedData. This list are the available
            forecasts up to the point where one of the constrains are reached.
        """
        if stop_date is None and n_fcsts is None:
            logger.exception("One of the two parameters has to be specified!")
        logger.info('Model data gathering for {0:s} started'.format(self.name))
        date = datetime.datetime.utcnow()
        spatial_fcsts = []
        if n_fcsts is None:
            n_fcsts = np.inf
        if stop_date is None:
            stop_date = datetime.datetime(1,1,1)
        while len(spatial_fcsts) < n_fcsts and (
                    (date-stop_date) < datetime.timedelta(0)):
            if date.hour in self.inits:
                run = self.create_model_run(date)
                spatial_fcst = run.get_spatial_fcst()
                if spatial_fcst is not None:
                    spatial_fcsts.append(spatial_fcst)
            date -= datetime.timedelta(hours=1)
        logger.info("Finished {0:s} data gathering, and got {1:d} forecasts.".
                    format(self.name, len(spatial_fcsts)))
        return spatial_fcsts

    def run(self, date):
        """
        Run the model and iterate through the initializations until there are
        four available SpatialForecasts or the initialization time is older
        than two days. This is used if the model is run via the System class.
        It creates automatically ModelRuns based on initializations and given
        date.

        Parameters
        ----------
        date : datetime.datetime
            The start time of the model in utc. This is usually the time
            determined by the system with datetime.datetime.utcnow.

        Returns
        -------
        spatial_fcsts : list of SpatialData
            List with instances of SpatialData. This list are the last four
            available forecasts made by this model.
        """
        logger.info('Model data gathering for {0:s} started'.format(self.name))
        assert isinstance(date, datetime.datetime), logger.error(
            'The given date is no datetime object')
        start_date = date
        spatial_fcsts = []
        while len(spatial_fcsts) < 4 and (
                    (start_date - date) < datetime.timedelta(days=2)):
            if date.hour in self.inits:
                run = self.create_model_run(date)
                spatial_fcst = run.get_spatial_fcst()
                if spatial_fcst is not None:
                    spatial_fcsts.append(spatial_fcst)
                    logger.info(
                        u"The run {0:s} is successfully opened".format(
                            date.strftime("%Y%m%d_%H")))
                else:
                    logger.debug(u"The run {0:s} has a problem".format(
                            date.strftime("%Y%m%d_%H")))
            date -= datetime.timedelta(hours=1)
        if (start_date - date) < datetime.timedelta(days=2):
            logger.error(
                "The model hasn't 4 available runs in the last 2 days")
        logger.info("Finished {0:s} data gathering".format(self.name))
        return spatial_fcsts

    def create_model_run(self, date):
        """
        Creates an instance of ModelRun with this model and given date as
        initialization.

        Parameters
        ----------
        date : datetime.datetime
            The initialization time object of the ModelRun.

        Returns
        -------
        ModelRun
            The created ModelRun instance with this model and the given date as
            argument. For more information about ModelRun see there.
        """
        return ModelRun(self, date)
