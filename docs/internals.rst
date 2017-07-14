Data description
================
The following text describes the licenses of the used data and how the data was
generated. Some of the data might have a large size.

Station data
------------
The following explanation is for the station data folder.

wettermast.nc
^^^^^^^^^^^^^
The wettermast.nc is extracted from original
`Wettermast Hamburg <https://wettermast.uni-hamburg.de>`_ data. We get the permission of
Ingo Lange to use the data in a sliced manner.

We extracted the data from the original NetCDF-file and sliced a time period of
5 days and used only the 2 metre temperature.


Grid data
---------
All of the grids are generated with the cdo griddes command. In the following
the grids and their origin are described.

gaussian_y
^^^^^^^^^^
The gaussian_y is a gaussian grid with an equal-spaced x coordinate and an
unequal-spaced y coordinate. The grid is copied from the `cdo documentation
<https://code.zmaw.de/projects/cdo/embedded/index.html#x1-150001.3.2>`_.

lcc
^^^
The lcc is a lambert conformal conic grid. The proj4 description is used to read
in the grid as projection grid. The grid is extracted from the met.no
Arome-MetCoOp model and is based on data from MET Norway. The data from the
`Thredds-OPeNDAP <http://thredds.met.no/thredds/dodsC/meps25files/meps_det_extracted_2_5km_latest.nc>`_ server is used.
The license of the original data is: `Norwegian license for public data (NLOD)
and Creative Commons 4.0 BY Internasjonal <https://www.met.no/en/free-meteorological-data/Licensing-and-crediting>`_.

lon_lat
^^^^^^^
The lon_lat is a lonlat grid with equal-spaced longitude and latitude
coordinates. It is extracted from the GFS model with a resolution of
0.25°x0.25°. The original data was used from the
`UCAR-edu Thredds <http://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_0p25deg/GFS_Global_0p25deg_20170410_0600.grib2>`_ server.
The original GFS data `is available for free in the public domain under
provisions of U.S. law <https://en.wikipedia.org/wiki/Global_Forecast_System>`_.
