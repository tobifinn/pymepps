# -*- coding: utf-8 -*-
"""
Created on 18.05.16
Created for pyMepps

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
import abc

# External modules

# Internal modules


__version__ = "0.2"


class BaseFile(object):
    """
    The file base class.
    """
    def __init__(self, path):
        self.__path = None
        self.path = path

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, path):
        if isinstance(path, str):
            self.__path = path
        else:
            raise ValueError("The path is not a string")

    @property
    def available(self):
        return self.check()

    @abc.abstractmethod
    def check(self):
        pass


class File(BaseFile):
    @property
    def dir(self):
        return self.get_dir()

    def check(self):
        return self.check_file()

    def get_dir(self):
        return os.path.dirname(self.path)

    def check_file(self):
        if os.path.isfile(self.path):
            return True
        return False

    def create_dir(self):
        try:
            os.makedirs(self.dir, exist_ok=True)
        except:
            raise ValueError("The dir can't be created")

    def create_file(self):
        try:
            open(self.path, 'a').close()
        except:
            raise ValueError("The file can't be created")

    def rename(self, new_name):
        try:
            new_path = os.path.join(self.dir, new_name)
            os.rename(self.path, new_path)
            self.path = new_path
        except:
            raise ValueError("The file can't be renamed")

    def change_path(self, new_path):
        try:
            os.rename(self.path, new_path)
            self.path = new_path
        except:
            raise ValueError("The file path can't be changed")

    def open(self, mode="w+b"):
        return open(self.path, mode=mode)
