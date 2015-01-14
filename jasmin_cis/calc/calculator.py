import numpy


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
        :param data_list: List of data used in the evaluation (these will be identified by var_name). Should all be of
        the same data type and shape.
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
            assert isinstance(var.var_name, str)
            assert isinstance(var.data, numpy.ndarray)
            safe_locals[var.var_name] = var.data
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
        history = ''  # TODO add history (need filenames)
        units = 'unknown'

        # Use the first item from the data list as we assume that:
        # - The coordinates are all the same
        # - The shape is all the same

        sample_data = data_list[0]  # TODO create copy (this changes original)
        if not sample_data.data.shape == result_array.shape:
            raise ValueError("The resulting array is not the same shape as the original data. Check your expression")
        sample_data.data = result_array
        try:
            sample_data.var_name = var_name
        except AttributeError:
            sample_data.metadata._name = var_name
        sample_data.standard_name = standard_name
        sample_data.long_name = long_name
        sample_data.history = history
        sample_data.units = units

        return sample_data
