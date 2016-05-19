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
    def __init__(self, name="", inits=[], leads=[], server_model="", files=[],
                 data_path="", base_logger=None):
        self.name = name
        self.inits = inits
        self.leads = leads
        self.server_model = server_model
        self.files = files
        self.data_path = data_path
        self.logger = base_logger.createLogger(name)
        self.logger.initLogger()

    def run(self, date, aoi={"lat": [53, 54], "lon": [9.5, 10.5]}):
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
                else:
                    self.logger.error(
                        u"The run {0:s} isn't available, due to {1:s}"
                            .format(date.strftime("%Y%m%d_%H"), run_avail[1]))
            date -= datetime.timedelta(hours=1)
        if (start_date - date) < datetime.timedelta(days=2):
            self.logger.error(
                "The model hasn't 4 available runs in the last 2 days")
        self.logger.info("Finished raw data gathering")

    def _createModelRun(self, init):
        return ModelRun(self, init)


class ModelRun(BaseComponent):
    def __init__(self, model, init, aoi={"lat": [53, 54], "lon": [9.5, 10.5]}):
        assert isinstance(model, Model)
        self.model = model
        self.init = init
        self.aoi = aoi

    def getRaw(self):
        success, error, temp_files = self.get()
        if not success:
            for file in temp_files:
                try:
                    os.remove(file)
                except OSError:
                    pass
            return success, u"Data gathering: {0:s}".format(error)
        success, error = self.process(temp_files)
        if not success:
            for file in temp_files:
                try:
                    os.remove(file)
                except OSError:
                    pass
            return success, u"Data processing: {0:s}".format(error)
        success, error = self.write(temp_files)
        if not success:
            for file in temp_files:
                try:
                    os.remove(file)
                except OSError:
                    pass
            return success, u"Data writing: {0:s}".format(error)
        return True, 0

    def get(self):
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
        print(input_files)
        for key, file in enumerate(input_files):
            temp_file = os.path.join(self.model.data_path,
                                u"temp_{0:d}.tmp".format(key))
            output, error = self.model.server_model.getFile(file, temp_file)
            if output:
                output_files.append(temp_file)
            else:
                return output, error, output_files
        return True, str(0), output_files

    def process(self, files):
        for file in files:
            try:
                CDO.sellonlatbox(
                    "{0:.2f},{1:.2f},{2:.2f},{3:.2f}".format(
                        self.aoi["lon"][0],
                        self.aoi["lon"][1],
                        self.aoi["lat"][0],
                        self.aoi["lat"][1]),
                    input=file, output=file)
            except Exception as e:
                return False, e
        return True, 0

    def write(self, files):
        output_path = os.path.join(self.model.data_path, "run_{0:s}.nc".format(
            self.init.strftime("%Y%m%d%H")))
        try:
            CDO.mergetime(input=files, output=output_path)
        except Exception as e:
            return False, e
        else:
            for file in files:
                try:
                    os.remove(file)
                except OSError:
                    pass
        return True, 0
