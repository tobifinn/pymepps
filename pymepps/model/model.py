# -*- coding: utf-8 -*-
"""
Created on 23.04.16
Created for FcstSystem

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
import datetime
from copy import deepcopy

# External modules
import cdo

# Internal modules
from ..data import PathTemplate
from ..base import BaseComponent

__version__ = "0.1"

# initialize CDO
CDO = cdo.Cdo()


class Model(object):
    """
    this class represents a single weather forecast model (e.g. arome or gfs).
    A model can create a modelrun, which downloads the model data from given
    source for a specific date.
    """

    def __init__(self, name="", inits=[], leads=[], server_model="", files=[],
                 data_path="", base_logger=None):
        """
        The model initialization.
        Args:
            name (str): The name of the model.
            inits (list[int]): The initialization hours of the model.
            leads (list[int]): The lead times of the model.
            server_model (instance of subclass of pymepss.data.Server):
                The used server of the model (e.g. an internet server)
            files (instance of pymepps.data.Pathtemplate or list[str]):
                The file names. The could created with a pathtemplate system.
            data_path (str): Path where the model data should be saved.
            base_logger (instance of BaseLogger):
                The logger base of the system.

        Attributes:
            name (str): The name of the model.
            inits (list[int]): The initialization hours of the model.
            leads (list[int]): The lead times of the model.
            server_model (instance of subclass of pymepss.data.Server class):
                The used server of the model (e.g. an internet server)
            files (instance of pymepps.data.Pathtemplate class or list[str]):
                The file names. The could created with a pathtemplate system.
            data_path (str): Path where the model data should be saved.
            logger (instance of Logger class): The logger for the model.
                Initialized with the model name and the base logger.
        """
        self.name = name
        self.inits = inits
        self.leads = leads
        self.server_model = server_model
        self.files = files
        self.data_path = data_path
        self.logger = base_logger.createLogger(name)
        self.logger.initLogger()

    def run(self, date, aoi={"lat": [53, 54], "lon": [9.5, 10.5]}):
        """
        This method runs the model and gets the model data.
        Args:
            date (datetime.datetime object): The current system date.
            aoi (dict[list[float]]):
                Area of interest, where the data is constrained.
        """
        self.logger.info("Started data gathering")
        assert isinstance(date, datetime.datetime)
        start_date = deepcopy(date)
        num_fcst = 0
        while num_fcst < 4 and \
                ((start_date - date) < datetime.timedelta(days=2)):
            if date.hour in self.inits:
                run = ModelRun(self, date, aoi)
                run_avail = run.getRaw()
                if run_avail[0]:
                    num_fcst += 1
                    self.logger.info(
                        u"The run {0:s} was sucessfully downloaded".format(
                            date.strftime("%Y%m%d_%H")))
                else:
                    self.logger.error(
                        u"The run {0:s} has a problem, due to {1:s}"
                            .format(date.strftime("%Y%m%d_%H"), run_avail[1]))
            date -= datetime.timedelta(hours=1)
        if (start_date - date) < datetime.timedelta(days=2):
            self.logger.error(
                "The model hasn't 4 available runs in the last 2 days")
        self.logger.info("Finished raw data gathering")

    def _createModelRun(self, init):
        return ModelRun(self, init)


class ModelRun(BaseComponent):
    """
    A model run for a specific numerical weather model nad initialization date.
    """

    def __init__(self, model, init, aoi={"lat": [53, 54], "lon": [9.5, 10.5]}):
        """
        The initialization of the model run
        Args:
            model (Model object): The corresponding model.
            init (datetime.datetime object): The initialization date of the run.
            aoi (dict[list[float]]):
                Area of interest, where the data is constrained.
        Attributes:
            model (Model object): The corresponding model.
            init (datetime.datetime object): The initialization date of the run.
            aoi (dict[list[float]]):
                Area of interest, where the data is constrained.
        """
        assert isinstance(model, Model)
        self.model = model
        self.init = init
        self.aoi = aoi

    def getRaw(self):
        """
        Get the raw data of the model run. Combines the data gathering,
        processing and saving.
        Returns:
            success (bool): If the model run saving was successful
            errorcode (int or str): The error code. If 0 there was no error.
        """
        for dirpath, dirnames, files in os.walk(
                os.path.join(self.model.data_path,u"{0:s}".format(
                                 self.init.strftime("%Y%m%d_%H")))):
            if files:
                return True, 0
        success, error, temp_files = self.get()
        if not success:
            for file in temp_files:
                try:
                    os.remove(file)
                except OSError:
                    pass
            return success, u"data gathering error: {0:s}".format(str(error))
        success, error, processed_files = self.process(temp_files)
        if not success:
            for file in temp_files:
                try:
                    os.remove(file)
                except OSError:
                    pass
            for file in processed_files:
                try:
                    os.remove(file)
                except OSError:
                    pass
            return success, u"data processing error: {0:s}".format(str(error))
        success, error = self.write(processed_files)
        if not success:
            return success, u"data writing error: {0:s}".format(str(error))
        return True, 0

    def get(self):
        """
        Get the model data.
        Returns:
            success (bool): If the model run gathering was successful
            errorcode (int or str): The error code. If 0 there was no error.
            output_files (list[str]): List of temporary raw model run files.
        """
        input_files = []
        output_files = []
        if isinstance(self.model.files, PathTemplate):
            input_files = self.model.files.generatePaths(self.model.leads,
                                                         self.init)
        elif isinstance(self.model.files, str):
            input_files = PathTemplate(self.model.files).generatePaths(
                self.model.leads, self.init)
        else:
            try:
                _ = (e for e in self.model.files)
                input_files = self.model.files
            except TypeError:
                print(self.model.files,
                      'is not iterable, nor a PathTemplate, nor a string')
        for key, file in enumerate(input_files):
            temp_file = os.path.join(self.model.data_path,
                                     u"{0:s}".format(
                                         self.init.strftime("%Y%m%d_%H")),
                                     u"raw_{0:d}.tmp".format(key))
            output, error = self.model.server_model.getFile(file, temp_file)
            if output:
                output_files.append(temp_file)
            else:
                return output, error, output_files
        return True, str(0), output_files

    def process(self, files):
        """
        Method to constrain the raw model files around the area of interest.
        Args:
            files (list[str]): List of raw temporary model files.

        Returns:
            success (bool): If the model run constraining was successful
            errorcode (int or str): The error code. If 0 there was no error.
            processed_files (list[str]): List of processed model run files.
        """
        processed_files = []
        for key, file in enumerate(files):
            try:
                working_dir = os.path.dirname(file)
                output = os.path.join(working_dir, "raw_{0:d}.nc".format(key))
                CDO.sellonlatbox(
                    "{0:.2f},{1:.2f},{2:.2f},{3:.2f}".format(
                        self.aoi["lon"][0],
                        self.aoi["lon"][1],
                        self.aoi["lat"][0],
                        self.aoi["lat"][1]),
                    input=file, output=output)
                os.remove(file)
                processed_files.append(output)
            except Exception as e:
                return False, e
        return True, 0, processed_files

    def write(self, files):
        """
        Method to combine the temporary model files into one model run netCDF
        file with cdo.
        Args:
            files (list[str]): List of constrained temporary model files.

        Returns:
            success (bool): If the model run combining was successful.
            errorcode (int or str): The error code. If 0 there was no error.
        """
        output_path = os.path.join(self.model.data_path, u"{0:s}".format(
                                     self.init.strftime("%Y%m%d_%H")),
                                   "run_{0:s}.nc".format(
                                     self.init.strftime("%Y%m%d%H")))
        try:
            CDO.merge(input=files, output=output_path)
        except Exception as e:
            return False, e
        else:
            for file in files:
                try:
                    os.remove(file)
                except OSError:
                    pass
        return True, 0
