pymepps
=======


.. list-table::
    :stub-columns: 1
    :widths: 15 85

    * - docs
      - |docs|
    * - reqs
      - |reqs|

.. |docs| image:: https://readthedocs.org/projects/pymepps/badge/?version=latest
                :target: http://pymepps.readthedocs.io/en/latest/?badge=latest
                :alt: Documentation Status

.. |reqs| image:: https://requires.io/github/maestrotf/pymepps/requirements.svg?branch=master
                :target: https://requires.io/github/maestrotf/pymepps/requirements/?branch=master
                :alt: Requirements Status

python meteorological post-processing system
--------------------------------------------

pymepps is a python package for processing of meteorological data, especially
for post-processing of numerical weather model data.

With this package it should be possible to load, process, save and plot the
data. The central entity of this package is the data itself. The package is
based on the climate data operators (cdo, [1]_). While cdo is used to process
meteorological files this package could be used to process extracted file data.

Under the hood this package is based on pandas [2]_ for processing of time
series data and xarray [3]_ for processing spatial data.


Installation
------------
We highly recommend to create a virtual environment for this package to prevent
package collisions.
At the moment this package is not uploaded via pypi or conda. So the package is
cloned and installed via pip.

Install the package and dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

via conda and virtual environment (recommended):

.. code:: sh

    conda env create -f environment.yml

via pip:

.. code:: sh

    pip install -r requirements.txt

Documentation
-------------
For further documentation, especially documentation for the api please take a
look at `docs <http://pymepps.readthedocs.io/en/latest>`_.


Authors
-------
* **Tobias Finn** - *Initial creator* - `maestrotf <https://github.com/maestrotf>`_

License
-------

This project is licensed under the GPL3 License - see the
`license <LICENSE.md>`_ file for details.


References
----------
.. [1] Climate data operators, https://code.zmaw.de/projects/cdo/
.. [2] pandas, http://pandas.pydata.org/
.. [3] xarray, http://xarray.pydata.org/
