import numpy

from jasmin_cis.cis import __version__


class Calculator(object):
    """
    Class to perform arithmetic calculations on sets of data.
    """

    SAFE_BUILTINS = ['abs', 'all', 'any', 'bool', 'cmp', 'divmod', 'enumerate', 'filter', 'int', 'len', 'map', 'max',
                     'min', 'pow', 'range', 'reduce', 'reversed', 'round', 'sorted', 'sum', 'xrange', 'zip']
    SAFE_MODULES = ['numpy']

    def evaluate(self, data_list, expr):
        """
        Evaluate a given expression over a list of data to produce an output data
        :param data_list: List of data used in the evaluation (these will be identified by alias or var_name).
        Should all be of the same data type and shape.
        :param expr: String python expression to evaluate.
        :return: Data object matching the type of the input data (i.e. GriddedData or UngriddedData).
        """
        if '__' in expr:
            raise ValueError("Use of functions or variables with double underscores (__) is not allowed")
        # Create list of allowed globals
        safe_globals = {module: globals()[module] for module in self.SAFE_MODULES}
        # Add allowed modules (should already be imported into current namespace)
        safe_globals['__builtins__'] = {var: globals()['__builtins__'][var] for var in self.SAFE_BUILTINS}
        safe_locals = {}
        for var in data_list:
            assert isinstance(var.alias, str)
            assert isinstance(var.data, numpy.ndarray)
            safe_locals[var.alias] = var.data
        result = eval(expr, safe_globals, safe_locals)
        return self._post_process(data_list, result, expr)

    def _post_process(self, data_list, result_array, expr):
        """
        Take sample data and the resultant output array, combine them and add appropriate metadata.
        :param data_list: The original sample data
        :param result_array: The calculated output array
        :param expr: The expression used to calculate the output
        :return: Post processed data object (GriddedData, UngriddedData or Cube)
        """
        var_name = 'calculated_variable'
        standard_name = None
        long_name = 'Calculated value for expression "%s"' % expr
        history = self._make_history(data_list, expr)
        units = 'unknown'

        # Use the first item from the data list as we assume that:
        # - The coordinates are all the same
        # - The shape is all the same
        sample_data = data_list[0]
        if not sample_data.data.shape == result_array.shape:
            raise ValueError("The resulting array is not the same shape as the original data. Check your expression")
        return sample_data.make_new_with_same_coordinates(data=result_array, var_name=var_name,
                                                          standard_name=standard_name, long_name=long_name,
                                                          history=history, units=units)

    def _make_history(self, data_list, expr):
        """
        Generate the history string
        :param data_list: List of data used in calculation
        :param expr: Expression using in calculation
        :return: History string
        """
        var_info = self._make_var_info(data_list)
        history_template = "Evaluated using CIS version {version}\n" + \
                           "Expression evaluated: '{expr}'\n" + \
                           "with variables: {var_info}."
        return history_template.format(version=__version__, expr=expr, var_info=var_info)

    def _make_var_info(self, data_list):
        """
        Get the variable info part of the history string, containing info
        about the variable names, aliases used and filenames.
        :param data_list: List of data used in calculation.
        :return: Var info string
        """
        var_infos = []
        var_info_tmpl = "'{var_name}'{alias} from files {files}"
        for var in data_list:
            alias = ''
            # If the alias is defaulting to the var_name then it probably hasn't been set
            if var.alias != var.var_name:
                alias = " (as '%s')" % var.alias
            var_info = var_info_tmpl.format(var_name=var.var_name, alias=alias, files=var.filenames)
            var_infos.append(var_info)
        return ",\n".join(var_infos)