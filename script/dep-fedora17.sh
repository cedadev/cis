#!/bin/sh
# Script to install various libraries and tools for the CIS project

# Run as root, of course
if [[ $UID -ne 0 ]]; then
	echo "$0 must be run as root"
	exit 1
fi

# installing low-level libraries
yum -y install gcc gcc-c++ freetype-devel libpng-devel
yum -y install wget git
yum -y install python python-devel python-pip
yum -y install blast python-numpy python-scipy
pip-python install cython
yum -y install geos geos-devel
pip-python install shapely
pip-python install pyshp
yum -y install proj proj-devel
pip-python install pyke
pip-python install pil
pip-python install nose

# installing hdf and netcdf
yum -y install hdf5 hdf5-devel
yum -y install netcdf netcdf-devel
pip-python install netcdf4

# installing matplotlib
yum -y install gtk2 gtk2-devel tkinter PackageKit-gtk3-module
yum -y install qt qt4 qt-devel
yum -y install pygtk2 pygtk2-devel python-pyside
yum -y install tcl tk tk-devel tcl-devel
wget http://heanet.dl.sourceforge.net/project/matplotlib/matplotlib/matplotlib-1.2.0/matplotlib-1.2.0.tar.gz
tar -xvf matplotlib-1.2.0.tar.gz
cd matplotlib-1.2.0
python setup.py install
cd ..
rm -rf matplotlib-1.2.0*

# installing cartopy
git clone https://github.com/SciTools/cartopy.git
cd cartopy
sudo python setup.py install
cd ..
rm -rf cartopy

# installing basemap
wget http://heanet.dl.sourceforge.net/project/matplotlib/matplotlib-toolkits/basemap-1.0.5/basemap-1.0.5.tar.gz
tar -xvf basemap-1.0.5.tar.gz
cd basemap-1.0.5
python setup.py install
cd ..
rm -rf basemap-1.0.5*

# installing iris
git clone https://github.com/SciTools/iris.git
cd iris
sudo python setup.py install
cd ..
rm -rf iris

echo -e "\nInstallation successful!"
exit 0
