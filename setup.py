from setuptools import setup, find_packages

setup(
    name='cis',
    version='0.1',
    description='Climate Inter-comparison Suite',
    author='David Michel',
    author_email='david.michel@tessella.com',
    url='www.tessella.com',

    packages=find_packages(),

    install_requires=[
        "scipy",
        "numpy",
        "netCDF4",
        "cartopy",
        "Shapely",
        "basemap",
        "pyke",
        "matplotlib==1.2.0",
        "iris>=1.1.0"
    ],

    tests_require=["nose>=1.1.2"],

    dependency_links=["https://github.com/SciTools/iris/tarball/master#egg=iris-1.1.0"]
)

