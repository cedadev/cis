import logging
import iris
from cis.data_io import gridded_data as gridded_data
from cis.data_io.products import AProduct


class NetCDF_Gridded(AProduct):
    def get_file_signature(self):
        # We don't know of any 'standard' netCDF CF model data yet...
        return [r'.*\.nc']

    @staticmethod
    def load_multiple_files_callback(cube, field, filename):
        # Static callback method for passing to iris when loading a single cube. To be implemented by subclasses as
        # needed
        pass

    @staticmethod
    def load_single_file_callback(cube, field, filename):
        # Static callback method for passing to iris when loading multiple cubes. To be implemented by subclasses as
        # needed
        pass

    def get_variable_names(self, filenames, data_type=None):
        import iris
        from cf_units import Unit
        from cis.utils import single_warnings_only

        variables = []

        # Filter the warnings so that they only appear once - otherwise you get lots of repeated warnings
        with single_warnings_only():
            cubes = iris.load(filenames)

        for cube in cubes:
            is_time_lat_lon_pressure_altitude_or_has_only_1_point = True
            for dim in cube.dim_coords:
                units = dim.units
                if dim.points.size > 1 and \
                        not units.is_time() and \
                        not units.is_time_reference() and \
                        not units.is_vertical() and \
                        not units.is_convertible(Unit('degrees')):
                    is_time_lat_lon_pressure_altitude_or_has_only_1_point = False
                    break
            if is_time_lat_lon_pressure_altitude_or_has_only_1_point:
                if cube.var_name:
                    variables.append(cube.var_name)
                else:
                    variables.append(cube.name())

        return set(variables)

    def create_coords(self, filenames, variable=None):
        """Reads the coordinates on which a variable depends.
        Note: This calls create_data_object because the coordinates are returned as a Cube.
        :param filenames: list of names of files from which to read coordinates
        :param variable: name of variable for which the coordinates are required
        (optional if file contains only one cube)
        :return: iris.cube.Cube
        """

        if variable is None:
            variable_names = self.get_variable_names(filenames)
            if len(variable_names) > 1:
                variable_name = str(variable_names.pop())
                logging.debug("Reading an IRIS Cube for the coordinates based on the variable %s" % variable_names)
            else:
                variable_name = None
        else:
            variable_name = variable

        return self.create_data_object(filenames, variable_name)

    def create_data_object(self, filenames, variable):
        """Reads the data for a variable.
        :param filenames: list of names of files from which to read data
        :param variable: (optional) name of variable; if None, the file(s) must contain data for only one cube
        :return: iris.cube.Cube
        """
        from cis.time_util import convert_cube_time_coord_to_standard_time
        from cis.utils import single_warnings_only

        # Filter the warnings so that they only appear once - otherwise you get lots of repeated warnings
        #  - partly because we open the files multiple times (to look for aux coords) and partly because iris
        #  will throw a warning every time it meets a variable with a non-CF dimension
        with single_warnings_only():
            cube = self._create_cube(filenames, variable)

        try:
            cube = convert_cube_time_coord_to_standard_time(cube)
        except iris.exceptions.CoordinateNotFoundError:
            pass
        return cube

    def get_file_format(self, filename):
        return "NetCDF/Gridded"

    def _create_cube(self, filenames, variable):
        """Creates a cube for the specified variable.
        :param filenames: List of filenames to read coordinates from
        :param variable: Optional variable to read while we're reading the coordinates, can be a string or a
        VariableConstraint object
        :return: If variable was specified this will return an UngriddedData object, otherwise a CoordList
        """
        from cis.exceptions import InvalidVariableError
        import six

        # Check if the files given actually exist.
        for filename in filenames:
            with open(filename) as f:
                pass

        variable_constraint = variable
        if isinstance(variable, six.string_types):
            variable_constraint = DisplayConstraint(cube_func=(lambda c: c.var_name == variable or
                                                               c.standard_name == variable or
                                                               c.long_name == variable), display=variable)
        if len(filenames) == 1:
            callback_function = self.load_single_file_callback
        else:
            callback_function = self.load_multiple_files_callback

        try:
            cube = gridded_data.load_cube(filenames, variable_constraint, callback=callback_function)
        except ValueError as e:
            if variable is None:
                message = "File contains more than one cube variable name must be specified"
            elif e.args[0] == "No cubes found":
                message = "Variable not found: {} \nTo see a list of variables run: cis info {}" \
                    .format(str(variable), filenames[0])
            else:
                message = e.args[0]
            raise InvalidVariableError(message)

        self._add_available_aux_coords(cube, filenames)

        return cube

    def _add_available_aux_coords(self, cube, filenames):
        """
        Add any altitude or pressure Auxiliary coordinates that IRIS does not load by default.
        :type cube: data_io.gridded_data.GriddedData
        :type filenames: list
        :return:
        """
        from iris.coords import AuxCoord

        def _make_aux_coord_and_dims_from_geopotential(g_cube):
            from scipy.constants import g
            points = g_cube.data / g
            dims = list(range(len(g_cube.shape)))
            coord = AuxCoord(points=points,
                             standard_name='altitude',
                             long_name='Geopotential height at layer midpoints',
                             var_name='altitude',
                             units='meter',
                             attributes={'positive': 'up'})
            return coord, dims

        def _make_aux_coord_and_dims_from_geopotential_height(g_ht_cube):
            dims = list(range(len(g_ht_cube.shape)))
            coord = AuxCoord(points=g_ht_cube.data,
                             standard_name='altitude',
                             long_name='Geopotential height at layer midpoints',
                             var_name='altitude',
                             units='meter',
                             attributes={'positive': 'up'})
            return coord, dims

        def _make_aux_coord_and_dims_from_air_pressure(aps_cube):
            dims = list(range(len(aps_cube.shape)))
            coord = AuxCoord(points=aps_cube.data,
                             standard_name='air_pressure',
                             long_name='Air Pressure',
                             var_name='air_pressure',
                             units='Pa')
            return coord, dims

        aux_coord_creation_functions = {'geopotential': _make_aux_coord_and_dims_from_geopotential,
                                        'geopotential_height': _make_aux_coord_and_dims_from_geopotential_height,
                                        'air_pressure': _make_aux_coord_and_dims_from_air_pressure}

        for standard_name, make_aux_coord in list(aux_coord_creation_functions.items()):
            constraint = DisplayConstraint(cube_func=lambda c: c.standard_name == standard_name,
                                           display=standard_name)
            try:
                aux_cube = gridded_data.load_cube(filenames, constraint)
                aux_coord, dims = make_aux_coord(aux_cube)
                cube.add_aux_coord(aux_coord, dims)
            except ValueError:
                pass  # The field doesn't exist; that's OK we just won't add it.


class DisplayConstraint(iris.Constraint):
    """Variant of iris.Constraint with a string value that can be displayed.
    """

    def __init__(self, *args, **kwargs):
        sc_kwargs = kwargs.copy()
        self.display = str(sc_kwargs.get('display', None))
        if self.display is not None:
            del sc_kwargs['display']
        super(DisplayConstraint, self).__init__(*args, **sc_kwargs)

    def __str__(self):
        if self.display is not None:
            return self.display
        else:
            return super(DisplayConstraint, self).__str__()
