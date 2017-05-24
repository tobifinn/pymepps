#!/bin/env python
# -*- coding: utf-8 -*-
#
#Created on 23.05.17
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

# External modules
import pandas as pd

# Internal modules
from pymepps.metdata import TSData


logger = logging.getLogger(__name__)


def rank_hist(ens_ts, truth_ts):
    """
    Calculate a rank histogram time series.

    Parameters
    ----------
    ens_ts: TSData
        A TSData instance with the ensemble members as columns and the valid 
        time as row.
    truth_ts: TSData
        The TSData which should be used as reference time series. These 
        values will be ranked within the ensemble time series.

    Returns
    -------
    rank_ts: TSData
        The rank as time series with the valid times as time axis.
    """
    rank_hist_values = ens_ts.data.T
    # Trick to get values if the truth is lower than the lowest ensemble member
    rank_hist_values.loc[0, :] = 0
    rank_hist_values = rank_hist_values.sort_index()
    rank_ts = pd.Series({col: rank_hist_values.index[
                truth_ts.data.loc[col] > rank_hist_values.loc[:, col]].max()
            for col in rank_hist_values.columns})
    rank_ts = TSData(rank_ts, 'rank_hist', lonlat=truth_ts.lonlat)
    return rank_ts


def rank_hist_wo_bias(ens_ts, truth_ts):
    """
    Calculate a rank histogram time series with a bias correction. The bias is 
    calculated as the mean of the ensemble mean - the observations mean.


    Parameters
    ----------
    ens_ts: TSData
        A TSData instance with the ensemble members as columns and the valid 
        time as row.
    truth_ts: TSData
        The TSData which should be used as reference time series. These 
        values will be ranked within the ensemble time series.

    Returns
    -------
    rank_ts: TSData
        The rank as time series with the valid times as time axis.
    """
    ens_ts = ens_ts.copy()
    bias_df = pd.DataFrame(
        {'chh': ens_ts.data.T.mean(), 'obs': truth_ts.data}).dropna().mean()
    bias = bias_df['chh'] - bias_df['obs']
    ens_ts.data = ens_ts.data-bias
    return rank_hist(ens_ts, truth_ts)