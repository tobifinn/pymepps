# -*- coding: utf-8 -*-
"""
Created on 18.05.16
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

# External modules

# Internal modules
from .basefile import BaseFile

__version__ = "0.2"


class File(BaseFile):
    def __init__(self, path):
        """
        Object for one single file.

        Parameters
        ----------
        path : str
            The path to the file.

        Methods
        -------
        get_dir
            Get the file dir.
        check_file
            Checks if the file is available.
        create_dir
            Create the file dir.
        create_file
            Create the file within the dir.
        rename(new_name)
            Rename the file.
        change_path(new_path)
            Move the file to another path.
        open(mode)
            Open the file.
        """
        super().__init__(path)
    @property
    def dir(self):
        return self.get_dir()

    @property
    def name(self):
        return self.get_basename()

    def check(self):
        return self.check_file()

    def get_dir(self):
        return os.path.dirname(self.path)

    def get_basename(self):
        return os.path.basename(self.path)

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
            self.create_dir()
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
