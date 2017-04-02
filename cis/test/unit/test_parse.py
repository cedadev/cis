"""
Module to test the parser
The parse raises a SystemExit exception with code 2 if it fails to parse.
Each test therefore ignores SystemExit exceptions with code 2 as they are expected.
"""
import argparse
from unittest import TestCase
import os
from mock import patch
from hamcrest import is_, assert_that, contains_inanyorder
from nose.tools import eq_, raises

from cis.parse import parse_args, expand_file_list
from cis.plotting.plot import plot_types


def escape_colons(string):
    import re
    return re.sub(r'([\:])', r'\\\1', string)


class ParseTestFiles(TestCase):
    def setUp(self):
        """
            Create the temporary files necassary for testing
        :return:
        """
        from tempfile import mkdtemp
        import os

        def _make_file(file):
            """
                Creates an empty file and then closes it (similar to 'touch' on linux)
            :param file:
            :return:
            """
            open(file, 'w').close()

        # Create a temporary directory to put our test files in
        self.data_directory = mkdtemp('cis_test_dir')

        # Name all of our test files (with full paths)
        self.test_directory = os.path.join(self.data_directory, 'test_directory_for_parser')
        os.mkdir(self.test_directory)
        self.escaped_test_directory = escape_colons(self.test_directory)

        self.escaped_test_directory_files = []
        self.test_directory_files = []
        for i in range(1, 4):
            test_directory_file = os.path.join(self.test_directory, 'test_file_for_parser_{}'.format(i))
            _make_file(test_directory_file)
            self.escaped_test_directory_files.append(escape_colons(test_directory_file))
            self.test_directory_files.append(test_directory_file)

        single_valid_file = os.path.join(self.data_directory, "single_data_file")
        _make_file(single_valid_file)
        self.single_valid_file = single_valid_file
        self.escaped_single_valid_file = escape_colons(single_valid_file)

        self.multiple_valid_files = []
        self.escaped_multiple_valid_files = []
        for i in range(1, 3):
            valid_file = os.path.join(self.data_directory, 'data_file_{}'.format(i))
            _make_file(valid_file)
            self.multiple_valid_files.append(valid_file)
            self.escaped_multiple_valid_files.append(escape_colons(valid_file))

        self.data_file_wildcard = os.path.join(self.data_directory, 'data_file*')

    def tearDown(self):
        """
            Remove the test directory and everything below it.
        :return:
        """
        from shutil import rmtree
        rmtree(self.data_directory)


