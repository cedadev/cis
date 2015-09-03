
==============
Installing CIS
==============

A pre-packaged version of CIS is available for installation using conda for 64-bit Linux, Mac OSX and Windows.

Once conda is installed, you can easily install CIS with the following command::

    $ conda install -c cistools -c scitools cis


If you don't already have conda, you must first download and install it. Anaconda is a free conda package that includes Python and many common scientific and data analysis libraries, and is available `here <http://continuum.io/downloads>`_. Further documentation on using Anaconda and the features it provides can be found at http://docs.continuum.io/anaconda/index.html.

To check that CIS is installed correctly, simply type ``cis version`` to display the version number, for example::

    $ cis version
    Using CIS version: V1R1M0 (Stable)

Dependencies
============

Use the following command to check the dependencies that CIS requries to run::

    $ python setup.py checkdep

