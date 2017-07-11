Toy grid data
=============
The following example shows how to use the grid capabilities of an extended
xarray.DataArray.

Create toy data
---------------
Firstly we need to generate the toy data. So the first step is to load an
arbitrary grid and generate a DataArray based on this grid.

.. ipython:: python

    import os
    import datetime
    import numpy as np
    import xarray as xr
    import pandas as pd
    import matplotlib.pyplot as plt
    import pymepps

    random_state = np.random.RandomState(42)

    # Load the grid file into the grid builder
    grid_path = "source/ipy_examples/data/lon_lat"
    print(os.path.realpath(grid_path))
    builder = pymepps.GridBuilder(grid_path)

    # Build the grid
    grid = builder.build_grid()

    # Print the grid shape
    shape = grid.shape
    print(shape)

    # Now lets generate some toy data
    white_noise = random_state.normal(0, 5, size=(shape))
    lat_temp = 273.15+45-np.abs(np.linspace(90, -90, shape[0]))
    lat_temp = lat_temp.reshape(-1, 1).repeat(shape[1], axis=1)
    toy_data = white_noise + lat_temp

    coords = {
        'time': (('time', ), [datetime.datetime.utcnow(), ]),
        'y': (('y', ), np.arange(shape[0])),
        'x': (('x', ), np.arange(shape[1])),}
    dims = ['time', 'y', 'x']
    toy_array = xr.DataArray(
        data=toy_data.reshape(1, *shape),
        coords=coords,
        dims=dims)

    print(toy_array)

    # Now we have to set the grid of the toy data
    toy_array.pp.grid = grid
    # To set the grid coordinates as coordinates for our toy data
    toy_array = toy_array.pp.set_grid_coordinates()

    print(toy_array)

Slice a lonlat box
------------------
We created our toy data, now we lets slice an area over the beautiful city
Hamburg. With sellonlatbox we could slice an area with given longitude and
latitude boundaries (west, north, east, south). The grid is automatically sliced
and set to the resulting sliced array.

.. ipython:: python

    sliced_array = toy_array.pp.sellonlatbox([9, 55, 11, 52])
    print(sliced_array)

    @savefig examples_toy_grid_sliced_box.png
    sliced_array.plot()

Select the nearest grid point
-----------------------------
It is even possible to select a point by given latitude and longitude values.
The to_pandas method selects the nearest grid point to the given
longitude-latitude pair with the haversine formula. Time axes are automatically
used as index. All other dimensions are flatten and used as multi-index column
for the resulting dataframe. If no coordinate pair is given, also the grid is
used for the multiindex.

.. ipython:: python

    extracted_point = sliced_array.pp.to_pandas((10, 53.5))
    print(extracted_point)

    flatten_grid = sliced_array.pp.to_pandas()
    print(flatten_grid)

Remapping
---------
With the grid capabilities it is also possible to remap the data. There are two
different interpolation methods implemented. The nearest neighbour interpolation
uses the nearest grid points as values while the bilinear interpolation tries to
infer with a linear approach the values for given grid points. The here shown
example is for structured grids, but there are also interpolation methods for
unstructured grids defined.

.. ipython:: python

    # First we need to generate a new grid.
    grid_path = "source/ipy_examples/data/gaussian_y"
    builder = pymepps.GridBuilder(grid_path)
    new_grid = builder.build_grid()

    # Lets do remapping with a nearest neighbour approach
    nn_array = toy_array.pp.remapnn(new_grid)

    # Lets do remapping with a bilinear approach
    bil_array = toy_array.pp.remapbil(new_grid)

    # Lets show the difference between the data
    fig, ax = plt.subplots(3, sharex=True)
    toy_array.plot(ax=ax[0])
    ax[0].set_title('Original')
    nn_array.plot(ax=ax[1])
    ax[1].set_title('Remapnn')
    bil_array.plot(ax=ax[2])
    ax[2].set_title('Remapbil')
    @savefig examples_toy_grid_remapped_all.png
    fig.tight_layout()
