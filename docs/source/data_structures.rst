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
planned. The spatial dataset also creates the grid for the spatial data. The
grid could be either predefined or is read in with the griddes function from the
cdo.


Time series dataset
^^^^^^^^^^^^^^^^^^^
A time series dataset is used to combine the times series file handlers. A time
series dataset is valid for a given coordinates, so it is possible to defined
a coordinate tuple. If no coordinate tuple is set the time series dataset tries
to infer the coordinates from the data origin.


Data
----
The main data types are based on xarray and pandas. Within this package these
data structures are extended by accessors. The accessor could be accessed with a
property named pp. With the use of accessors the namespace of the base data
structures remains clean.

Spatial data
^^^^^^^^^^^^
Spatial data is loaded as xarray.DataArray. The SpatialAccessor extends the
DataArray structure by grid capabilities. With the grid it is possible to remap
and slice the data based on coordinates and other grids.

Time series data
^^^^^^^^^^^^^^^^
Time series data is loaded as pandas.Series or pandas.DataFrame. The
PandasAccessor extends the pandas structure by some station specific
capabilities. It is planned to expand the accessor in the future.
