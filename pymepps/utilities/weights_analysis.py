#!/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 26.09.17
#
# Created for pymepps
#
# @author: Tobias Sebastian Finn, tobias.sebastian.finn@studium.uni-hamburg.de
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
This module is used for the master thesis of Tobias Sebastian Finn
It is used to load the weights of an ensemble Kalman filter and to process
these.
"""


# System modules
import logging
import os
import datetime
import re

# External modules
import numpy as np
import xarray as xr

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# Internal modules


logger = logging.getLogger(__name__)


def process_file(file):
    with open(file, 'r') as fh:
        lines = fh.readlines()
    concat_lines = [lines[l]+lines[l+1] for l in range(0, len(lines), 2)]
    processed_lines = [re.findall(r"(?<![a-zA-Z:])[-+]?\d*\.?\d+", l)
                       for l in concat_lines]
    return np.array(processed_lines, dtype=np.float32)


def extract_date(file):
    splitted_path = os.path.normpath(file).split(os.path.sep)
    read_date = datetime.datetime.strptime(splitted_path[7], '%Y%m%d_%H%M')
    timeshift = datetime.timedelta(hours=1)
    return read_date + timeshift


def get_weights(files):
    weights_array = np.array([process_file(f) for f in files])
    date = np.array([extract_date(f) for f in files], dtype='datetime64[ns]')
    data_array = xr.DataArray(
        data=weights_array,
        coords=dict(
            time=date,
            ensemble_1=np.arange(weights_array.shape[1]),
            ensemble_2=np.arange(weights_array.shape[2])
        ),
        dims=['time', 'ensemble_1', 'ensemble_2']
    )
    ens_weights = data_array[:, :, :-1]
    det_weights = data_array[:, :, -1]
    return ens_weights, det_weights


def diagonalize_xr(xr_array):
    return xr_array.where(np.eye(xr_array.shape[1], dtype='bool'))


def antidiagonalize_xr(xr_array):
    return xr_array.where(~np.eye(xr_array.shape[1], dtype='bool'))


def plot_weights(weights, save_path=None, colored_members=None,
                 title=r'Wind assimilation, lowest model layer', ylim=None):
    fig, ax = plt.subplots()
    colored_cnt = 0
    new_icon = ax.axvline(datetime.datetime(2016, 6, 7), c='0.2',
                          label='New ICON run')
    label_list = [new_icon, ]
    for k, mem in enumerate(weights.ensemble_1):
        mem_data = weights.sel(ensemble_1=mem)
        if colored_members is not None:
            colored = colored_members.sel(ensemble_1=k)
        else:
            colored = False
        if colored:
            plt_col, = ax.plot(
                mem_data.indexes['time'], mem_data,
                label='member {0:d}'.format(int(mem)))
            label_list.append(plt_col)
            colored_cnt += 1
        else:
            plt_unimp, = ax.plot(
                mem_data.indexes['time'], mem_data,
                label='unimportant member',
                color='0', alpha=0.05)
    label_list.append(plt_unimp)
    if ylim is None:
        ax.set_ylim(np.floor(weights.min() * 2) / 2,
                    np.ceil(weights.max() * 2) / 2)
    else:
        ax.set_ylim(*ylim)
    ax.set_ylabel('Mean weight ($\overline{\mathbf{W}}^a$)')
    ax.set_xlabel('2016-06-06 – 2016-06-07')
    hours_fmt = mdates.DateFormatter('%Hz')
    ax.xaxis.set_major_formatter(hours_fmt)
    xtick_index = (mem_data.indexes['time'].hour % 3 == 0) & \
                  (mem_data.indexes['time'].minute % 60 == 0)
    ax.set_xticks(mem_data.indexes['time'][xtick_index])
    plt.title(title)
    plt.legend(handles=label_list, labels=[l.get_label() for l in label_list],
               fancybox=False)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    plt.show()
