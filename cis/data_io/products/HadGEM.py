from cis.data_io.products import NetCDF_Gridded


class HadGEM_CONVSH(NetCDF_Gridded):
    """
        HadGEM plugin for reading NetCDF files converted by CONVSH. It implements a callback to pass to iris when
        reading multiple files to allow correct merging
    """

    def get_file_signature(self):
        return [r'[a-z]{6}[\._][pamd]{2}[0-9]{4,6}.*\.nc']

    @staticmethod
    def load_multiple_files_callback(cube, field, filename):
        from iris.util import squeeze
        # We need to remove the history field when reading multiple files so that the cubes can be properly merged
        cube.attributes.pop('history')
        # cube.coord(name_or_coord='Hybrid height').attributes['formula_terms'] = 'a: lev b: b orog: orog'
        # We also need to remove the length one time dimension so that the cube can be merged correctly (iris preserves
        #  the value as a scalar which then gets converted back into a full coordinate again on merge).
        return squeeze(cube)

    def _create_cube(self, filenames, variable):
        """Creates a cube for the specified variable.
        :param filenames: List of filenames to read coordinates from
        :param variable: Optional variable to read while we're reading the coordinates, can be a string or a
        VariableConstraint object
        :return: If variable was specified this will return an UngriddedData object, otherwise a CoordList
        """
        from cis.exceptions import InvalidVariableError
        from cis.data_io.products.gridded_NetCDF import DisplayConstraint
        from cis.data_io.gridded_data import load_cube
        from iris.exceptions import ConstraintMismatchError, CoordinateNotFoundError

        # Check if the files given actually exist.
        for filename in filenames:
            with open(filename) as f:
                pass

        variable_constraint = variable
        if isinstance(variable, str):
            # noinspection PyPep8
            variable_constraint = DisplayConstraint(cube_func=(lambda c: c.var_name == variable or
                                                               c.standard_name == variable or
                                                               c.long_name == variable), display=variable)
        if len(filenames) == 1:
            callback_function = self.load_single_file_callback
        else:
            callback_function = self.load_multiple_files_callback

        try:
            cube = load_cube(filenames, variable_constraint, callback=callback_function)
        except ConstraintMismatchError as e:
            if variable is None:
                message = "File contains more than one cube variable name must be specified"
            elif e.message == "no cubes found":
                message = "Variable not found: {} \nTo see a list of variables run: cis info {}" \
                    .format(str(variable), filenames[0])
            else:
                message = e.message
            raise InvalidVariableError(message)
        except ValueError as e:
            raise IOError(str(e))

        try:
            hybrid_ht = cube.coord(name_or_coord='Hybrid height')
            hybrid_ht.attributes['formula'] = 'z(k,j,i) = a(k) + b(k)*orog(j,i)'
            hybrid_ht.convert_units('m')
        except CoordinateNotFoundError as e:
            pass

        try:
            cube.coord(long_name='t').standard_name = 'time'
        except CoordinateNotFoundError as e:
            pass

        self._add_available_aux_coords(cube, filenames)

        return cube

    def get_variable_names(self, filenames, data_type=None):
        # Don't do any checks on valid variables at the moment as iris can't parse the hybrid height dimension units...
        import iris
        cubes = iris.load(filenames)

        return set(cube.name() for cube in cubes)


class HadGEM_PP(NetCDF_Gridded):
    """
        HadGEM plugin for reading native pp files
    """

    def get_file_signature(self):
        return [r'.*\.pp']

    @staticmethod
    def load_multiple_files_callback(cube, field, filename):
        # This method sets the var_name (used for outputting the cube to NetCDF) to the cube name. This can be quite
        #  for some HadGEM variables but most commands allow the user to override this field on output.
        var_name = cube.name()
        cube.var_name = var_name

    @staticmethod
    def load_single_file_callback(cube, field, filename):
        # This method sets the var_name (used for outputting the cube to NetCDF) to the cube name. This can be quite
        #  for some HadGEM variables but most commands allow the user to override this field on output.
        var_name = cube.name()
        cube.var_name = var_name
