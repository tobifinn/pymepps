#pymepps
pymepps is a **Py**thon module to implement a **me**teorological **p**ost-
**p**rocessing **s**ystem.</br>
The system contains following modules:
<li>System: The module to start the system and to read the config files.
<li>Model: With this module meteorological weather forecast model data could be
downloaded, constraint and saved from various data sources.
<li>Station: With this module weather station data could be downloaded, readed
and saved from various data sources.
<li>Forecast: With this module scripts could be loaded to manipulate the
model data and to forecast the weather.
<li>Verification: With this module the performance of the models and the
forecasts could be verified against measurement sites and/or grid analyses.
<li>Plot: With this module the data (model, station, forecast or verification)
could be plotted into a map or to a meteogram.


This repository is in the pre-alpha (V. 0.0.1) stadium.
It will grow with the time.


Requirements
------------
Written using Python 3.5.<br>
It requires:
<li>Numpy
<li>Matplotlib
<li>Basemap
<li>Pandas
<li>Xarray
<li>Netcdf-4
<li>CDO