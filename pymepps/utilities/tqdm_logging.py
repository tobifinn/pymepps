#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 18.05.17
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
"""
This module is a shortcut to implement teh tqdm progressbar within the logging
module. To add the tqdm capability to a logger you need to add the intialized 
tqdm_handler to the logger as handler. This module is based on [1]_.

..[1] https://github.com/tqdm/tqdm/issues/193
"""

# System modules
import logging
from tqdm import tqdm
import colorlog

# External modules

# Internal modules


logger = logging.getLogger(__name__)


class TqdmHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        tqdm.write(msg)


tqdm_handler = TqdmHandler()
tqdm_handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(name)s | %(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%d-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'white',
        'SUCCESS:': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white'}, ))
