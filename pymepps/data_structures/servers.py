#!/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 16.11.16

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
import cgi
import logging
import os
import shutil
import urllib.error
import urllib.request

from pymepps.utilities.path_encoder import PathEncoder
from .file import File

logger = logging.getLogger(__name__)


class DataServer(object):
    def __init__(self, path_template):
        """
        Base class for a data server, needed by model class, to download/move
        weather model data.
        """
        self.path_template = path_template

    @abc.abstractmethod
    def _download_data(self, download_path, dest_path):
        pass

    def get_data(self, dest_path=None, date=None, num=None):
        path_encoder = PathEncoder(self.path_template, date=date,
                                   undet_numbers=num)
        in_paths = path_encoder.get_encoded()
        output_paths = []
        for path in in_paths:
            temp_path = self._download_data(path, dest_path)
            if temp_path is not None:
                output_paths.append(temp_path)
        return output_paths


class WettermastServer(DataServer):
    """
    The Wettermast server (combination of ssh and samba server) to get the
    Wettermast Hamburg site data.
    """
    pass


class InternetServer(DataServer):
    def __init__(self, path_template):
        """
        An internet server based on an url template. Most weather forecast data
        is delivered by this type of server.

        Attributes
        ----------
        path_template : str
            The path template which should be encoded.

        Parameters
        ----------
        path_template : str
            The path template which should be encoded. For possible commands
            of the path template see at the documentation of PathTemplate.

        Methods
        -------
        get_data(dest_path, date, num) :
            Method to download the data to the destination path.
        """
        super().__init__(path_template)

    def _download_data(self, download_path, dest_path=None):
        """
        Download data from download path to destination path. The file name is
        determined by the header of the download path. The file is downloaded
        with urllib.request and shutil.copyfileobj.

        Parameters
        ----------
        download_path : str
            The url which should be downloaded. Queries are supported.
        dest_path : str, optional
            The destination path where the downloaded file should be saved.
            The file name is determined automatically by the header of the url.
            If it's None the destination path is set to current working
            directory. Default is None.

        Returns
        -------
        str
            The path to the downloaded file. If this is None the file couldn't
            be downloaded.
        """
        if dest_path is None:
            dest_path = os.getcwd()
            logger.info('The destination path was none and is set to the '
                        'current working directory {0:s}'.
                        format(dest_path))
        try:
            with urllib.request.urlopen(download_path) as response:
                _, params = cgi.parse_header(
                    response.headers.get('Content-Disposition', ''))
                try:
                    file_name = params['filename']
                except KeyError:
                    file_name = download_path.split('/')[-1]
                if file_name != '':
                    save_file = File(os.path.join(dest_path, file_name))
                    save_file.create_file()
                    try:
                        with save_file.open() as fopen:
                            data = response.read()
                            fopen.write(data)
                        if save_file.available:
                            return save_file.path
                        else:
                            logger.info('The url {0:s} couldn\'t be downloaded'
                                        ' to {1:s}, due to {2:s}'.
                                        format(download_path,
                                               save_file.path,
                                               response))
                            return None
                    except:
                        logger.info('The url {0:s} couldn\'t be downloaded'
                                    ' to {1:s}, due to {2:s}'.
                                    format(download_path,
                                           save_file.path,
                                           response))
                        return None
        except urllib.error.HTTPError:
            logger.info('The url {0:s} couldn\'t be downloaded, due to 404'.
                        format(download_path))
            return None



class DiskServer(DataServer):
    """
    A server where the files are stored on an accessible disk. This is the
    right server type if you have run your own model.
    """
    pass



def url_downloader(url, save_file=None):
    """
    Function to download an url and save if to the specified path.

    Parameters
    ----------
    url : str
        The url which should be download.
    save_file : str or None, optional

    Returns
    -------

    """
