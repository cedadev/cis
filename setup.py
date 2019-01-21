import os
import os.path

from setuptools import setup, find_packages, Command
from pkg_resources import require, DistributionNotFound, VersionConflict
from cis.test.runner import nose_test
from cis import __version__, __website__


root_path = os.path.dirname(__file__)

# If we're building docs on readthedocs we don't have any dependencies as they're all mocked out
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    dependencies = []
    optional_dependencies = {}
    test_dependencies = []

else:
    dependencies = ["matplotlib>=2.0",
                    "netcdf4>=1.0",
                    "numpy",
                    "scipy>=0.15.0",
                    "scitools-iris>=1.8.0",
                    "psutil>=2.0.0",
                    "six"]

    optional_dependencies = {"HDF": ["pyhdf>=0.9.0"], "Pandas": ["pandas"]}

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
                print(dep + " ...[ok]")
            except (DistributionNotFound, VersionConflict):
                print(dep + "... MISSING!")

# Extract long-description from README
README = open(os.path.join(root_path, 'README.md'), 'rb').read().decode('utf-8')

setup(
    name='cis',
    version=__version__,
    description='Community Intercomparison Suite',
    long_description=README,
    maintainer='Philip Kershaw',
    maintainer_email='Philip.Kershaw@stfc.ac.uk',
    url=__website__,
    classifiers=[
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'Topic :: Scientific/Engineering :: Visualization',
        'Environment :: Console',
        ],
    packages=find_packages(),
    package_data={'': ['logging.conf', 'plotting/raster/*.png']},
    scripts=['bin/cis', 'bin/cis.lsf'],
    cmdclass={"checkdep": check_dep,
              "test": nose_test},
    install_requires=dependencies,
    extras_require=optional_dependencies,
    tests_require=test_dependencies
)
