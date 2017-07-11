History
=======

Let's talk a little about the history and the formation process of this package.

There are so many python packages why a new one?
------------------------------------------------
Python is a rapidly developing programming language. In the last few years has
got more fans, especially in the geoscientific community. There are so many
different packages for different purposes, but no package matched my
requirements.

What are the requirements?
--------------------------
In my bachelor thesis I used a simple method for post-processing of numerical
weather model data. This method was based on a linear regression and is called
model output statistics in the meteorological community. The work for this
thesis needed a system for offline statistical processing of data. Later I
developed an operational weather forecast system based on the same
methods. The requirements of an online and operational weather forecast system
are very different to an offline system. So the requirements for this package
are offline and online processing of weather model data.

The biggest part of the online processing is outsourced to a companion project
called `pymepps-streaming <https://github.com/maestrotf/pymepps-streaming>`_.
But this package will be the base for offline and online processing of numerical
weather model data.