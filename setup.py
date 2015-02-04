import os
import os.path
from distutils.spawn import find_executable

from setuptools import setup, find_packages, Command
from pkg_resources import require, DistributionNotFound, VersionConflict

dependencies = ["matplotlib>=1.2.0", "pyke", "cartopy", "Shapely", "netcdf4>=1.0",
                "numpy", "scipy", "iris>=1.7.3", 'pyhdf']

test_dependencies = ["pyhamcrest", "mock", "nose"]


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

        for dep in dependencies:
            try:
                require(dep)
                print dep + " ...[ok]"
            except (DistributionNotFound, VersionConflict):
                print dep + "... MISSING!" 


class gen_doc(Command):
    """
    Command to generate the API reference using epydoc
    """
    description = "Generates the API reference using epydoc"
    user_options = []

    def initialize_options(self):
        require("epydoc")

    def finalize_options(self):
        pass

    def run(self):
        if not find_executable('epydoc'):
            print "Could not find epydoc on system"
            return  

        # create output directory if does not exists
        output_dir = "doc/api"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        from subprocess import call
        call(["epydoc", "--html", "--no-sourcecode", "-o", output_dir, "*"])

        import webbrowser
        webbrowser.open(os.path.join(output_dir, "index.html"))


# Extract long-description from README
here = os.path.dirname(__file__)
README = open(os.path.join(here, 'README')).read()

from jasmin_cis import __version__

setup(
    name='jasmin_cis',
    version=__version__,
    description='JASMIN Community Inter-comparison Suite',
    long_description=README,
    maintainer='Philip Kershaw',
    maintainer_email='Philip.Kershaw@stfc.ac.uk',
    url='http://proj.badc.rl.ac.uk/cedaservices/wiki/JASMIN/CommunityIntercomparisonSuite',
    classifiers=[
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'Topic :: Scientific/Engineering :: Visualization',
        'Environment :: Console',
        ],
    packages=find_packages(),
    package_data={'': ['logging.conf']},
    scripts=['bin/cis', 'bin/cis.lsf'],
    cmdclass={"gendoc": gen_doc,
              "checkdep": check_dep},
    install_requires=dependencies,
    tests_require=test_dependencies
)
