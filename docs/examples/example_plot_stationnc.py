"""
Load station data based on NetCDF files
=======================================

In this example we show how to load station data based on NetCDF files.
The data is loaded with the pymepps package. Thanks to Ingo Lange we
could use original data from the Wettermast for this example. In the
following the data is loaded, plotted and saved as json file.

"""

import pymepps
import matplotlib.pyplot as plt


######################################################################
# We could use the global pymepps open\_station\_dataset function to open
# the Wettermast data. We have to specify the data path and the data type.
# 

wm_ds = pymepps.open_station_dataset('../data/station/wettermast.nc', 'nc')

print(wm_ds)


######################################################################
# Now we could extract the temperature in 2 m height. For this we use the
# select method of the resulted dataset.
# 

t2m = wm_ds.select('TT002_M10')

print(type(t2m))
print(t2m.describe())


######################################################################
# We could see that the resulting temperature is a normal pandas.Series.
# So it is possible to use all pandas methods, e.g. plotting of the
# Series.
# 

t2m.plot()
plt.xlabel('Date')
plt.ylabel('Temperature in °C')
plt.title('Temperature at the Wettermast Hamburg')
plt.show()


######################################################################
# Pymepps uses an accessor to extend the pandas functionality. The
# accessor could be accessed with Series.pp. At the moment there is only a
# lonlat attribute, update, save and load method defined, but it is
# planned to expand the number of additional methods.
# 

print(t2m.pp.lonlat)


######################################################################
# We could see that the logitude and latitude are None at the moment,
# because we haven't set the yet. We could either set them directly or set
# the coordintes in the open\_station\_dataset function with the lonlat
# argument.
# 