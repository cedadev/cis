#!/bin/sh
# Script to install various libraries and tools for the CIS project

# Run as root, of course
if [[ $UID -ne 0 ]]; then
	echo "$0 must be run as root"
	exit 1
fi

# to install from git source
apt-get install git

# to install usng pip
apt-get install python-pip

# installing low level dependencies
apt-get install python-dev python-pyke python-imaging
apt-get install libproj-dev
pip install cython
pip install pyshp

# installing nose
apt-get install python-nose

# installing numpy and scipy
pip install numpy
apt-get install python-scipy

# installing hdf and netcdf
apt-get install libhdf5-serial-1.8.4 libhdf5-serial-dev
apt-get install python-netcdf libnetcdf-dev
pip instal netcdf4

# installing shapely
pip install shapely

# installing geos
wget http://download.osgeo.org/geos/geos-3.3.7.tar.bz2
tar xvf geos-3.3.7.tar.bz2
cd geos-3.3.7
./configure
make
make install
cd ..
rm -rf geos*

# installing the matplotlib 1.2.0 with all its dependencies
apt-get build-dep matplotlib
wget https://github.com/downloads/matplotlib/matplotlib/matplotlib-1.2.0rc2.tar.gz
tar xzf matplotlib-1.2.0rc2.tar.gz
cd matplotlib-1.2.0rc2
python setup.py install
cd ..
rm -rf matplotlib*

# installing basemap
wget http://heanet.dl.sourceforge.net/project/matplotlib/matplotlib-toolkits/basemap-1.0.5/basemap-1.0.5.tar.gz
tar xvf basemap-1.0.5.tar.gz
cd basemap-1.0.5
python setup.py install
cd ..
rm -rf basemap-1.0.5*

# installing cartopy
git clone https://github.com/SciTools/cartopy.git
cd cartopy
python setup.py install
cd ..
rm -rf cartopy

# installing udunits
apt-get install libudunits2-0 libudunits2-dev

# installing iris
git clone https://github.com/SciTools/iris.git
cd iris
python setup.py install
cd ..
rm -rf iris

echo -e "\nInstallation complete."
exit 0
