"""
Module to do integration tests of version. Does not check the version is correct just that the command runs
created without errors.
"""
from unittest import TestCase

from jasmin_cis.cis import parse_and_run_arguments


class TestVersionIntegration(TestCase):

    def test_should_do_scatter_plot_of_file_valid_aerosol_cci_file(self):

        arguments = ['version']
        parse_and_run_arguments(arguments)
