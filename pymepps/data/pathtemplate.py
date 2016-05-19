# -*- coding: utf-8 -*-
"""
Created on 07.02.16
Created for pymepps

@author: Tobias Sebastian Finn, t.finn@meteowindow.com, University of Hamburg

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
# External modules
import itertools
import re

# Internal modules

__version__ = "0.5"


class PathTemplate(object):
    def __init__(self, base_path):
        """
        This template decode paths and can calculate paths, replace init, text
        and lead commands.
        Commands:
            ${X}$: Replace with X
                X could be:
                    text(Y): text will be replaced by Y
                        (e.g. text(SP1,SP2,IP1) => [SP1, SP2, SP3])
                    init(Y): init will be replaced by init date
                        with specific format Y
                        (e.g. init(%Y%m%d_%H) => 20160518_12)
                    lead(): lead will be replaced by lead times
                        (e.g. lead() => [0,1,2,3,4,5])
            @{X}: Calculate X
                (e.g. @{1+4+6}@ => 11)
        Args:
            base_path (str): The path which should be decoded
        """
        self.base_path = base_path
        self.leads = []
        self.date = None
        self.replace_delimiters = ("${", "}$")
        self.calc_delimiters = ("@{", "}@")
        self.temp_methods = {
            "text": self._text,
            "init": self._init,
            "lead": self._lead}

    def generatePaths(self, leads=[], date=None):
        try:
            self.leads = leads
            self.date = date
            url_list = self._replace_static(self.base_path)
            url_list = self._replace_lead(url_list)
            url_list = ["".join(url) for url in url_list]
            #url_list = [self._calculation("".join(url)) for url in url_list]
            return url_list
        except:
            return False

    def _replace_static(self, url):
        start, end = self.replace_delimiters
        #url = url.replace(start+"lead"+end, self.leads)
        escaped = (re.escape(start), re.escape(end))
        regex = re.compile('%s(.*?)%s' % escaped, re.DOTALL)
        replaced_url = []
        for i, part in enumerate(regex.split(url)):
            try:
                part = self.temp_methods[part[:4]](part[5:-1])
            except:
                part = [part, ]
            replaced_url.append(part)
        url = list(itertools.product(*replaced_url))
        return url

    def _replace_lead(self, url_list):
        new_url_list = []
        for key, url in enumerate(url_list):
            if "§" in url:
                for lead in self.leads:
                    new_url_list.append([w.replace("§", str(lead)) for w in url])
            else:
                new_url_list.append(url)
        return new_url_list

    def _calculation(self, url):
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
        text = args[0].split(",")
        return text

    def _init(self, date_format):
        """
        Method to evaluate an initialization regex (!init)
        in the url with given date.
        """
        return [self.date.strftime(date_format), ]

    def _lead(self, *args):
        leads = "§"
        return leads
