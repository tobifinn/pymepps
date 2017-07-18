"""
Load a thredds dataset
======================

In the following example we will load a thredds dataset from the
norwegian met.no thredds server.

"""

import numpy as np
import matplotlib.pyplot as plt

import pymepps


######################################################################
# The first step is to load the dataset. This will be performed with
# pymepps.open\_model\_dataset. The NetCDF4 backend is also supporting
# opendap paths. So we could specify nc as data type.
# 

metno_path = 'http://thredds.met.no/thredds/dodsC/meps25files/' \
    'meps_det_pp_2_5km_latest.nc'
metno_ds = pymepps.open_model_dataset(metno_path, 'nc')


######################################################################
# The resulting dataset is a SpatialDataset. The dataset has several
# methods to load a xr.DataArray from the path. It also possible to print
# the content of the dataset. The content contains the dataset type, the
# number of file handlers within the dataset and all available data
# variables.
# 

print(metno_ds)


######################################################################
# The next step is to select/extract a variable from the Dataset. We will
# select the air temperature in 2 metre height and print the content of
# the resulting data
# 

metno_t2m = metno_ds.select('air_temperature_2m')
print(metno_t2m)
metno_t2m.isel(validtime=0).plot()
plt.show()


######################################################################
# We could see that the resulting data is a normal xarray.DataArray and
# all of the DataArray methods could be used. The coordinates of the
# DataArray are normalized. The DataArray is expanded with an accessor.
# Also the coordinates are normalized. We could access the accessor with
# metno\_t2m.pp. The main methods of the accessor are allowing a grid
# handling. So our next step is to explore the grid of the DataArray.
# 

print(metno_t2m.pp.grid)


######################################################################
# We could see that the grid is a grid with a defined projection. In our
# next step we will slice out an area around Hamburg. We will see that a
# new DataArray with a new grid is created.
# 

hh_bounds = [9, 54, 11, 53]
t2m_hh = metno_t2m.pp.sellonlatbox(hh_bounds)
print(t2m_hh.pp.grid)
print(t2m_hh)


######################################################################
# We sliced a longitude and latitude box around the given grid. So we
# sliced the data in a longitude and latitude projection. Our original
# grid was in another projection with unstructured lat lon coordinates. So
# it is not possible to create a structured grid based on this slice. So
# the grid becomes an unstructured grid. In the next step we will show the
# remapping capabilities of the pymepps grid structure.
# 


######################################################################
# If we slice the data we have seen that the structured grid could not
# maintained. So in the next step we will create a structured LonLatGrid
# from scratch. After the grid building we will remap the raw DataArray
# basen on the new grid.
# 
# The first step is to calculate the model resolution in degree.
# 

res = 2500   # model resolution in metre
earth_radius = 6371000 # Earth radius in metre
res_deg = np.round(res*360/(earth_radius*2*np.pi), 4)
# rounded model resolution equivalent in degree if it where on the equator
print(res_deg)


######################################################################
# Our next step is to build the grid. The grid implementation is inspired
# by the climate data operators. So to build the grid we will use the same
# format.
# 

grid_dict = dict(
    gridtype='lonlat',
    xsize=int((hh_bounds[2]-hh_bounds[0])/res_deg),
    ysize=int((hh_bounds[1]-hh_bounds[3])/res_deg),
    xfirst=hh_bounds[0],
    xinc=res_deg,
    yfirst=hh_bounds[3],
    yinc=res_deg,
)


######################################################################
# Now we use our grid dict together with the GridBuilder to build our
# grid.
# 

builder = pymepps.GridBuilder(grid_dict)
hh_grid = builder.build_grid()
print(hh_grid)


######################################################################
# Now we created the grid. The next step is a remapping of the raw
# DataArray to the new Grid. We will use th enearest neighbour approach to
# remap the data.
# 

t2m_hh_remapped = metno_t2m.pp.remapnn(hh_grid)

print(t2m_hh_remapped)


######################################################################
# To plot the data in a map, we have to slice the data. We will select the
# first validtime as plotting parameter.
# 

t2m_hh_remapped.isel(validtime=0).plot()
plt.show()


######################################################################
# In the map around Hamburg we could see the north and baltic sea in the
# top edges. But with the nearest enighbour approach we retain some of the
# sharp edges at the map. Our last step is a second remap plot, this time
# with a bilinear approach.
# 

metno_t2m.pp.remapbil(hh_grid).isel(validtime=0).plot()
plt.show()