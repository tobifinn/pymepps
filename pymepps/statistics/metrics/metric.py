#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 24.05.17
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
import abc
import os
import tarfile
import importlib

# External modules
import jsonpickle

# Internal modules
from pymepps.statistics.model import Model


logger = logging.getLogger(__name__)


class Metric(Model):
    """
    A metric is a tool to calculate the error of a given prediction for a given 
    truth. The metric has a dict with prediction and truth as state. If a class
    instance is called after the initialization a fit and transform will be
    performed with given prediction and truth. If the metric is unsupervised it 
    is also allowed to create a metric without a truth.
    """
    def __init__(self):
        super().__init__()
        self.state = {'prediction': None,
                      'truth': None}

    def __call__(self, prediction, truth):
        self.fit(X=prediction, y=truth)
        return self.transform()

    def fit(self, X, y=None):
        self.state['prediction'] = X
        self.state['truth'] = y

    def update(self, X=None, y=None):
        self.state['prediction'].update(X)
        self.state['truth'].update(y)

    def predict(self, X=None, y=None):
        return self._calc_metric()

    @abc.abstractmethod
    def _calc_metric(self):
        pass

    def save(self, save_path):
        """
        The data is saved as tarred file. Within the tarred file is this
        instance pickle and the state saved within their own file format.

        Parameters
        ----------
        save_path: str
            This path will be used to save the tarred file.
        """
        files_to_tar = []
        save_path = os.path.abspath(save_path)
        parent_dir = os.path.dirname(save_path)
        save_inst = self.copy()
        for k in save_inst.state:
            state_inst = save_inst.state[k]
            if state_inst is not None:
                state_save_path = os.path.join(parent_dir, k)
                state_inst.save(state_save_path)
                save_inst.state[k] = {
                    'module': state_inst.__module__,
                    'name': state_inst.__class__.__name__}
                files_to_tar.append(state_save_path)
        inst_save_path = os.path.join(parent_dir, 'metric.json')
        json_str = jsonpickle.encode(save_inst)
        with open(inst_save_path, mode='w+') as fd:
            fd.write(json_str)
        files_to_tar.append(inst_save_path)
        tar = tarfile.open(save_path, "w:gz")
        for f_path in files_to_tar:
            tar.add(f_path, arcname=os.path.basename(f_path))
        tar.close()

    @staticmethod
    def load(load_path):
        with tarfile.open(load_path, 'r:gz') as tar:
            metric_f = tar.extractfile('metric.json')
            json_str = metric_f.read().decode()
            metric = jsonpickle.decode(json_str)
            for k in metric.state:
                state_inst = metric.state[k]
                if isinstance(state_inst, dict):
                    state_load_path = os.path.join('/tmp', k)
                    tar.extract(k, '/tmp')
                    state_class = getattr(
                        importlib.import_module(state_inst['module']),
                        state_inst['name'])
                    state_inst = state_class.load(state_load_path)
                    metric.state[k] = state_inst
                    os.remove(state_load_path)
        return metric
