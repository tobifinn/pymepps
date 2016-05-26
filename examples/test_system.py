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
import os.path
import datetime as dt

# External modules
import datetime

# Internal modules
import pymepps
import pymepps.data

__version__ = "0.1"

base_path = "/home/tfinn/test"

wm = pymepps.System("Wettermast_forecast", base_path)
wm.addModel(name="arome_metno", inits=[0, 6, 12, 18], leads=range(0, 67, 1),
            server_model=pymepps.data.Internet
                ("http://thredds.met.no/thredds/fileServer/arome25/"),
            files=pymepps.data.PathTemplate("arome_metcoop_${text(default,test)}$2_5km_${init(%Y%m%d_%H)}$.nc"),
            data_path=os.path.join(base_path, "data", "arome_metno"),
            base_logger=pymepps.BaseLogger(os.path.join(base_path, "log")))

wm.addModel(name="gfs", inits=[0, 6, 12, 18], leads=range(0, 12, 6),
            server_model=pymepps.data.Internet
                ("ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/"),
            files=pymepps.data.PathTemplate("gfs.${init(%Y%m%d%H)}$/gfs.t${init(%H)}$z.pgrb2.0p25.f${lead(3)}$"),
            data_path=os.path.join(base_path, "data", "gfs"),
            base_logger=pymepps.BaseLogger(os.path.join(base_path, "log")))

wm.start()
