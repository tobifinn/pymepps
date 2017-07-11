Spatial data from thredds server
================================
The following example shows how to get data from the met.no thredds server.

Load grid
---------
Due to missing cdo, we preloaded a grid file for the met.no Arome model. We need
to load the grid.

.. ipython:: python

    import xarray as xr
    import pymepps

    try:
        builder = pymepps.GridBuilder('ipy_examples/data/llc')
    except KeyError: # If the html is compiled in the docs directory
        builder = pymepps.GridBuilder('source/ipy_examples/data/llc')
    grid = builder.build_grid()

Load dataset
------------
The first step we have to do is to load the data from the thredds server into a
SpatialDataset. We could use the NetCDF4-engine to load the data into the
dataset, because of the opendap capabilities.

.. ipython:: python

    # Define the thredds server path
    metno_path = 'http://thredds.met.no/thredds/dodsC/meps25files/' \
        'meps_det_pp_2_5km_latest.nc'

    metno_ds = pymepps.open_model_dataset(metno_path, 'nc', grid=grid)
    # Print the dataset information
    print(metno_ds)
    # Print the variable names of the dataset
    print(metno_ds.var_names)

Select variable
---------------
Now we loaded the dataset and printed the content of the dataset. The next step
is to select a variable, which should be extracted. Let's extract the
temperature in 2 metre height, the data is downloaded from the server. We could
see that the dataset added and normalized the coordinates. Also the grid is
added to the DataArray.

.. ipython:: python

    # Show the content of a DataArray loaded with xarray
    xr_ds = xr.open_dataset(metno_path)
    print(xr_ds['air_temperature_2m'])

    # Load the data
    t2m = metno_ds.select('air_temperature_2m')

    # Print content of t2m
    print(t2m)

Plot temperature field
----------------------
We extracted the temperature in 2 m height to a xarray.DataArray. Now lets plot
the field for the first time step with


.. ipython:: python

    # Slice the data
    time_sliced_t2m = t2m.isel(validtime=0)

    @savefig examples_thredds_server_temp_field.png
    time_sliced_t2m.plot()

Plot time series for grid point
-------------------------------
Lets plot a time series for a given grid point. We select the nearest grid point
to the `"Wettermast Hamburg" <http://wettermast.uni-hamburg.de/>`_. We could use
the plotting module of pandas to plot the series.

.. ipython:: python

    # Squeeze the data
    squeezed_t2m = t2m.squeeze()

    # We have to set the grid again
    squeezed_t2m = squeezed_t2m.set_grid(grid)

    # Now lets select the Wettermast Hamburg grid point
    lonlat = (10.105139, 53.519917)
    wm_ts = squeezed_t2m.pp.to_pandas(lonlat)

    @savefig examples_thredds_server_wm_ts.png
    wm_ts.plot()
