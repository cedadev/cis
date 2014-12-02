"""
Module to test the parser
The parse raises a SystemExit exception with code 2 if it fails to parse.
Each test therefore ignores SystemExit exceptions with code 2 as they are expected.
"""
import argparse
from unittest import TestCase

from hamcrest import is_, assert_that, contains_inanyorder
from nose.tools import eq_

from jasmin_cis.parse import parse_args, expand_file_list
from jasmin_cis.test.test_files.data import *
from jasmin_cis.plotting.plot import Plotter


class TestParse(TestCase):
    def test_order_is_preserved_when_specifying_individual_files(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(valid_1d_filename + "," + valid_2d_filename, parser)
        eq_(files, [valid_1d_filename, valid_2d_filename])
        files = expand_file_list(valid_2d_filename + "," + valid_1d_filename, parser)
        eq_(files, [valid_2d_filename, valid_1d_filename])

    def test_directories_are_sorted(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(test_directory, parser)
        eq_(files, test_directory_files)

    def test_wildcarded_files_are_sorted(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(os.path.join(test_directory,
                                              'test_file_for_parser_*'), parser)
        eq_(files, test_directory_files)

    def test_order_is_preserved_when_specifying_files_even_when_wildcards_and_directories_are_specified_too(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(valid_1d_filename + "," + valid_2d_filename + "," +
                                 os.path.join(test_directory, 'test_file_for_parser_1') +
                                 "," + valid_cloud_cci_filename + "," + test_directory, parser)
        eq_(files, [valid_1d_filename, valid_2d_filename, test_directory_file1,
                    valid_cloud_cci_filename, test_directory_file2, test_directory_file3])

    def test_can_specify_one_valid_filename_and_a_directory(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(valid_1d_filename + ',' + test_directory, parser)
        eq_(files, [valid_1d_filename] + test_directory_files)

    def test_can_specify_a_directory(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(test_directory, parser)
        eq_(files, test_directory_files)

    def test_can_specify_a_file_with_wildcards(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(os.path.join(test_directory, 'test_file_for_parser_*'), parser)
        eq_(files, test_directory_files)
        files = expand_file_list(os.path.join(test_directory, '*_1'), parser)
        eq_(files, [test_directory_file1])
        files = expand_file_list(os.path.join(test_directory, 'test_file_for_parser_?'), parser)
        eq_(files, test_directory_files)
        files = expand_file_list(os.path.join(test_directory, 'test_file_for_parser_[0-9]'), parser)
        eq_(files, test_directory_files)

    def test_can_specify_one_valid_filename_and_a_wildcarded_file(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(valid_1d_filename + ',' + os.path.join(test_directory, 'test_file_for_parser_[0-9]'),
                                 parser)
        eq_(files, [valid_1d_filename] + test_directory_files)

    def test_duplicate_files_are_not_returned_from_expand_file_list(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(
            os.path.join(test_directory, 'test_file_for_parser_1') + ',' + os.path.join(test_directory,
                                                                                        'test_file_for_parser_[0-9]'),
            parser)
        eq_(files, test_directory_files)

    def test_can_specify_one_valid_filename(self):
        args = ["plot", valid_variable_in_valid_filename + ":" + valid_1d_filename]
        parse_args(args)

    def test_should_raise_error_with_one_invalid_filename(self):
        try:
            args = ["plot", valid_variable_in_valid_filename + ":" + invalid_filename]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_can_specify_more_than_one_valid_filename(self):
        args = ["plot", valid_variable_in_valid_filename + ":" + valid_1d_filename
                + ',' + netcdf_file_with_incorrect_file_extension]
        parse_args(args)

    def test_should_raise_error_with_a_mixture_of_valid_and_invalid_filenames(self):
        try:
            args = ["plot", valid_variable_in_valid_filename + ":" + valid_1d_filename + ',' + invalid_filename]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_can_specify_valid_chart_type(self):
        args = ["plot", valid_variable_in_valid_filename + ":" + valid_1d_filename, "--type",
                Plotter.plot_types.keys()[0]]
        parse_args(args)

    def test_should_raise_error_with_an_invalid_chart_type(self):
        try:
            args = ["plot", valid_variable_in_valid_filename + ":" + valid_1d_filename, "--type", "dfgdfgdfgdfgdfgdf"]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_should_raise_error_with_more_than_one_chart_type(self):
        try:
            args = ["plot", valid_variable_in_valid_filename + ":" + valid_1d_filename, "--type",
                    Plotter.plot_types.keys()[0], Plotter.plot_types.keys()[1]]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_can_specify_more_than_one_variable(self):
        args = ["plot", valid_variable_in_valid_filename + ":" + valid_1d_filename,
                valid_variable_in_valid_filename + ":" + valid_1d_filename]
        parse_args(args)

    def test_GIVEN_subset_command_WHEN_multiple_variables_in_datagroup_THEN_variables_unpacked(self):
        var1, var2 = 'rain', 'snow'
        limits = 'x=[-10,10],y=[40,60]'
        output = 'subset-out'
        product = 'cis'
        args = ["subset", var1 + "," + var2 + ':' + valid_1d_filename + ':product=' + product, limits, '-o', output]
        main_args = parse_args(args)
        dg = main_args.datagroups
        assert_that(len(dg), is_(1))
        assert_that(dg[0]['filenames'], is_([valid_1d_filename]))
        assert_that(dg[0]['product'], is_('cis'))
        assert_that(dg[0]['variable'], contains_inanyorder('rain', 'snow'))

    def test_GIVEN_command_not_subset_WHEN_multiple_variables_in_datagroup_THEN_variables_not_unpacked(self):
        var1, var2 = 'rain', 'snow'
        product = 'cis'
        args = ["plot", var1 + "," + var2 + ':' + valid_1d_filename + ':product=' + product]
        main_args = parse_args(args)
        dg = main_args.datagroups
        assert_that(len(dg), is_(1))
        assert_that(dg[0]['filenames'], is_([valid_1d_filename]))
        assert_that(dg[0]['product'], is_('cis'))
        assert_that(dg[0]['variable'], is_('rain,snow'))

    def test_should_raise_error_when_no_variable_is_specified(self):
        try:
            args = ["plot", valid_1d_filename]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_should_raise_error_with_invalid_line_width(self):
        try:
            args = ["plot", valid_variable_in_valid_filename + ":" + valid_1d_filename, "--itemwidth", "4a0"]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_should_raise_error_with_invalid_line_style(self):
        try:
            args = ["plot", valid_variable_in_valid_filename + ":" + valid_1d_filename, "--linestyle", "4a0"]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_GIVEN_input_contains_output_WHEN_parse_THEN_raises_error(self):
        args_list = [["subset", "var:" + dummy_cis_out, "x=[-180,180]", "-o", dummy_cis_out[:-3]],
                     ["col", "var1,var2:" + dummy_cis_out, valid_aerosol_cci_filename + ':colocator=bin',
                      "-o", dummy_cis_out[:-3]],
                     ["col", "var1,var2:" + valid_aerosol_cci_filename, dummy_cis_out + ':colocator=bin',
                      "-o", dummy_cis_out[:-3]],
                     ["aggregate", "var:" + dummy_cis_out, "t", "-o", dummy_cis_out[:-3]]]
        for args in args_list:
            try:
                parse_args(args)
                assert False
            except SystemExit as e:
                if e.code != 2:
                    raise e