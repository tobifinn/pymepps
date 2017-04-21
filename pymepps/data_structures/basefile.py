#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 08.12.16

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
import abc

# External modules

# Internal modules




class BaseFile(object):
    """
    The file base class.
    """
    def __init__(self, path):
        """
        Base for file classes.

        Parameters
        ----------
        path : str
            The path to the file.
        """
        self.__path = None
        self.path = path

    @property
    def path(self):
        """
        Get the path to the file.

        Returns
        -------
        str
            The path to the file
        """
        return self.__path

    @path.setter
    def path(self, path):
        """
        Set the file path

        Parameters
        ----------
        path : str
            The path to the file.

        Raises
        ------
        ValueError
            If the path is not a string.
        """
        if isinstance(path, str):
            self.__path = path
        else:
            raise ValueError("The path is not a string")

    @property
    def available(self):
        """
        Property if the file is available.

        Returns
        -------
        bool
            If the file is available.
        """
        return self.check()

    @abc.abstractmethod
    def check(self):
        pass
