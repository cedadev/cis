"""
Module to test the parser
The parse raises a SystemExit exception with code 2 if it fails to parse.
Each test therefore ignores SystemExit exceptions with code 2 as they are expected.
"""
import argparse
from unittest import TestCase
import os

from hamcrest import is_, assert_that, contains_inanyorder
from nose.tools import eq_

from cis.parse import parse_args, expand_file_list
from cis.test.test_files.unittest_data import test_directory_files, test_directory, invalid_filename, \
    multiple_valid_files, single_valid_file, data_directory, dummy_cis_out

from cis.plotting.plot import Plotter


class TestParse(TestCase):
    """
    Generic parser tests not specific to one particular command
    """

    def test_order_is_preserved_when_specifying_individual_files(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(test_directory_files[0] + "," + test_directory_files[1], parser)
        eq_(files, [test_directory_files[0], test_directory_files[1]])
        files = expand_file_list(test_directory_files[1] + "," + test_directory_files[0], parser)
        eq_(files, [test_directory_files[1], test_directory_files[0]])

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
        files = expand_file_list(','.join([single_valid_file, os.path.join(data_directory, 'data_file*'),
                                           test_directory]), parser)
        eq_(files, [single_valid_file] + multiple_valid_files + test_directory_files)

    def test_can_specify_one_valid_filename_and_a_directory(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(single_valid_file + ',' + test_directory, parser)
        eq_(files, [single_valid_file] + test_directory_files)

    def test_can_specify_a_directory(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(test_directory, parser)
        eq_(files, test_directory_files)

    def test_can_specify_a_file_with_wildcards(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(os.path.join(test_directory, 'test_file_for_parser_*'), parser)
        eq_(files, test_directory_files)
        files = expand_file_list(os.path.join(test_directory, '*_1'), parser)
        eq_(files, [test_directory_files[0]])
        files = expand_file_list(os.path.join(test_directory, 'test_file_for_parser_?'), parser)
        eq_(files, test_directory_files)
        files = expand_file_list(os.path.join(test_directory, 'test_file_for_parser_[0-9]'), parser)
        eq_(files, test_directory_files)

    def test_can_specify_one_valid_filename_and_a_wildcarded_file(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(single_valid_file + ',' + os.path.join(test_directory, 'test_file_for_parser_[0-9]'),
                                 parser)
        eq_(files, [single_valid_file] + test_directory_files)

    def test_duplicate_files_are_not_returned_from_expand_file_list(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(
            os.path.join(test_directory, 'test_file_for_parser_1') + ',' + os.path.join(test_directory,
                                                                                        'test_file_for_parser_[0-9]'),
            parser)
        eq_(files, test_directory_files)

    def test_can_specify_one_valid_filename(self):
        args = ["plot", "var:" + test_directory_files[0]]
        parse_args(args)

    def test_should_raise_error_with_one_invalid_filename(self):
        try:
            args = ["plot", "var:" + invalid_filename]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_can_specify_more_than_one_valid_filename(self):
        args = ["plot", "var:" + ','.join(test_directory_files[0:1])]
        parse_args(args)

    def test_should_raise_error_with_a_mixture_of_valid_and_invalid_filenames(self):
        try:
            args = ["plot", "var:" + test_directory_files[0] + ',' + invalid_filename]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_GIVEN_input_contains_output_WHEN_parse_THEN_raises_error(self):
        args_list = [["subset", "var:" + dummy_cis_out, "x=[-180,180]", "-o", dummy_cis_out[:-3]],
                     ["col", "var1,var2:" + dummy_cis_out, single_valid_file + ':colocator=bin',
                      "-o", dummy_cis_out[:-3]],
                     ["col", "var1,var2:" + single_valid_file, dummy_cis_out + ':colocator=bin',
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
        args = ['eval', 'var1,var2:%s:product=cis' % single_valid_file,
                'var1 + var2 + var3', 'units', '-o', 'output_name']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('output_name.nc'))

    def test_GIVEN_output_has_file_extension_WHEN_parse_THEN_extension_not_added(self):
        args = ['eval', 'var1,var2:%s:product=cis' % single_valid_file,
                'var1 + var2 + var3', 'units', '-o', 'output_name.nc']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('output_name.nc'))


class TestParsePlot(TestCase):
    """
    Tests specific to the plot command
    """

    def test_can_specify_valid_chart_type(self):
        args = ["plot", "var:" + test_directory_files[0], "--type",
                Plotter.plot_types.keys()[0]]
        parse_args(args)

    def test_should_raise_error_with_an_invalid_chart_type(self):
        try:
            args = ["plot", "var:" + test_directory_files[0], "--type", "dfgdfgdfgdfgdfgdf"]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_should_raise_error_with_more_than_one_chart_type(self):
        try:
            args = ["plot", "var:" + test_directory_files[0], "--type",
                    Plotter.plot_types.keys()[0], Plotter.plot_types.keys()[1]]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_can_specify_more_than_one_variable(self):
        args = ["plot", "var:" + test_directory_files[0], "var:" + test_directory_files[0]]
        parse_args(args)

    def test_should_raise_error_when_no_variable_is_specified(self):
        try:
            args = ["plot", test_directory_files[0]]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_should_raise_error_with_invalid_line_width(self):
        try:
            args = ["plot", "var:" + test_directory_files[0], "--itemwidth", "4a0"]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_should_raise_error_with_invalid_line_style(self):
        try:
            args = ["plot", "var:" + test_directory_files[0], "--linestyle", "4a0"]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e


class TestParseEvaluate(TestCase):
    """
    Tests specific to the evaluate command
    """

    def test_parse_evaluate_single_datagroup(self):
        args = ['eval', 'var1,var2:%s:product=cis' % single_valid_file,
                'var1 + var2 + var3', 'units', '-o', 'output.nc']
        parsed = parse_args(args)
        assert_that(parsed.command, is_('eval'))
        assert_that(parsed.expr, is_('var1 + var2 + var3'))
        assert_that(parsed.units, is_('units'))
        assert_that(parsed.output, is_('output.nc'))
        assert_that(len(parsed.datagroups), is_(1))
        assert_that(parsed.datagroups[0]['filenames'], is_([single_valid_file]))
        assert_that(parsed.datagroups[0]['variables'], is_(['var1', 'var2']))
        assert_that(parsed.datagroups[0]['product'], is_('cis'))

    def test_parse_evaluate_multiple_datagroups(self):
        args = ['eval', 'var1,var2:%s' % single_valid_file,
                'var3:%s' % dummy_cis_out, 'var1^var2 / var3', 'units', '-o', 'output.nc']
        parsed = parse_args(args)
        assert_that(parsed.command, is_('eval'))
        assert_that(parsed.expr, is_('var1^var2 / var3'))
        assert_that(parsed.units, is_('units'))
        assert_that(parsed.output, is_('output.nc'))
        assert_that(len(parsed.datagroups), is_(2))
        assert_that(parsed.datagroups[0]['filenames'], is_([single_valid_file]))
        assert_that(parsed.datagroups[0]['variables'], is_(['var1', 'var2']))
        assert_that(parsed.datagroups[1]['filenames'], is_([dummy_cis_out]))
        assert_that(parsed.datagroups[1]['variables'], is_(['var3']))

    def test_parse_evaluate_output_variable(self):
        args = ['eval', 'var1,var2:%s' % single_valid_file,
                'var3:%s' % dummy_cis_out, 'var1^var2 / var3', 'units', '-o', 'out_var:output.nc']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('output.nc'))
        assert_that(parsed.output_var, is_('out_var'))

    def test_parse_evaluate_no_output_variable(self):
        args = ['eval', 'var1,var2:%s' % single_valid_file,
                'var3:%s' % dummy_cis_out, 'var1^var2 / var3', 'units', '-o', 'output.nc']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('output.nc'))
        assert_that(parsed.output_var, is_(None))

    def test_parse_evaluate_no_output(self):
        args = ['eval', 'var1,var2:%s' % single_valid_file,
                'var3:%s' % single_valid_file, 'var1^var2 / var3', 'units']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('out.nc'))
        assert_that(parsed.output_var, is_(None))

    def test_parse_evaluate_invalid_output(self):
        args = ['eval', 'var1,var2:%s' % single_valid_file,
                'var3:%s' % dummy_cis_out, 'var1^var2 / var3', 'units', '-o', 'var:var:out']
        try:
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_parse_evaluate_valid_aliases(self):
        # Should use the given alias or the variable name if not provided
        args = ['eval', 'var1=alias1,var2:%s' % single_valid_file,
                'var3=alias3:%s' % dummy_cis_out, 'var1^var2 / var3', 'units', '-o', 'output.nc']
        parsed = parse_args(args)
        assert_that(parsed.datagroups[0]['variables'], is_(['var1', 'var2']))
        assert_that(parsed.datagroups[0]['aliases'], is_(['alias1', 'var2']))
        assert_that(parsed.datagroups[1]['variables'], is_(['var3']))
        assert_that(parsed.datagroups[1]['aliases'], is_(['alias3']))

    def test_parse_evaluate_duplicate_aliases(self):
        args = ['eval', 'var1=alias1,var2=alias1:%s' % single_valid_file,
                'var1^var2 / var3', 'units', '-o', 'output.nc']
        try:
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_parse_evaluate_invalid_aliases(self):
        invalid_var_aliases = ['var1=', '=alias', '=', 'var=a=a']
        for var in invalid_var_aliases:
            args = ['eval', '%s:%s' % (var, single_valid_file),
                    'var1^var2 / var3', 'units', '-o', 'output.nc']
            try:
                parse_args(args)
                assert False
            except SystemExit as e:
                if e.code != 2:
                    raise e

    def test_parse_evaluate_missing_units_single_datagroup(self):
        args = ['eval', 'var1,var2:%s' % single_valid_file,
                'var1 + var2']
        try:
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_can_specify_attributes(self):
        args = ['eval', 'var1,var2:%s' % single_valid_file, 'var1^var2 / var3', 'units',
                '--attributes', 'att1=val1,att2=val2']
        parsed = parse_args(args)
        assert_that(parsed.attributes, is_({'att1': 'val1',
                                            'att2': 'val2'}))

    def test_can_specify_attributes_shorthand(self):
        args = ['eval', 'var1,var2:%s' % single_valid_file, 'var1^var2 / var3', 'units',
                '-a', 'att1=val1,att2=val2']
        parsed = parse_args(args)
        assert_that(parsed.attributes, is_({'att1': 'val1',
                                            'att2': 'val2'}))

    def test_invalid_attributes_throws_parser_error(self):
        args = ['eval', 'var1,var2:%s' % single_valid_file, 'var1^var2 / var3', 'units',
                '-a']
        attributes = ['att1val1,att2=val2', '=', '=val', 'key=']
        for attr in attributes:
            full_args = args + [attr]
            try:
                parse_args(full_args)
                assert False
            except SystemExit as e:
                if e.code != 2:
                    raise e


class TestParseStats(TestCase):
    """
    Tests specific to the stats command
    """

    def test_GIVEN_no_output_WHEN_parse_stats_THEN_output_is_None(self):
        args = ['stats', 'var1,var2:%s' % single_valid_file]
        arguments = parse_args(args)
        assert_that(arguments.output, is_(None))

    def test_GIVEN_one_variable_WHEN_parse_stats_THEN_parser_error(self):
        args = ['stats', 'var1:%s' % single_valid_file]
        try:
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_GIVEN_more_than_two_variables_WHEN_parse_stats_THEN_parser_error(self):
        args = ['stats', 'var1,var2:%s' % single_valid_file,
                'var3:%s' % single_valid_file]
        try:
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_GIVEN_two_variables_WHEN_parse_stats_THEN_variables_are_in_datagroups(self):
        args = ['stats', 'var1:%s' % single_valid_file, 'var2:%s' % dummy_cis_out]
        arguments = parse_args(args)
        assert_that(arguments.datagroups[0]['filenames'], is_([single_valid_file]))
        assert_that(arguments.datagroups[0]['variables'], is_(['var1']))
        assert_that(arguments.datagroups[1]['filenames'], is_([dummy_cis_out]))
        assert_that(arguments.datagroups[1]['variables'], is_(['var2']))

    def test_GIVEN_output_file_WHEN_parse_stats_THEN_output_file_in_arguments(self):
        args = ['stats', 'var1,var2:%s' % single_valid_file, '-o', 'output']
        arguments = parse_args(args)
        assert_that(arguments.output, is_('output.nc'))


class TestParseSubset(TestCase):
    """
    Tests specific to the subset command
    """

    def test_GIVEN_longitude_limits_not_monotonically_increasing_WHEN_subset_THEN_raises_error(self):
        limits = ['x=[270,90]', 'x=[-30,-60]']
        for lim in limits:
            args = ['subset', 'var1:%s' % single_valid_file, lim]
            try:
                parse_args(args)
                assert False
            except SystemExit as e:
                if e.code != 2:
                    raise

    def test_GIVEN_longitude_limits_wider_than_360_WHEN_subset_THEN_raises_error(self):
        limits = ['x=[-180,360]', 'x=[-1,360]']
        for lim in limits:
            args = ['subset', 'var1:%s' % single_valid_file, lim]
            try:
                parse_args(args)
                assert False
            except SystemExit as e:
                if e.code != 2:
                    raise

    def test_GIVEN_longitude_limits_valid_WHEN_subset_THEN_parsed_OK(self):
        limits = ['x=[-10,10]', 'x=[0,360]', 'x=[-180.0,180.0]']
        for lim in limits:
            args = ['subset', 'var1:%s' % single_valid_file, lim]
            parse_args(args)

    def test_GIVEN_subset_command_WHEN_multiple_variables_in_datagroup_THEN_variables_unpacked(self):
        var1, var2 = 'rain', 'snow'
        limits = 'x=[-10,10],y=[40,60]'
        output = 'subset-out'
        product = 'cis'
        args = ["subset", var1 + "," + var2 + ':' + test_directory_files[0] + ':product=' + product, limits, '-o', output]
        main_args = parse_args(args)
        dg = main_args.datagroups
        assert_that(len(dg), is_(1))
        assert_that(dg[0]['filenames'], is_([test_directory_files[0]]))
        assert_that(dg[0]['product'], is_('cis'))
        assert_that(dg[0]['variables'], contains_inanyorder('rain', 'snow'))


class TestParseAggregate(TestCase):
    """
    Tests specific to the aggregate command
    """

    def test_GIVEN_aggregate_command_WHEN_multiple_variables_in_datagroup_THEN_variables_unpacked(self):
        var1, var2 = 'rain', 'snow'
        grid = 'x=[-10,10,2]'
        output = 'aggregate-out'
        product = 'cis'
        args = ["aggregate", var1 + "," + var2 + ':' + test_directory_files[0] + ':product=' + product, grid, '-o', output]
        main_args = parse_args(args)
        dg = main_args.datagroups
        assert_that(len(dg), is_(1))
        assert_that(dg[0]['filenames'], is_([test_directory_files[0]]))
        assert_that(dg[0]['product'], is_('cis'))
        assert_that(dg[0]['variables'], contains_inanyorder('rain', 'snow'))

    def test_GIVEN_longitude_limits_not_monotonically_increasing_WHEN_aggregate_THEN_raises_error(self):
        limits = ['x=[270,90,10]', 'x=[-30,-60,1]']
        for lim in limits:
            args = ['aggregate', 'var1:%s' % single_valid_file, lim]
            try:
                parse_args(args)
                assert False
            except SystemExit as e:
                if e.code != 2:
                    raise

    def test_GIVEN_longitude_limits_wider_than_360_WHEN_aggregate_THEN_raises_error(self):
        limits = ['x=[-180,360,10]', 'x=[-1,360,5]']
        for lim in limits:
            args = ['aggregate', 'var1:%s' % single_valid_file, lim]
            try:
                parse_args(args)
                assert False
            except SystemExit as e:
                if e.code != 2:
                    raise

    def test_GIVEN_longitude_limits_valid_WHEN_aggregate_THEN_parsed_OK(self):
        limits = ['x=[-10,10,1]', 'x=[0,360,10]', 'x=[-180.0,180.0,5]']
        for lim in limits:
            args = ['aggregate', 'var1:%s' % single_valid_file, lim]
            parse_args(args)


class TestParseColocate(TestCase):
    """
    Tests specific to the colocate command
    """

    def test_GIVEN_colocate_command_WHEN_multiple_variables_in_datagroup_THEN_variables_unpacked(self):
        var1, var2 = 'rain', 'snow'
        output = 'aggregate-out'
        samplegroup = test_directory_files[0] + ':colocator=bin'
        product = 'cis'
        args = ["col", var1 + "," + var2 + ':' + test_directory_files[0] + ':product=' + product, samplegroup, '-o', output]
        main_args = parse_args(args)
        dg = main_args.datagroups
        assert_that(len(dg), is_(1))
        assert_that(dg[0]['filenames'], is_([test_directory_files[0]]))
        assert_that(dg[0]['product'], is_('cis'))
        assert_that(dg[0]['variables'], contains_inanyorder('rain', 'snow'))

    def test_can_leave_colocator_missing(self):
        var = 'rain'
        samplegroup = test_directory_files[0] + ':variable=rain'
        args = ["col", var + ':' + test_directory_files[0], samplegroup]
        main_args = parse_args(args)
        sg = main_args.samplegroup
        assert_that(sg['colocator'], is_(None))
        assert_that(sg['variable'], is_('rain'))

    def test_can_specify_one_valid_samplefile_and_one_complete_datagroup(self):
        args = ["col", "variable:" + test_directory_files[0], test_directory_files[0] + ":colocator=col,constraint=con,kernel=nn"]
        args = parse_args(args)
        eq_([test_directory_files[0]], args.samplegroup['filenames'])
        eq_(('col', {}), args.samplegroup['colocator'])
        eq_(('con', {}), args.samplegroup['constraint'])
        eq_(('nn', {}), args.samplegroup['kernel'])
        eq_([{'variables': ['variable'], 'product': None, 'filenames': [test_directory_files[0]]}], args.datagroups)

    def test_can_specify_one_valid_samplefile_and_one_datafile_without_other_options(self):
        args = ["col", "variable:" + test_directory_files[0], test_directory_files[0] + ':colocator=bin']
        args = parse_args(args)
        eq_([test_directory_files[0]], args.samplegroup['filenames'])
        eq_(('bin', {}), args.samplegroup['colocator'])
        eq_(None, args.samplegroup['constraint'])
        eq_(None, args.samplegroup['kernel'])
        eq_([{'variables': ['variable'], 'product': None, 'filenames': [test_directory_files[0]]}], args.datagroups)

    def test_can_specify_one_valid_samplefile_and_many_datagroups(self):
        args = ["col", "variable1:" + test_directory_files[0],
                "variable2:" + test_directory_files[0],
                "variable3:" + test_directory_files[0],
                test_directory_files[0] + ':variable=variable4,colocator=col,kernel=nn']
        args = parse_args(args)
        eq_([test_directory_files[0]], args.samplegroup['filenames'])
        eq_("variable4", args.samplegroup['variable'])
        eq_(('col', {}), args.samplegroup['colocator'])
        eq_(None, args.samplegroup['constraint'])
        eq_(('nn', {}), args.samplegroup['kernel'])
        eq_([test_directory_files[0]], args.datagroups[0]['filenames'])
        eq_(["variable1"], args.datagroups[0]['variables'])
        eq_([test_directory_files[0]], args.datagroups[1]['filenames'])
        eq_(["variable2"], args.datagroups[1]['variables'])
        eq_([test_directory_files[0]], args.datagroups[2]['filenames'])
        eq_(["variable3"], args.datagroups[2]['variables'])

    def test_can_specify_one_valid_samplefile_and_one_datafile_with_internal_options(self):
        args = ["col", "var1:" + test_directory_files[0], test_directory_files[0]
                + ":variable=var2,constraint=SepConstraint[h_sep=1500,v_sep=22000,t_sep=5000],kernel=nn,colocator=bin"]
        args = parse_args(args)
        eq_([test_directory_files[0]], args.datagroups[0]['filenames'])
        eq_(["var1"], args.datagroups[0]['variables'])
        eq_([test_directory_files[0]], args.samplegroup['filenames'])
        eq_("var2", args.samplegroup['variable'])
        eq_(('SepConstraint', {'h_sep': '1500', 'v_sep': '22000', 't_sep': '5000'}), args.samplegroup['constraint'])
        eq_(('nn', {}), args.samplegroup['kernel'])
        eq_(('bin', {}), args.samplegroup['colocator'])
        eq_(None, args.samplegroup['product'])
