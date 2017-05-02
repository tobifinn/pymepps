Data structure
==============

Pymepps is a system to read and process meteorological data. So we defined some
base types and tools for an easier read and process workflow.


File handlers
-------------
File handlers are used to read in the data. A file handler is working on file
basis, such that one file handler could only process one file. There different
file handlers for different file types. Some are only to read in spatial data
and some could only read in time series data. But all file handlers have three
common methods:
    * Method to load the data into the memory
    * Method to get the variable names within the file
    * Method to extract a variable and prepare the variable for the dataset.

The method to extract a variable uses a message based interface so that similar
files could be merged within a dataset.


NetCDF handler
^^^^^^^^^^^^^^
The NetCDF handler could be used to read in netcdf files. The NetCDF handler is
based on the xarray and the netcdf4 package, so it is also possible to load
opendap data streams with this handler. The NetCDF handler could be used to read
in spatial and time series files. At the moment the load of time series data
with this handler is only tested for measurement data from the
"Universtät Hamburg".

Grib handler
^^^^^^^^^^^^
The grib handler could be used to read in grib1 and grib2 files. The grib
handler is based on the pygrib package. The grib handler could be only used to
read in spatial data, due to the requirements of a grib file.


At the moment there are only these two differnt file handlers, but it is planned
to implement some other file handlers to read in hdf4/5 and csv based data.



Dataset
-------
Datasets are used to combine file handlers and to manage the variable selection.
A dataset is working at multiple file level. The messages of the file handlers
are bundled to spatial or time series data. So the two different dataset types
the spatial and the times series dataset have a merge method in common.


Spatial dataset
^^^^^^^^^^^^^^^
A spatial dataset is used to combine the file handlers, which are capable to
read in spatial data. The spatial dataset interacts on the same level as the
climate data operators (cdo). So it is possible to process the data of a spatial
dataset with some of the cdos. A method for the general support of the cdos is
planned.The spatial dataset also creates the grid for the spatial data. The grid
could be either predefined or is read in with the griddes function from the cdo.


Time series dataset
^^^^^^^^^^^^^^^^^^^
A time series dataset is ised to combine the times series file handlers. A time
series dataset is valid for a given coordinates, so it is possible to defined
a coordinate tuple. If no coordinate tuple is set the time series dataset tries
to get the coordinates from the data origin.


Data
----
Two different data types are defined within this package – spatial data and
time series data. The data types are used to process and plot the data. The
data types are working at variable level. Both data types are like a wrapper
around powerful packages – pandas and xarray.

Spatial data
^^^^^^^^^^^^
The spatial data is represented within the SpatialData data type. The data type
is based on xarray.DataArray and could be seen as NetCDF like cube. So it is
easy to save the data as NetCDF file. The spatial data contains a grid, defining
the horizontal grid coordinates of the data. With this grid it is further
possible to remap the data and to transform the data to time series data. These
features are used to process the data in statistical models.

Time series data
^^^^^^^^^^^^^^^^
The time series data is represented within the TSData data type. The data type
is based on pandas.Series and pandas.DataFrame and could be seen as table like
data.
