from setuptools import setup, find_packages, Command
from pkg_resources import require, DistributionNotFound, VersionConflict
import sys
import os

# Extension classes and functions to add custom command
#======================================================


class check_dep(Command):
    """
    Command to check that the required dependencies are installed on the system
    """
    description = "Checks that the required dependencies are installed on the system"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):

        deps = ["matplotlib>=1.2.0","pyke","cartopy","Shapely","netcdf4",
                "numpy","scipy","nose","iris","epydoc"]
        for dep in deps:
            try:
                require(dep)
                print dep + " ...[ok]"
            except (DistributionNotFound, VersionConflict):
                print dep + "... MISSING!" 

class gen_doc(Command):
    """
    Command to generate the API reference with epydoc
    """
    description = "Generates the API reference with epydoc"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        raise NotImplementedError, "not implemented yet"       


# Metadata description
#=====================

setup(
    name='cis',
    version='0.1',
    description='Climate Inter-comparison Suite',
    author=' ',
    author_email=' ',
    url='http://proj.badc.rl.ac.uk/cedaservices/wiki/JASMIN/CommunityIntercomparisonSuite',

    packages=find_packages(),
    scripts = ['bin/cis'],
    
    cmdclass={"gendoc": gen_doc, "checkdep":check_dep}
)


