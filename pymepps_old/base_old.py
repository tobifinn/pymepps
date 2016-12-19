# -*- coding: utf-8 -*-
"""
Created on 11.09.16

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

# External modules

# Internal modules


class Model(object):
    def createModelRun(self):
        return ModelRun(self)


class ModelRun(object):
    def __init__(self, model):
        self.model = model

    def getData(self):
        return SpatialForecast()


class TimeSeries(object):
    def plot(self):
        pass

    def save(self, file_path):
        pass


class StationData(TimeSeries):
    pass


class Forecast(TimeSeries):
    pass

class SpatialForecast(Forecast):
    def plot(self):
        pass

    def save(self, file_path):
        pass


class DataArchive(object):
    def __init__(self, server=None):
        self.server = server


class Station(object):
    def __init__(self, server):
        self.server = server

    def getTimeSeries(self, start, end, frequency):
        return StationData()


class Server(object):
    def getData(self):
        pass

    def saveData(self):
        pass


class StatisticalModel(object):
    def __init__(self, layers=[]):
        self.layers = layers

    def fit(self, fcst, target):
        pass

    def update(self, fcst, target, update_rate):
        pass

    def predict(self, fcst):
        pass


class System(object):
    pass
