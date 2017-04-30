pymepps
=======


.. list-table::
    :stub-columns: 1
    :widths: 15 85

    * - docs
      - |docs|

.. |docs| image:: https://readthedocs.org/projects/pymepps/badge/?version=latest
                :target: http://pymepps.readthedocs.io/en/latest/?badge=latest
                :alt: Documentation Status

*p*ython *me*teorological *p*ost-*p*processing *s*ystem
-------------------------------------------------------

pymepps is a python package for processing of meteorological data, especially
for post-processing of numerical weather model data.

With this package it should be possible to load, process, save and plot the
data. The central entity of this package is the data itself. The package is
based on the climate data operators (cdo, [1]_). While cdo is used to process
meteorological files this package could be used to process extracted file data.

Under the hood this package is based on pandas [2]_ for processing of time
series data and xarray [3]_ for processing spatial data.



References
----------
[1]_ Climate data operators, https://code.zmaw.de/projects/cdo/
[2]_ pandas, http://pandas.pydata.org/
[3]_ xarray, http://xarray.pydata.org
