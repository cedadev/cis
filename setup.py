import os
import os.path
from distutils.spawn import find_executable

from setuptools import setup, find_packages, Command
from pkg_resources import require, DistributionNotFound, VersionConflict
from cis.test.runner import nose_test

root_path = os.path.dirname(__file__)

dependencies = ["matplotlib>=1.2.0",
                "netcdf4>=1.0",
                "numpy",
                "scipy",
                "iris>=1.7.3",
                'psutil>=2.0.0',
                'basemap>=1.0.7']

optional_dependencies = {"HDF": ["pyhdf"]}

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
README = open(os.path.join(root_path, 'README')).read()

from cis import __version__, __website__

setup(
    name='cis',
    version=__version__,
    description='Community Inter-comparison Suite',
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
    package_data={'': ['logging.conf']},
    scripts=['bin/cis', 'bin/cis.lsf'],
    cmdclass={"gendoc": gen_doc,
              "checkdep": check_dep,
              "test": nose_test},
    install_requires=dependencies,
    extras_require=optional_dependencies,
    tests_require=test_dependencies
)
