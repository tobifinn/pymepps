# -*- coding: utf-8 -*-
"""
Created on 17.05.16
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
import abc
from abc import abstractmethod
import urllib.request
import urllib.parse
import urllib.error
import shutil

# External modules

# Internal modules
from .file import File

__version__ = "0.1"


class Server(object):
    __meta__ = abc.ABCMeta

    def __init__(self, base_path):
        """
        This class representing a common server.
        Args:
            base_path (str): Server base path (e.g. myserver/home/name/data/).
        """
        self.base_path = base_path

    @abstractmethod
    def getFile(self, file_path, save_path):
        """
        Method to download the file from the server and to save it to save_path.
        Args:
            file_path (str): File path on the server.
            save_path (str): Path where the file should be saved.

        Returns:
            success (bool): If the download was successful.
            error (str): If the download wasn't successful,
                there will be an error.
        """
        pass


class Internet(Server):
    """
    This class represents an internet server.
    """
    def getFile(self, file_path, save_path):
        file_path = urllib.parse.urljoin(self.base_path, file_path)
        save_path = File(save_path)
        save_path.create_dir()
        try:
            with urllib.request.urlopen(file_path) as response,\
                    save_path.open() as out_file:
                try:
                    shutil.copyfileobj(response, out_file)
                    if save_path.available:
                        return True, None
                    else:
                        return False, response
                except:
                    return False, response
        except urllib.error.HTTPError:
            return False, 404
