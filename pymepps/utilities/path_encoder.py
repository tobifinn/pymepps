# -*- coding: utf-8 -*-
"""
Created on 28.09.16

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
import logging
import re
import itertools
import datetime
from collections import Counter

# External modules
import numpy as np

# Internal modules

logger = logging.getLogger(__name__)


class PathEncoder(object):
    def __init__(self, base_path, date=None, undet_numbers=None):
        """
        This template decode paths and can calculate paths, replace date, text
        and undetermined numbers commands.
        Commands:
            ${X}$: Replace with X
                X could be:
                    text(Y): text will be replaced by Y
                        (e.g. text(SP1,SP2,IP1) => [SP1, SP2, SP3])
                    date(Y): date will be replaced by specified date
                        with specific format Y
                        (e.g. date(%Y%m%d_%H) => 20160518_12)
                    unde(Y): unde stands for undetermined numbers and is
                        replaced by specified undet_numbers with a given
                        format Y. For possible format types look [1]
                        (e.g. dete(02d) => [00,01,02,03,04,05])
            @{X}@: Calculate X. It is possible to use numpy commands for the
                calculations. Be careful, the calculations are done with the
                eval() function!
                (e.g. @{1+4+6}@ => 11)
        [1] https://docs.python.org/3/library/string.html#formatstrings

        Parameters
        ----------
        base_path : str
            The path template which should be decoded. The path template is
            composed of the commands showed above.
        date : datetime.datetime, optional
            The path is valid for this date. For numerical weather models,
            this is usually the initialization date. If there is no valid date
            or it isn't needed this could be None. Default is None.
        numbers : list(int/float), optional
            If there are numbers within the path, which are given now given.
            For numerical weather model path, these are usually the model lead
            times. If there are no numbers or aren't needed this could be None.
            Default is None.
        """
        self.base_path = base_path
        self.undet_numbers = undet_numbers
        self.date = date
        self.replace_delimiters = ("${", "}$")
        self.calc_delimiters = ("@{", "}@")
        self.replace_methods = {
            "text": self._text,
            "date": self._date,
            "numb": self._unde}
        logger.debug('Url template: {0:s}\n'
                     'Undetermined numbers: {1:s}\n'
                     'Date: {2:s}'.format(
            str(self.base_path), str(undet_numbers), str(date)))

    def get_file_number(self):
        return len(self.get_encoded())

    def get_encoded(self):
        """
        Encode the path with given data.

        Returns
        -------
        list of str
            List with encoded paths.
        """
        url_list = self._replace_static(self.base_path)
        for k, url in enumerate(url_list):
            url_list[k] = self._calculation(url)
        logger.debug(str(url_list))
        return url_list

    def _replace_static(self, url_temp):
        start, end = self.replace_delimiters
        escaped = (re.escape(start), re.escape(end))
        regex = re.compile('%s(.*?)%s' % escaped, re.DOTALL)
        replaced_url = []
        splitted_url = regex.split(url_temp)
        logger.debug('Splitted {0:s} to {1:s}'.format(url_temp, str(splitted_url)))
        for i, part in enumerate(splitted_url):
            try:
                part = self.replace_methods[part[:4]](part[5:-1])
            except:
                part = [part, ]
            replaced_url.append(part)
        logger.debug(replaced_url)
        replaced_url = tuple(itertools.product(*replaced_url))
        logger.debug(replaced_url)
        cnt = Counter(splitted_url)
        splitted_url_same = [True if cnt[p]>1 else False for p in splitted_url]
        cleaned_url = []
        for url in replaced_url:
            cnt = Counter(url)
            url_same = [True if cnt[p] > 1 else False for p in url]
            if url_same == splitted_url_same:
                cleaned_url.append(url)
        combined_url = [''.join(u) for u in replaced_url]
        return combined_url

    def _calculation(self, url):
        """
        Methods calculations triggered by the calculate delimiters.
        Attention, this method uses eval() as method to calculate string type
        operations, so be careful!

        Args:
            url:

        Returns:

        """
        start, end = self.calc_delimiters
        escaped = (re.escape(start), re.escape(end))
        regex = re.compile('%s(.*?)%s' % escaped, re.DOTALL)
        replaced_url = []
        for i, part in enumerate(regex.split(url)):
            try:
                part = str(eval(part))
            except:
                part = part
            replaced_url.append(part)
        url = "".join(replaced_url)
        return url

    @staticmethod
    def _text(*args):
        """
        Split the first argument by comma and return it.
        Args:
            *args:

        Returns:
            text (list[str]): The first argument splitted by comma as list with
                strings.
        """
        text = args[0].split(",")
        return text

    def _date(self, date_format):
        """
        Method to evaluate an date regex (!init)
        in the url with given date.

        Args:
            date_format(str): The date format for the initialization regex.
                This date format is the same date format as datetime format.
        """
        if isinstance(self.date, datetime.datetime):
            return [self.date.strftime(date_format), ]
        else:
            logger.error('The date isn\'t set yet, but is called!')


    def _unde(self, fixed_format='03d'):
        """

        Args:
            fixed_format

        Returns:

        """
        if hasattr(self.undet_numbers, '__iter__') and \
                not isinstance(self.undet_numbers, str):
            leads = ['{number:fixed_format}'.format(
                        fixed_format=fixed_format, number=lead)
                     for lead in self.undet_numbers]
            return leads
        else:
            logger.error('The undetermined numbers aren\'t set yet,'
                         'but are called!')
