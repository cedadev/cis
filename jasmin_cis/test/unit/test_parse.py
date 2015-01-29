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
        assert_that(dg[0]['variables'], contains_inanyorder('rain', 'snow'))

    def test_GIVEN_colocate_command_WHEN_multiple_variables_in_datagroup_THEN_variables_unpacked(self):
        var1, var2 = 'rain', 'snow'
        output = 'aggregate-out'
        samplegroup = valid_1d_filename + ':colocator=bin'
        product = 'cis'
        args = ["col", var1 + "," + var2 + ':' + valid_1d_filename + ':product=' + product, samplegroup, '-o', output]
        main_args = parse_args(args)
        dg = main_args.datagroups
        assert_that(len(dg), is_(1))
        assert_that(dg[0]['filenames'], is_([valid_1d_filename]))
        assert_that(dg[0]['product'], is_('cis'))
        assert_that(dg[0]['variables'], contains_inanyorder('rain', 'snow'))

    def test_GIVEN_aggregate_command_WHEN_multiple_variables_in_datagroup_THEN_variables_unpacked(self):
        var1, var2 = 'rain', 'snow'
        grid = 'x=[-10,10,2]'
        output = 'aggregate-out'
        product = 'cis'
        args = ["aggregate", var1 + "," + var2 + ':' + valid_1d_filename + ':product=' + product, grid, '-o', output]
        main_args = parse_args(args)
        dg = main_args.datagroups
        assert_that(len(dg), is_(1))
        assert_that(dg[0]['filenames'], is_([valid_1d_filename]))
        assert_that(dg[0]['product'], is_('cis'))
        assert_that(dg[0]['variables'], contains_inanyorder('rain', 'snow'))

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

    def test_GIVEN_output_missing_file_extension_WHEN_parse_THEN_extension_added(self):
        args = ['eval', 'var1,var2:%s:product=cis' % ascii_filename_with_no_values,
                'var1 + var2 + var3', '-o', 'output_name']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('output_name.nc'))

    def test_GIVEN_output_has_file_extension_WHEN_parse_THEN_extension_not_added(self):
        args = ['eval', 'var1,var2:%s:product=cis' % ascii_filename_with_no_values,
                'var1 + var2 + var3', '-o', 'output_name.nc']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('output_name.nc'))

    def test_parse_evaluate_single_datagroup(self):
        args = ['eval', 'var1,var2:%s:product=cis' % ascii_filename_with_no_values,
                'var1 + var2 + var3', '-o', 'output.nc']
        parsed = parse_args(args)
        assert_that(parsed.command, is_('eval'))
        assert_that(parsed.expr, is_('var1 + var2 + var3'))
        assert_that(parsed.output, is_('output.nc'))
        assert_that(len(parsed.datagroups), is_(1))
        assert_that(parsed.datagroups[0]['filenames'], is_([ascii_filename_with_no_values]))
        assert_that(parsed.datagroups[0]['variables'], is_(['var1', 'var2']))
        assert_that(parsed.datagroups[0]['product'], is_('cis'))

    def test_parse_evaluate_multiple_datagroups(self):
        args = ['eval', 'var1,var2:%s' % ascii_filename_with_no_values,
                'var3:%s' % dummy_cis_out, 'var1^var2 / var3', '-o', 'output.nc']
        parsed = parse_args(args)
        assert_that(parsed.command, is_('eval'))
        assert_that(parsed.expr, is_('var1^var2 / var3'))
        assert_that(parsed.output, is_('output.nc'))
        assert_that(len(parsed.datagroups), is_(2))
        assert_that(parsed.datagroups[0]['filenames'], is_([ascii_filename_with_no_values]))
        assert_that(parsed.datagroups[0]['variables'], is_(['var1', 'var2']))
        assert_that(parsed.datagroups[1]['filenames'], is_([dummy_cis_out]))
        assert_that(parsed.datagroups[1]['variables'], is_(['var3']))

    def test_parse_evaluate_output_variable(self):
        args = ['eval', 'var1,var2:%s' % ascii_filename_with_no_values,
                'var3:%s' % dummy_cis_out, 'var1^var2 / var3', '-o', 'out_var:output.nc']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('output.nc'))
        assert_that(parsed.output_var, is_('out_var'))

    def test_parse_evaluate_no_output_variable(self):
        args = ['eval', 'var1,var2:%s' % ascii_filename_with_no_values,
                'var3:%s' % dummy_cis_out, 'var1^var2 / var3', '-o', 'output.nc']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('output.nc'))
        assert_that(parsed.output_var, is_(None))

    def test_parse_evaluate_no_output(self):
        args = ['eval', 'var1,var2:%s' % ascii_filename_with_no_values,
                'var3:%s' % dummy_cis_out, 'var1^var2 / var3']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('out.nc'))
        assert_that(parsed.output_var, is_(None))

    def test_parse_evaluate_invalid_output(self):
        args = ['eval', 'var1,var2:%s' % ascii_filename_with_no_values,
                'var3:%s' % dummy_cis_out, 'var1^var2 / var3', '-o', 'var:var:out']
        try:
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_parse_evaluate_valid_aliases(self):
        # Should use the given alias or the variable name if not provided
        args = ['eval', 'var1=alias1,var2:%s' % ascii_filename_with_no_values,
                'var3=alias3:%s' % dummy_cis_out, 'var1^var2 / var3', '-o', 'output.nc']
        parsed = parse_args(args)
        assert_that(parsed.datagroups[0]['variables'], is_(['var1', 'var2']))
        assert_that(parsed.datagroups[0]['aliases'], is_(['alias1', 'var2']))
        assert_that(parsed.datagroups[1]['variables'], is_(['var3']))
        assert_that(parsed.datagroups[1]['aliases'], is_(['alias3']))

    def test_parse_evaluate_duplicate_aliases(self):
        args = ['eval', 'var1=alias1,var2=alias1:%s' % ascii_filename_with_no_values,
                'var1^var2 / var3', '-o', 'output.nc']
        try:
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_parse_evaluate_invalid_aliases(self):
        invalid_var_aliases = ['var1=', '=alias', '=', 'var=a=a']
        for var in invalid_var_aliases:
            args = ['eval', '%s:%s' % (var, ascii_filename_with_no_values),
                    'var1^var2 / var3', '-o', 'output.nc']
            try:
                parse_args(args)
                assert False
            except SystemExit as e:
                if e.code != 2:
                    raise e

    def test_GIVEN_no_output_WHEN_parse_stats_THEN_output_is_None(self):
        args = ['stats', 'var1,var2:%s' % ascii_filename_with_no_values]
        arguments = parse_args(args)
        assert_that(arguments.output, is_(None))

    def test_GIVEN_one_variable_WHEN_parse_stats_THEN_parser_error(self):
        args = ['stats', 'var1:%s' % ascii_filename_with_no_values]
        try:
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_GIVEN_more_than_two_variables_WHEN_parse_stats_THEN_parser_error(self):
        args = ['stats', 'var1,var2:%s' % ascii_filename_with_no_values,
                'var3:%s' % ascii_filename_with_no_values]
        try:
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_GIVEN_two_variables_WHEN_parse_stats_THEN_variables_are_in_datagroups(self):
        args = ['stats', 'var1:%s' % ascii_filename_with_no_values, 'var2:%s' % dummy_cis_out]
        arguments = parse_args(args)
        assert_that(arguments.datagroups[0]['filenames'], is_([ascii_filename_with_no_values]))
        assert_that(arguments.datagroups[0]['variables'], is_(['var1']))
        assert_that(arguments.datagroups[1]['filenames'], is_([dummy_cis_out]))
        assert_that(arguments.datagroups[1]['variables'], is_(['var2']))

    def test_GIVEN_output_file_WHEN_parse_stats_THEN_output_file_in_arguments(self):
        args = ['stats', 'var1,var2:%s' % ascii_filename_with_no_values, '-o', 'output']
        arguments = parse_args(args)
        assert_that(arguments.output, is_('output.nc'))