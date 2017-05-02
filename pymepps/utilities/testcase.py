#!/bin/env python
# -*- coding: utf-8 -*-
# """
# Created on 09.01.17
#
# Created for pymepps
#
# @author: Tobias Sebastian Finn, tobias.sebastian.finn@studium.uni-hamburg.de
#
#     Copyright (C) {2017}  {Tobias Sebastian Finn}
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
import logging
import unittest

# External modules

# Internal modules


logger = logging.getLogger(__name__)


class TestCase(unittest.TestCase):
    def assertAttribute(self, obj, attr):
        self.assertTrue(hasattr(obj, attr),
                        '{0:s} has not \'{1:s}\' as attribute'.format(
                            str(type(obj)), attr))

    def assertCallable(self, obj, method):
        self.assertTrue(callable(getattr(obj, method)),
                        '{0:s} is not a callable method in {1:s}'.format(
                            method, str(type(obj))))

    def assertMethod(self, obj, method):
        self.assertAttribute(obj, method)
        self.assertCallable(obj, method)
