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

# System modules
import logging
import os
from functools import partial

# External modules
CDO = None
try:
    from cdo import Cdo
    CDO = Cdo()
except ImportError:
    raise ImportWarning('For full support please install the cdo package via '
                        '"pip install cdo"')

# Internal modules
from pymepps.utilities.file import File
from pymepps.utilities import MultiThread



logger = logging.getLogger(__name__)


def selnearest(ds, lonlat, new_path=None, inplace=False, in_opt=None,
               options=None, processes=1):
    logger.info('Started selnearest for {0:d} files'.format(
        len(ds.file_handlers)))
    multiproc = MultiThread(processes)
    single_fh_func = partial(
        _single_fh_selnearest,
        lonlat=lonlat,
        new_path=new_path,
        inplace=inplace,
        in_opt=in_opt,
        options=options)
    new_file_handlers = multiproc.map(single_fh_func, ds.file_handlers)
    logger.info('Finished sellonlatbox')
    return new_file_handlers


def _single_fh_selnearest(fh, lonlat, new_path=None, inplace=False,
                          in_opt=None, options=None):
    in_file, out_file = cdo_path_helper(file_path=fh.file,
                                        new_path=new_path,
                                        inplace=inplace)
    options_str = ''
    if isinstance(options, str):
        options_str = options
    input_str = in_file
    if isinstance(in_opt, str):
        input_str = in_opt.replace('%FILE%', in_file)
    if not os.path.isfile(out_file) and in_file!=out_file:
        CDO.remapnn(
            'lon={0:.4f}_lat={1:.4f}'.format(lonlat[0], lonlat[1]),
            input=input_str,
            output=out_file,
            options=options_str)
        new_fh = fh.__class__(out_file)
    else:
        new_fh = fh
    return new_fh


def sellonlatbox(ds, lonlatbox, new_path=None, inplace=False, in_opt=None,
                 options=None, processes=1):
        logger.info('Started sellonlatbox for {0:d} files'.format(
            len(ds.file_handlers)))
        multiproc = MultiThread(processes)
        single_fh_func = partial(
            _single_fh_sellonlatbox,
            lonlatbox=lonlatbox,
            new_path=new_path,
            inplace=inplace,
            in_opt=in_opt,
            options=options)
        new_file_handlers = multiproc.map(single_fh_func, ds.file_handlers)
        logger.info('Finished sellonlatbox')
        return new_file_handlers


def _single_fh_sellonlatbox(fh, lonlatbox, new_path=None, inplace=False,
                            in_opt=None, options=None):
        in_file, out_file = cdo_path_helper(file_path=fh.file,
                                            new_path=new_path,
                                            inplace=inplace)
        options_str = ''
        if isinstance(options, str):
            options_str = options
        input_str = in_file
        if isinstance(in_opt, str):
            input_str = in_opt.replace('%FILE%', in_file)
        if not os.path.isfile(out_file) and in_file!=out_file:
            CDO.sellonlatbox(
                lonlatbox[0],
                lonlatbox[2],
                lonlatbox[3],
                lonlatbox[1],
                input=input_str,
                options=options_str)
            new_fh = fh.__class__(out_file)
        else:
            new_fh = fh
        return new_fh


def griddes(*args, **kwargs):
    if CDO is not None:
        return CDO.griddes(*args, **kwargs)
    else:
        logger.warning('To load the grid description with the cdos you '
                       'need to install the cdos!')
        return None


def cdo_path_helper(file_path, new_path=None, inplace=False):
    file_obj = File(file_path)
    in_file = file_obj.path
    if inplace:
        out_file = in_file
    else:
        file_name = file_obj.get_basename()
        if file_obj.get_dir == new_path or new_path is None:
            file_name = '{0:s}_{1:s}'.format(file_name, 'sliced')
        if new_path is not None:
            out_file = os.path.join(new_path, file_name)
        else:
            out_file = os.path.join(file_obj.get_dir(), file_name)
    logger.debug(
        'Set output path to {0:s} for file {1:s}'.format(out_file, in_file))
    return in_file, out_file
