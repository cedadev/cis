
==============
Installing CIS
==============

A pre-packaged version of CIS is available for installation using conda for 64-bit Linux, Mac OSX and Windows.

Once conda is installed, you can easily install CIS with the following command::

    $ conda install -c cistools -c scitools cis


If you don't already have conda, you must first download and install it. Anaconda is a free conda package that includes Python and many common scientific and data analysis libraries, and is available `here <http://continuum.io/downloads>`_. Further documentation on using Anaconda and the features it provides can be found at http://docs.continuum.io/anaconda/index.html.

To check that CIS is installed correctly, simply type ``cis version`` to display the version number, for example::

    $ cis version
    Using CIS version: V1R2M0 (Stable)

In order to upgrade CIS to the latest version use::

    $ conda update cis

Dependencies
============

If you choose to install the dependencies yourself, use the following command to check the required dependencies are present::

    $ python setup.py checkdep

