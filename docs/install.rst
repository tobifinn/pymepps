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

In the future some requirements will be added, e.g.
`scikit-learn <http://scikit-learn.org>`_.

Installation
------------
At the moment this package is not available on pypi and conda. So you have to
clone this package and install it via pip.

It is recommended to install the requirements via a conda virtual environment,
but it is also possible to install them via pip.

Installation and activation via conda (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code:: sh

    git clone git@github.com:maestrotf/pymepps.git
    cd pymepps
    conda env create -f environment.yml
    source activate pymepps
    pip install .

Installation via pip
^^^^^^^^^^^^^^^^^^^^
.. code:: sh

    git clone git@github.com:maestrotf/pymepps.git
    cd pymepps
    pip install -r requirements.txt
    pip install .