class TestParse(ParseTestFiles):
    """
    Generic parser tests not specific to one particular command
    """

    def test_order_is_preserved_when_specifying_individual_files(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(self.test_directory_files[0] + "," + self.test_directory_files[1], parser)
        eq_(files, [self.test_directory_files[0], self.test_directory_files[1]])
        files = expand_file_list(self.test_directory_files[1] + "," + self.test_directory_files[0], parser)
        eq_(files, [self.test_directory_files[1], self.test_directory_files[0]])

    def test_directories_are_sorted(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(self.test_directory, parser)
        eq_(files, self.test_directory_files)

    def test_wildcarded_files_are_sorted(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(os.path.join(self.test_directory,
                                              'test_file_for_parser_*'), parser)
        eq_(files, self.test_directory_files)

    def test_order_is_preserved_when_specifying_files_even_when_wildcards_and_directories_are_specified_too(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(','.join([self.single_valid_file, self.data_file_wildcard,
                                           self.test_directory]), parser)
        eq_(files, [self.single_valid_file] + self.multiple_valid_files + self.test_directory_files)

    def test_can_specify_one_valid_filename_and_a_directory(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(self.single_valid_file + ',' + self.test_directory, parser)
        eq_(files, [self.single_valid_file] + self.test_directory_files)

    def test_can_specify_a_directory(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(self.test_directory, parser)
        eq_(files, self.test_directory_files)

    def test_can_specify_a_file_with_wildcards(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(os.path.join(self.test_directory, 'test_file_for_parser_*'), parser)
        eq_(files, self.test_directory_files)
        files = expand_file_list(os.path.join(self.test_directory, '*_1'), parser)
        eq_(files, [self.test_directory_files[0]])
        files = expand_file_list(os.path.join(self.test_directory, 'test_file_for_parser_?'), parser)
        eq_(files, self.test_directory_files)
        files = expand_file_list(os.path.join(self.test_directory, 'test_file_for_parser_[0-9]'), parser)
        eq_(files, self.test_directory_files)

    def test_can_specify_one_valid_filename_and_a_wildcarded_file(self):
        parser = argparse.ArgumentParser()
        files = expand_file_list(
            self.single_valid_file + ',' + os.path.join(self.test_directory, 'test_file_for_parser_[0-9]'),
            parser)
        eq_(files, [self.single_valid_file] + self.test_directory_files)

    def test_duplicate_files_are_not_returned_from_expand_file_list(self):
        parser = argparse.ArgumentParser()
        part_1 = os.path.join(self.test_directory, 'test_file_for_parser_1')
        part_2 = os.path.join(self.test_directory, 'test_file_for_parser_[0-9]')
        files = expand_file_list(','.join([part_1, part_2]), parser)
        eq_(files, self.test_directory_files)

    def test_can_specify_one_valid_filename(self):
        args = ["plot", "var:" + self.escaped_test_directory_files[0]]
        parse_args(args)

    def test_should_raise_error_with_one_invalid_filename(self):
        try:
            args = ["plot", "var:invalidfilename"]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_can_specify_more_than_one_valid_filename(self):
        args = ["plot", "var:" + ','.join(self.escaped_test_directory_files[0:1])]
        parse_args(args)

    def test_should_raise_error_with_a_mixture_of_valid_and_invalid_filenames(self):
        try:
            args = ["plot", "var:" + self.escaped_test_directory_files[0] + ',invalidfilename']
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_GIVEN_input_contains_output_WHEN_parse_THEN_raises_error(self):
        dummy_cis_out = 'out.nc'
        args_list = [["subset", "var:" + dummy_cis_out, "x=[-180,180]", "-o", dummy_cis_out[:-3]],
                     ["col", "var1,var2:" + dummy_cis_out, self.escaped_single_valid_file + ':collocator=bin',
                      "-o", dummy_cis_out[:-3]],
                     ["col", "var1,var2:" + self.escaped_single_valid_file, dummy_cis_out + ':collocator=bin',
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
        args = ['eval', 'var1,var2:%s:product=cis' % self.escaped_single_valid_file,
                'var1 + var2 + var3', 'units', '-o', 'output_name']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('output_name.nc'))

    def test_GIVEN_output_has_file_extension_WHEN_parse_THEN_extension_not_added(self):
        args = ['eval', 'var1,var2:%s:product=cis' % self.escaped_single_valid_file,
                'var1 + var2 + var3', 'units', '-o', 'output_name.nc']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('output_name.nc'))

    def test_can_escape_variables_with_colons(self):
        args = ['plot', 'my\:var:{0}:product=cis'.format(self.escaped_single_valid_file)]
        parsed = parse_args(args)
        assert_that('my:var' in parsed.datagroups[0]['variables'])

    def test_GIVEN_plot_output_missing_file_extension_WHEN_parse_THEN_extension_added(self):
        args = ['plot', 'var1:%s:product=cis' % self.escaped_single_valid_file,
                '-o', 'output_name']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('output_name.png'))

    def test_output_file_matches_an_existing_file_with_force_overwrite_option(self):
        from cis.parse import _file_already_exists_and_no_overwrite
        from argparse import Namespace
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile() as tmpfile:
            existing_file = tmpfile.name
            arguments = Namespace(force_overwrite=True)
            # Test output file is the same as input file
            arguments.output = existing_file
            assert not _file_already_exists_and_no_overwrite(arguments)

    def test_output_file_matches_an_existing_file_with_force_overwrite_env(self):
        from cis.parse import _file_already_exists_and_no_overwrite
        from argparse import Namespace
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile() as tmpfile:
            existing_file = tmpfile.name
            arguments = Namespace(force_overwrite=False)
            # Test output file is the same as input file
            arguments.output = existing_file
            os.environ["CIS_FORCE_OVERWRITE"] = "True"
            assert not _file_already_exists_and_no_overwrite(arguments)
            os.environ["CIS_FORCE_OVERWRITE"] = ""

    def test_output_file_matches_an_existing_file_with_force_overwrite_env_FALSE(self):
        from cis.parse import _file_already_exists_and_no_overwrite
        from argparse import Namespace
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile() as tmpfile:
            existing_file = tmpfile.name
            arguments = Namespace(force_overwrite=False)
            # Test output file is the same as input file
            arguments.output = existing_file
            os.environ["CIS_FORCE_OVERWRITE"] = "False"
            with patch("six.moves.input", return_value='n') as in_patch:
                # Check we're not going to overwrite the file
                assert _file_already_exists_and_no_overwrite(arguments)
                # Check we didn't have to ask for input to work that out
                assert in_patch.call_count == 0
            os.environ["CIS_FORCE_OVERWRITE"] = ""

    def test_output_file_matches_an_existing_file_with_no_force_overwrite_will_prompt(self):
        from cis.parse import _file_already_exists_and_no_overwrite
        from argparse import Namespace
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile() as tmpfile:
            existing_file = tmpfile.name
            arguments = Namespace(force_overwrite=False)
            # Test output file is the same as input file
            arguments.output = existing_file

            # Choose yes to overwrite - so return false
            with patch('six.moves.input', return_value='y'):
                assert not _file_already_exists_and_no_overwrite(arguments)

            # Choose no to not overwrite - return True
            with patch('six.moves.input', return_value='n'):
                assert _file_already_exists_and_no_overwrite(arguments)

            # Choose yes, eventually
            with patch('six.moves.input', side_effect=['blah', 'blah', 'y']):
                assert not _file_already_exists_and_no_overwrite(arguments)

            # Choose the default (no)
            with patch('six.moves.input', return_value=''):
                assert _file_already_exists_and_no_overwrite(arguments)

            # Choose the default, eventually
            with patch('six.moves.input', side_effect=['yo', 'nope', '']):
                assert _file_already_exists_and_no_overwrite(arguments)


class TestParsePlot(ParseTestFiles):
    """
    Tests specific to the plot command
    """

    def test_can_specify_valid_chart_type(self):
        args = ["plot", "var:" + self.escaped_test_directory_files[0], "--type",
                list(plot_types.keys())[0]]
        parse_args(args)

    def test_should_raise_error_with_an_invalid_chart_type(self):
        try:
            args = ["plot", "var:" + self.escaped_test_directory_files[0], "--type", "dfgdfgdfgdfgdfgdf"]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_should_raise_error_with_more_than_one_chart_type(self):
        try:
            args = ["plot", "var:" + self.escaped_test_directory_files[0], "--type",
                    list(plot_types.keys())[0], list(plot_types.keys())[1]]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_can_specify_more_than_one_variable(self):
        args = ["plot", "var:" + self.escaped_test_directory_files[0], "var:" + self.escaped_test_directory_files[0]]
        parse_args(args)

    def test_should_raise_error_when_no_variable_is_specified(self):
        try:
            args = ["plot", self.escaped_test_directory_files[0]]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_should_raise_error_with_invalid_line_width(self):
        try:
            args = ["plot", "var:" + self.escaped_test_directory_files[0], "--itemwidth", "4a0"]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_should_raise_error_with_invalid_line_style(self):
        try:
            args = ["plot", "var:" + self.escaped_test_directory_files[0], "--linestyle", "4a0"]
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e


class TestParseEvaluate(ParseTestFiles):
    """
    Tests specific to the evaluate command
    """

    def test_parse_evaluate_single_datagroup(self):
        args = ['eval', 'var1,var2:%s:product=cis' % self.escaped_single_valid_file,
                'var1 + var2 + var3', 'units', '-o', 'output.nc']
        parsed = parse_args(args)
        assert_that(parsed.command, is_('eval'))
        assert_that(parsed.expr, is_('var1 + var2 + var3'))
        assert_that(parsed.units, is_('units'))
        assert_that(parsed.output, is_('output.nc'))
        assert_that(len(parsed.datagroups), is_(1))
        assert_that(parsed.datagroups[0]['filenames'], is_([self.single_valid_file]))
        assert_that(parsed.datagroups[0]['variables'], is_(['var1', 'var2']))
        assert_that(parsed.datagroups[0]['product'], is_('cis'))

    def test_parse_evaluate_multiple_datagroups(self):
        args = ['eval', 'var1,var2:%s' % self.escaped_multiple_valid_files[0],
                'var3:%s' % self.escaped_multiple_valid_files[1], 'var1^var2 / var3', 'units', '-o', 'output.nc']
        parsed = parse_args(args)
        assert_that(parsed.command, is_('eval'))
        assert_that(parsed.expr, is_('var1^var2 / var3'))
        assert_that(parsed.units, is_('units'))
        assert_that(parsed.output, is_('output.nc'))
        assert_that(len(parsed.datagroups), is_(2))
        assert_that(parsed.datagroups[0]['filenames'], is_([self.multiple_valid_files[0]]))
        assert_that(parsed.datagroups[0]['variables'], is_(['var1', 'var2']))
        assert_that(parsed.datagroups[1]['filenames'], is_([self.multiple_valid_files[1]]))
        assert_that(parsed.datagroups[1]['variables'], is_(['var3']))

    def test_parse_evaluate_output_variable(self):
        args = ['eval', 'var1,var2:%s' % self.escaped_single_valid_file,
                'var3:%s' % self.escaped_multiple_valid_files[0], 'var1^var2 / var3', 'units', '-o',
                'out_var:output.nc']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('output.nc'))
        assert_that(parsed.output_var, is_('out_var'))

    def test_parse_evaluate_no_output_variable(self):
        args = ['eval', 'var1,var2:%s' % self.escaped_single_valid_file,
                'var3:%s' % self.escaped_multiple_valid_files[0], 'var1^var2 / var3', 'units', '-o', 'output.nc']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('output.nc'))
        assert_that(parsed.output_var, is_(None))

    def test_parse_evaluate_no_output(self):
        args = ['eval', 'var1,var2:%s' % self.escaped_single_valid_file,
                'var3:%s' % self.escaped_single_valid_file, 'var1^var2 / var3', 'units']
        parsed = parse_args(args)
        assert_that(parsed.output, is_('out.nc'))
        assert_that(parsed.output_var, is_(None))

    def test_parse_evaluate_invalid_output(self):
        args = ['eval', 'var1,var2:%s' % self.escaped_single_valid_file,
                'var3:%s' % self.escaped_multiple_valid_files[0], 'var1^var2 / var3', 'units', '-o', 'var:var:out']
        try:
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_parse_evaluate_valid_aliases(self):
        # Should use the given alias or the variable name if not provided
        args = ['eval', 'var1=alias1,var2:%s' % self.escaped_single_valid_file,
                'var3=alias3:%s' % self.escaped_multiple_valid_files[0], 'var1^var2 / var3', 'units', '-o', 'output.nc']
        parsed = parse_args(args)
        assert_that(parsed.datagroups[0]['variables'], is_(['var1', 'var2']))
        assert_that(parsed.datagroups[0]['aliases'], is_(['alias1', 'var2']))
        assert_that(parsed.datagroups[1]['variables'], is_(['var3']))
        assert_that(parsed.datagroups[1]['aliases'], is_(['alias3']))

    def test_parse_evaluate_duplicate_aliases(self):
        args = ['eval', 'var1=alias1,var2=alias1:%s' % self.escaped_single_valid_file,
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
            args = ['eval', '%s:%s' % (var, self.escaped_single_valid_file),
                    'var1^var2 / var3', 'units', '-o', 'output.nc']
            try:
                parse_args(args)
                assert False
            except SystemExit as e:
                if e.code != 2:
                    raise e

    def test_parse_evaluate_missing_units_single_datagroup(self):
        args = ['eval', 'var1,var2:%s' % self.escaped_single_valid_file,
                'var1 + var2']
        try:
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_can_specify_attributes(self):
        args = ['eval', 'var1,var2:%s' % self.escaped_single_valid_file, 'var1^var2 / var3', 'units',
                '--attributes', 'att1=val1,att2=val2']
        parsed = parse_args(args)
        assert_that(parsed.attributes, is_({'att1': 'val1',
                                            'att2': 'val2'}))

    def test_can_specify_attributes_shorthand(self):
        args = ['eval', 'var1,var2:%s' % self.escaped_single_valid_file, 'var1^var2 / var3', 'units',
                '-a', 'att1=val1,att2=val2']
        parsed = parse_args(args)
        assert_that(parsed.attributes, is_({'att1': 'val1',
                                            'att2': 'val2'}))

    def test_invalid_attributes_throws_parser_error(self):
        args = ['eval', 'var1,var2:%s' % self.escaped_single_valid_file, 'var1^var2 / var3', 'units',
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


class TestParseStats(ParseTestFiles):
    """
    Tests specific to the stats command
    """

    def test_GIVEN_no_output_WHEN_parse_stats_THEN_output_is_None(self):
        args = ['stats', 'var1,var2:%s' % self.escaped_single_valid_file]
        arguments = parse_args(args)
        assert_that(arguments.output, is_(None))

    def test_GIVEN_one_variable_WHEN_parse_stats_THEN_parser_error(self):
        args = ['stats', 'var1:%s' % self.escaped_single_valid_file]
        try:
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_GIVEN_more_than_two_variables_WHEN_parse_stats_THEN_parser_error(self):
        args = ['stats', 'var1,var2:%s' % self.escaped_single_valid_file,
                'var3:%s' % self.escaped_single_valid_file]
        try:
            parse_args(args)
            assert False
        except SystemExit as e:
            if e.code != 2:
                raise e

    def test_GIVEN_two_variables_WHEN_parse_stats_THEN_variables_are_in_datagroups(self):
        args = ['stats', 'var1:%s' % self.escaped_single_valid_file, 'var2:%s' % self.escaped_multiple_valid_files[0]]
        arguments = parse_args(args)
        assert_that(arguments.datagroups[0]['filenames'], is_([self.single_valid_file]))
        assert_that(arguments.datagroups[0]['variables'], is_(['var1']))
        assert_that(arguments.datagroups[1]['filenames'], is_([self.multiple_valid_files[0]]))
        assert_that(arguments.datagroups[1]['variables'], is_(['var2']))

    def test_GIVEN_output_file_WHEN_parse_stats_THEN_output_file_in_arguments(self):
        args = ['stats', 'var1,var2:%s' % self.escaped_single_valid_file, '-o', 'output']
        arguments = parse_args(args)
        assert_that(arguments.output, is_('output.nc'))


class TestParseSubset(ParseTestFiles):
    """
    Tests specific to the subset command
    """

    def test_GIVEN_longitude_limits_not_monotonically_increasing_WHEN_subset_THEN_raises_error(self):
        limits = ['x=[270,90]', 'x=[-30,-60]']
        for lim in limits:
            args = ['subset', 'var1:%s' % self.escaped_single_valid_file, lim]
            try:
                parse_args(args)
                assert False
            except SystemExit as e:
                if e.code != 2:
                    raise

    def test_GIVEN_longitude_limits_wider_than_360_WHEN_subset_THEN_raises_error(self):
        limits = ['x=[-180,360]', 'x=[-1,360]']
        for lim in limits:
            args = ['subset', 'var1:%s' % self.escaped_single_valid_file, lim]
            try:
                parse_args(args)
                assert False
            except SystemExit as e:
                if e.code != 2:
                    raise

    def test_GIVEN_longitude_limits_valid_WHEN_subset_THEN_parsed_OK(self):
        limits = ['x=[-10,10]', 'x=[0,360]', 'x=[-180.0,180.0]']
        for lim in limits:
            args = ['subset', 'var1:%s' % self.escaped_single_valid_file, lim]
            parse_args(args)

    def test_GIVEN_subset_command_WHEN_multiple_variables_in_datagroup_THEN_variables_unpacked(self):
        var1, var2 = 'rain', 'snow'
        limits = 'x=[-10,10],y=[40,60]'
        output = 'subset-out'
        product = 'cis'
        args = ["subset", var1 + "," + var2 + ':' + self.escaped_test_directory_files[0] + ':product=' + product,
                limits, '-o', output]
        main_args = parse_args(args)
        dg = main_args.datagroups
        assert_that(len(dg), is_(1))
        assert_that(dg[0]['filenames'], is_([self.test_directory_files[0]]))
        assert_that(dg[0]['product'], is_('cis'))
        assert_that(dg[0]['variables'], contains_inanyorder('rain', 'snow'))


class TestParseAggregate(ParseTestFiles):
    """
    Tests specific to the aggregate command
    """

    def test_GIVEN_aggregate_command_WHEN_multiple_variables_in_datagroup_THEN_variables_unpacked(self):
        var1, var2 = 'rain', 'snow'
        grid = 'x=[-10,10,2]'
        output = 'aggregate-out'
        product = 'cis'
        args = ["aggregate", var1 + "," + var2 + ':' + self.escaped_test_directory_files[0] + ':product=' + product,
                grid, '-o', output]
        main_args = parse_args(args)
        dg = main_args.datagroups
        assert_that(len(dg), is_(1))
        assert_that(dg[0]['filenames'], is_([self.test_directory_files[0]]))
        assert_that(dg[0]['product'], is_('cis'))
        assert_that(dg[0]['variables'], contains_inanyorder('rain', 'snow'))

    def test_GIVEN_longitude_limits_not_monotonically_increasing_WHEN_aggregate_THEN_raises_error(self):
        limits = ['x=[270,90,10]', 'x=[-30,-60,1]']
        for lim in limits:
            args = ['aggregate', 'var1:%s' % self.escaped_single_valid_file, lim]
            try:
                parse_args(args)
                assert False
            except SystemExit as e:
                if e.code != 2:
                    raise

    def test_GIVEN_longitude_limits_wider_than_360_WHEN_aggregate_THEN_raises_error(self):
        limits = ['x=[-180,360,10]', 'x=[-1,360,5]']
        for lim in limits:
            args = ['aggregate', 'var1:%s' % self.escaped_single_valid_file, lim]
            try:
                parse_args(args)
                assert False
            except SystemExit as e:
                if e.code != 2:
                    raise

    def test_GIVEN_longitude_limits_valid_WHEN_aggregate_THEN_parsed_OK(self):
        limits = ['x=[-10,10,1]', 'x=[0,360,10]', 'x=[-180.0,180.0,5]']
        for lim in limits:
            args = ['aggregate', 'var1:%s' % self.escaped_single_valid_file, lim]
            parse_args(args)

    def test_GIVEN_mixed_limits_valid_WHEN_aggregate_THEN_parsed_OK(self):
        limits = ['x=[-180.0,180.0,0.5],y=[-80.0,10.0,0.1]',
                  'x=[-180.0,180.0,0.5],y=[-80.0,10.0,0.1],t=[2008-05-12,2008-05-12,PT15M]']
        for lim in limits:
            args = ['aggregate', 'var1:%s' % self.escaped_single_valid_file, lim]
            parse_args(args)

    def test_output_file_matches_an_input_file(self):
        from cis.parse import _output_file_matches_an_input_file
        from argparse import Namespace
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile() as tmpfile:
            input_file = tmpfile.name
            arguments = Namespace()
            # Test output file is the same as input file
            arguments.output = input_file
            arguments.datagroups = [{"filenames": [input_file]}]
            assert _output_file_matches_an_input_file(arguments)

            # Test output file is different
            with NamedTemporaryFile() as tmp_out:
                arguments.output = tmp_out.name
                assert not _output_file_matches_an_input_file(arguments)

            # Test output file is different (and doesn't exist)
            arguments.output = 'blah'
            assert not _output_file_matches_an_input_file(arguments)


class TestParseCollocate(ParseTestFiles):
    """
    Tests specific to the collocate command
    """

    def test_GIVEN_collocate_command_WHEN_multiple_variables_in_datagroup_THEN_variables_unpacked(self):
        var1, var2 = 'rain', 'snow'
        output = 'aggregate-out'
        samplegroup = self.escaped_test_directory_files[0] + ':collocator=bin'
        product = 'cis'
        args = ["col", var1 + "," + var2 + ':' + self.escaped_test_directory_files[0] + ':product=' + product,
                samplegroup, '-o', output]
        main_args = parse_args(args)
        dg = main_args.datagroups
        assert_that(len(dg), is_(1))
        assert_that(dg[0]['filenames'], is_([self.test_directory_files[0]]))
        assert_that(dg[0]['product'], is_('cis'))
        assert_that(dg[0]['variables'], contains_inanyorder('rain', 'snow'))

    def test_can_leave_collocator_missing(self):
        var = 'rain'
        samplegroup = self.escaped_test_directory_files[0] + ':variable=rain'
        args = ["col", var + ':' + self.escaped_test_directory_files[0], samplegroup]
        main_args = parse_args(args)
        sg = main_args.samplegroup
        assert_that(not sg.get('collocator', False))
        assert_that(sg['variable'], is_('rain'))

    def test_can_specify_one_valid_samplefile_and_one_complete_datagroup(self):
        args = ["col", "variable:" + self.escaped_test_directory_files[0], self.escaped_test_directory_files[0] +
                ":collocator=col,constraint=con,kernel=nn"]
        args = parse_args(args)
        eq_([self.test_directory_files[0]], args.samplegroup['filenames'])
        eq_(('col', {}), args.samplegroup['collocator'])
        eq_(('con', {}), args.samplegroup['constraint'])
        eq_(('nn', {}), args.samplegroup['kernel'])
        eq_([{'variables': ['variable'], 'filenames': [self.test_directory_files[0]]}], args.datagroups)

    def test_can_specify_one_valid_samplefile_and_one_datafile_without_other_options(self):
        args = ["col", "variable:" + self.escaped_test_directory_files[0], self.escaped_test_directory_files[0] +
                ':collocator=bin']
        args = parse_args(args)
        eq_([self.test_directory_files[0]], args.samplegroup['filenames'])
        eq_(('bin', {}), args.samplegroup['collocator'])
        eq_([{'variables': ['variable'], 'filenames': [self.test_directory_files[0]]}], args.datagroups)

    def test_can_specify_one_valid_samplefile_and_many_datagroups(self):
        args = ["col", "variable1:" + self.escaped_test_directory_files[0],
                "variable2:" + self.escaped_test_directory_files[0],
                "variable3:" + self.escaped_test_directory_files[0],
                self.escaped_test_directory_files[0] + ':variable=variable4,collocator=col,kernel=nn']
        args = parse_args(args)
        eq_([self.test_directory_files[0]], args.samplegroup['filenames'])
        eq_("variable4", args.samplegroup['variable'])
        eq_(('col', {}), args.samplegroup['collocator'])
        eq_(False, args.samplegroup.get('constraint', False))
        eq_(('nn', {}), args.samplegroup['kernel'])
        eq_([self.test_directory_files[0]], args.datagroups[0]['filenames'])
        eq_(["variable1"], args.datagroups[0]['variables'])
        eq_([self.test_directory_files[0]], args.datagroups[1]['filenames'])
        eq_(["variable2"], args.datagroups[1]['variables'])
        eq_([self.test_directory_files[0]], args.datagroups[2]['filenames'])
        eq_(["variable3"], args.datagroups[2]['variables'])

    def test_can_specify_one_valid_samplefile_and_one_datafile_with_internal_options(self):
        args = ["col", "var1:" + self.escaped_test_directory_files[0], self.escaped_test_directory_files[0] +
                ":variable=var2,constraint=SepConstraint[h_sep=1500,v_sep=22000,t_sep=5000],kernel=nn,collocator=bin"]
        args = parse_args(args)
        eq_([self.test_directory_files[0]], args.datagroups[0]['filenames'])
        eq_(["var1"], args.datagroups[0]['variables'])
        eq_([self.test_directory_files[0]], args.samplegroup['filenames'])
        eq_("var2", args.samplegroup['variable'])
        eq_(('SepConstraint', {'h_sep': '1500', 'v_sep': '22000', 't_sep': '5000'}), args.samplegroup['constraint'])
        eq_(('nn', {}), args.samplegroup['kernel'])
        eq_(('bin', {}), args.samplegroup['collocator'])


class TestParseInfo(ParseTestFiles):
    """
    Tests specific to the info command
    """

    def test_GIVEN_info_command_WHEN_single_file_present_THEN_empty_variable_and_product(self):
        args = ["info", self.escaped_test_directory_files[0]]
        main_args = parse_args(args)
        dg = main_args.datagroups
        assert_that(len(dg), is_(1))
        assert_that(dg[0]['filenames'], is_([self.test_directory_files[0]]))
        assert_that(dg[0].get('product', None), is_(None))
        assert_that(dg[0].get('variables', None), is_(None))

    def test_GIVEN_info_command_WHEN_many_files_present_THEN_empty_variable_and_product(self):
        args = ["info", ",".join(self.escaped_test_directory_files)]
        main_args = parse_args(args)
        dg = main_args.datagroups
        assert_that(len(dg), is_(1))
        assert_that(dg[0]['filenames'], is_(self.test_directory_files))
        assert_that(dg[0].get('product', None), is_(None))
        assert_that(dg[0].get('variables', None), is_(None))

    def test_GIVEN_info_command_WHEN_files_and_single_var_present_THEN_single_variable_and_empty_product(self):
        var1 = 'rain'
        args = ["info", var1 + ':' + self.escaped_test_directory_files[0]]
        main_args = parse_args(args)
        dg = main_args.datagroups
        assert_that(len(dg), is_(1))
        assert_that(dg[0]['filenames'], is_([self.test_directory_files[0]]))
        assert_that(dg[0].get('product', None), is_(None))
        assert_that(dg[0].get('variables', None), is_([var1]))

    def test_GIVEN_info_command_WHEN_files_and_many_vars_present_THEN_many_variable_and_empty_product(self):
        var1, var2 = 'rain', 'snow'
        args = ["info", var1 + "," + var2 + ':' + self.escaped_test_directory_files[0]]
        main_args = parse_args(args)
        dg = main_args.datagroups
        assert_that(len(dg), is_(1))
        assert_that(dg[0]['filenames'], is_([self.test_directory_files[0]]))
        assert_that(dg[0].get('product', None), is_(None))
        assert_that(dg[0].get('variables', None), contains_inanyorder('rain', 'snow'))

    def test_GIVEN_info_command_WHEN_files_and_var_and_product_present_THEN_variable_and_product_set(self):
        var1 = 'rain'
        product = 'cis'
        args = ["info", var1 + ':' + self.escaped_test_directory_files[0] + ':product=' + product]
        main_args = parse_args(args)
        dg = main_args.datagroups
        assert_that(len(dg), is_(1))
        assert_that(dg[0]['filenames'], is_([self.test_directory_files[0]]))
        assert_that(dg[0].get('product', None), is_('cis'))
        assert_that(dg[0].get('variables', None), is_([var1]))
