"""
How to use Xarray accessor
==========================

This example shows how to use the SpatialData accessor to extend the
capabilities of xarray.

"""


######################################################################
# To extend xarray.DataArray you need only to load also pymepps with
# "import pymepps". The extensions could be used with the property
# xarray.DataArray.pp
# 

import matplotlib.pyplot as plt
import xarray as xr
import pymepps


######################################################################
# To use the full power of pymepps, you have to set a grid. If you load
# the data with the xarray functions you have to set the grid afterwards.
# So the next step is to load a NetCDF model file with xarray. There are
# also pymepps functions to load model data. These are shown in another
# example.
# 

ds = xr.open_dataset('../data/model/GFS_Global_0p25deg_20161219_0600.nc')
t2m_max = ds['Maximum_temperature_height_above_ground_Mixed_intervals_Maximum']
print(t2m_max)


######################################################################
# The grid definition is inspired by the climate data operators. So you
# could either generate your own grid (done in this example), or you could
# load a cdo-conform grid file.
# 


######################################################################
# We could see that the grid is a structured latitude and longitude grid
# with a resolution of 0.25 degree.
# 

grid_dict = dict(
    gridtype='lonlat',
    xsize=t2m_max['lon'].size,
    ysize=t2m_max['lat'].size,
    xfirst=t2m_max['lon'].values[0],
    xinc=0.25,
    yfirst=t2m_max['lat'].values[0],
    yinc=-0.25,
)


######################################################################
# We created our grid dict with the information. Now we have to build the
# grid. In pymepps you could use the GridBuilder to build the grid with
# given grid\_dict.
# 

builder = pymepps.GridBuilder(grid_dict)
grid = builder.build_grid()
print(grid)


######################################################################
# The next step is to set the grid for our dataset. For this we could use
# the set\_grid method of the SpatialAccessor.
# 

t2m_max = t2m_max.pp.set_grid(grid)
print(t2m_max.pp.grid)


######################################################################
# Now we set the grid. It is also possible to normalize the coordinates to
# allow a consistent processing of the model data.
# 

# Before normalization
print('Before:\n{0:s}\n'.format(str(t2m_max)))

t2m_max = t2m_max.pp.normalize_coords()
# After normalization
print('After:\n{0:s}'.format(str(t2m_max)))


######################################################################
# We could see that the height\_above\_ground and the time variable are
# renamed to a more common name. The ensemble member is set to the default
# value 'det', while the runtime is set to the missing value None. Now
# lets plot the data with the xarray internal plot method.
# 

t2m_max.plot()
plt.show()


######################################################################
# Lets make use of the SpatialAccessor to slice an area over germany. We
# would also transform the temperature unit to degree celsius. For this we
# could use the normal xarray.DataArray mathematical operations. After the
# transformation lets plot the temperature.
# 

# sphinx_gallery_thumbnail_number = 2
ger_t2m_max = t2m_max.pp.sellonlatbox([5, 55, 15, 45])
# K to deg C
ger_t2m_max -= 273.15
ger_t2m_max.plot()
plt.show()


######################################################################
# If we use a xarray.DataArray method where the DataArray instance is
# copied, we have to set a new grid. This behaviour coud seen in the
# following code block.
# 

stacked_array = t2m_max.stack(stacked=('runtime', 'validtime'))
# we have to catch the error for sphinx documentation
try:
    print(stacked_array.pp.grid)
except TypeError:
    print('This DataArray has no grid defined!')


######################################################################
# This seen behavior arises from the fact that the grid is depending on
# the grid coordinates of the DataArray and they could be changed with a
# xarray.DataArray method.
# 