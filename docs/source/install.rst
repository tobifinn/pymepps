Installation
============

This package is a python package. Further this package is based on different
python tools. So there are some dependencies which should be matched. To install
this package you should read the installation section.

Requirements
------------
This package is programmed with python 3.5. It is not planned to support python
2.7. In the future this package will be back checked with travis ci for version
3.4 – 3.6. But at the moment we couldn't guarantee the compatibility of other
versions than 3.5.

* `python <https://www.python.org/>`_
* `numpy <http://www.numpy.org/>`_
* `scipy <https://www.scipy.org/>`_
* `pandas <http://pandas.pydata.org/>`_
* `xarray <http://xarray.pydata.org/>`_
* `netcdf4 <http://unidata.github.io/netcdf4-python/>`_
* `pygrib <https://github.com/jswhit/pygrib>`_
* `matplotlib <https://matplotlib.org/>`_
* `basemap <https://matplotlib.org/basemap/users/intro.html>`_

The following packages are only recommended to use all features.
* `cdo <https://code.zmaw.de/projects/cdo/>`_
* `cdo bindings <https://github.com/Try2Code/cdo-bindings>`_

In the future some requirements will be added for example
`scikit-learn <http://scikit-learn.org>`_.

Installation
------------
At the moment this package is not available on pypi and conda. So you have to
install this package via github. For an easier install you need only to download
the environment.yml or the requirements.txt.

The recommended way to install this package is to create a new conda environment
based on environment.yml. But it is also possible to install this package via
the requirements.txt with pip. Both ways includes this package.

Installation and activation via conda (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code:: sh

    conda env create -f environment.yml
    source activate pymepps

Installation via pip
^^^^^^^^^^^^^^^^^^^^
.. code:: sh

    pip install -r requirements.txt
