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
from copy import deepcopy

# External modules

# Internal modules


logger = logging.getLogger(__name__)


class Model(object):
    """
    This is a base class for all statistical modules of pymepps.
    
    Attributes
    ----------
    state:
        The state of the statistical model. This state could be a dict with 
        SpatialData and TSData instances or a fitted model. If the state is None
        the model has no state.
    
    Methods
    -------
    fit:
        The fit method is used for an initial fit of the statistical model. 
        The initial fit could be e.g. used to set the initial state of the
        model.
    predict:
        The predict method is used to get predict with the saved state and the 
        given data new instances.
    transform:
        Transform refers to predict. This method should be used if it is not 
        natural to make a predict with the statistical model, e.g. this could be
        used for a metric.
    save:
        The save method is used to save the statistical model in a persistent
        manner. With an external load function a statistical model could be
        load. Normally the statistical model will be pickled.
    """
    def __init__(self):
        self.state = None

    def copy(self):
        return deepcopy(self)

    @abc.abstractmethod
    def fit(self, X, y=None):
        pass

    @abc.abstractmethod
    def predict(self, X=None, y=None):
        pass

    def transform(self, X=None, y=None):
        return self.predict(X, y)

    @abc.abstractmethod
    def update(self, X=None, y=None):
        pass

    @abc.abstractmethod
    def save(self, path):
        pass