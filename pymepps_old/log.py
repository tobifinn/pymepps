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
import logging
import unicodedata

# External modules

# Internal modules
from .data import File

__version__ = "0.1"


class BaseLogger(object):
    """
    The base logger class, which could create a logger.
    """
    def __init__(self, log_path):
        log_path = File(log_path)
        log_path.create_dir()
        self.log_path = log_path.get_dir()

    def createLogger(self, name):
        return Logger(name, self.log_path)

class Logger(object):
    """
    The logger class, for logging of the system components.
    """
    def __init__(self, logger_name, log_path):
        self._logger = None
        self.logger_name = logger_name
        self.log_file = os.path.join(log_path, self.logger_name+".log")


    def initLogger(self):
        """
        initialize the logger and write it into the logging path.
        """
        self._logger = logging.getLogger(self.logger_name)
        self._logger.setLevel(logging.INFO)
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        self._logger.addHandler(fh)
        self._logger.addHandler(ch)
        self.info("Logger initialized")

    def shutdown(self):
        """ Method to shutdown the logger
        """
        self.info("Logger shutdown")
        for handler in self._logger.handlers:
            self._logger.removeHandler(handler)
            del handler
        logging.shutdown()
        del self._logger

    @property
    def available(self):
        return self.check()

    def check(self):
        """ Check if the logger is initialized
        """
        if self._logger is None:
            return False
        else:
            return True

    def info(self, message):
        """ Write an info message into log file.

        Args:
            message (str): message which should be writed into log file
        """
        if self.check():
            self._logger.info(message)

    def error(self, message):
        """ Write an error message into log file and print it.

        Args:
            message (str): message which should be writed into log file
        """
        if self.check():
            self._logger.error(message)
            print(message)

    def warning(self, message):
        """ Write a warning message into log file.

        Args:
            message (str): message which should be writed into log file
        """
        if self.check():
            self._logger.warning(message)