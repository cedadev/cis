import logging
import os

import numpy as np

from cis.data_io.Coord import CoordList
from cis.exceptions import InvalidVariableError, FileFormatError
from cis.data_io.products import AProduct
from cis.data_io.ungridded_data import UngriddedCoordinates, UngriddedData, Metadata
from cis.utils import add_to_list_if_not_none, dimensions_compatible, listify
from cis.data_io.netcdf import get_metadata, get_netcdf_file_attributes, read_many_files_individually, \
    get_netcdf_file_variables


class NCAR_NetCDF_RAF_variable_name_selector(object):
    """
    NCAR-RAF file definition: for the purposes of this data product
        It is a NetCDF file
        It contains attributes and variables
        The attributes must contain the following:
            an attribute GASSP_Version
            or an attribute Conventions with the value "NCAR-RAF/nimbus"

    This should successful differentiate the names of the variables for the various dimensions in NCAR-RAF and GASSP.
    The variables set are:
    station: True if this is for a fixed station data, False otherwise
    station_latitude: the latitude of the station (set only if station is true)
    station_longitude: the longitude of the station (set only if station is true)
    altitude: Altitude of the measurement if it is fixed, none if this is not fixed, defaults to DEFAULT_ALTITUDE
    time_variable_name: variable name for time
    latitude_variable_name: variable name of the latitude, None if fixed
    longitude_variable_name: variable name of the longitude, None if fixed
    altitude_variable_name: variable name of the altitude, None if fixed
    pressure_variable_name: variable name of the pressure, None if not included in data
    time_stamp_info: time stamp info if included, None otherwise

    The choice are in order of preference:
    Aeroplane GASSP (Data with time, lat, lon and altitude vars)
    Ship GASSP (Data with time, lat and lon vars but fixed altitude)
    Station GASSP (Data with time vars but fixed lat, lon and altitude)
    NCAR-RAF: (Data with time, lat, lon and altitude, but names are defined in coordinates attribute)
    """

    # Attribute name for the attribute holding the time coordinate
    TIME_COORDINATE_NAME = 'Time_Coordinate'
    # Attribute name for the attribute holding the latitude coordinate
    LATITUDE_COORDINATE_NAME = 'Latitude_Coordinate'
    # Attribute name for the attribute holding the longitude coordinate
    LONGITUDE_COORDINATE_NAME = 'Longitude_Coordinate'
    # Attribute name for the attribute holding the altitude or vertical coordinate
    ALTITUDE_COORDINATE_NAME = 'Vertical_Coordinate'
    # Variable name for the dataset for corrected pressure
    CORRECTED_PRESSURE_VAR_NAME = 'PSXC'
    # Variable name for the dataset for pressure
    PRESSURE_VAR_NAME = 'PRE'
    # Attribute name for the attribute holding the names of the best coordinates to use for lon, lat, alt and time
    BEST_COORDINATES_NAME = 'Coordinates'
    # Attribute name for the attribute holding the stations latitude
    STATION_LATITUDE_NAME = 'Station_Lat'
    # Attribute name for the attribute holding the stations longitude
    STATION_LONGITUDE_NAME = 'Station_Lon'
    # Attribute name for the attribute holding the stations altitude
    STATION_ALTITUDE_NAME = 'Station_Altitude'
    # Attribute name for the attribute holding the time stamp info (this is used for where time is measured from
    TIME_STAMP_INFO_NAME = 'Time_Stamp_Info'
    # The default altitude to use if it is not set, for instance ship based GASSP does not contain altitude
    DEFAULT_ALTITUDE = 0

    def __init__(self, attributes, variables):
        """
        Initialisation
        :param attributes: dictionary of attributes and their values (or list of dictionarys if multiple files read)
        :param variables: dictionary of variable names and NetCDF Variable objects
        (or list of dictionarys if multiple files read)
        :return: nothing
        """
        self.station = False
        self.station_latitude = None
        self.latitude_variable_name = None
        self.station_longitude = None
        self.longitude_variable_name = None
        self.altitude = None
        self.altitude_variable_name = None
        self.pressure_variable_name = None
        self.time_stamp_info = None
        self.time_dimensions = None

        self._attributes = [{k.lower(): v for k, v in list(attrs.items())} for attrs in listify(attributes)]
        if len(variables) == 0:
            raise InvalidVariableError("No variables in the file so the type of data is unknown")
        self._variables = list(variables[0].keys())
        self._variable_dimensions = [{name: var.dimensions for name, var in list(vars.items())}
                                     for vars in listify(variables)]
        self._check_has_variables_and_attributes()

        # Carry out these checks using the attributes from the first file as a 'master'
        if self.TIME_COORDINATE_NAME.lower() in self._attributes[0]:
            self.time_variable_name = self._get_coordinate_variable_name(self.TIME_COORDINATE_NAME, "time")

            if self.LATITUDE_COORDINATE_NAME.lower() in self._attributes[0]:
                self._lat_lon_var_specified_setup()
            elif self.STATION_LATITUDE_NAME.lower() in self._attributes[0]:
                self._stationary_setup()
            else:
                raise InvalidVariableError("No attributes indicating latitude, expecting '{}' or '{}'"
                                           .format(self.STATION_LATITUDE_NAME, self.LONGITUDE_COORDINATE_NAME))
        elif self.BEST_COORDINATES_NAME.lower() in self._attributes[0]:
            self._best_coordinates_setup()
        else:
            raise InvalidVariableError(
                "No attributes indicating time variable name, expecting either '{}' or 'Coordinates'"
                .format(self.TIME_COORDINATE_NAME))

        if self.CORRECTED_PRESSURE_VAR_NAME in self._variables:
            self.pressure_variable_name = self.CORRECTED_PRESSURE_VAR_NAME
        elif self.PRESSURE_VAR_NAME in self._variables:
            self.pressure_variable_name = self.PRESSURE_VAR_NAME
        else:
            self.pressure_variable_name = None

        if self.TIME_STAMP_INFO_NAME.lower() in self._attributes[0]:
            # Not all files will have the same timestamp -> Retrieve a list of timestamps for each file.
            self.time_stamp_info = [attrs[self.TIME_STAMP_INFO_NAME.lower()] for attrs in self._attributes]

        self.time_dimensions = self._variable_dimensions[0][self.time_variable_name]

    def _get_coordinate_variable_name(self, attribute_name, coordinate_display_name):
        """
        Reads an attribute value for a co-ordinate and returns the value. Checks that value is a variables in the data
        Throws InvalidVariableError if the attribute or variable does not exist
        :param attribute_name: the name of the attribute to read
        :param coordinate_display_name: the display name of the attribute read
        :return: the variable name
        """
        if attribute_name.lower() in self._attributes[0]:
            variable_name = self._attributes[0][attribute_name.lower()]
            if variable_name not in self._variables:  # Just check the first file
                raise InvalidVariableError("There is no variable for the {} co-ordinate '{}'"
                                           .format(coordinate_display_name, variable_name))
            return variable_name

        raise InvalidVariableError(
            "No attributes indicating {} variable name, expecting '{}'"
            .format(coordinate_display_name, attribute_name))

    def _parse_station_altitude(self, altitude_string):
        """
        Parse a station's altitude string. Will try and read it directly as a float, then will try and read the first
        white-space separated part of the string (e.g. '80 m asl' -> float(80)), finally sets the default altitude and
        logs a warning indicating this.
        :param altitude_string:
        :return:
        """
        try:
            return float(altitude_string)
        except ValueError:
            try:
                return float(altitude_string.split()[0])
            except ValueError:
                logging.warning("Couldn't parse station altitude attribute '{alt_string}'. Using default altitude "
                                "({default}m)".format(alt_string=altitude_string, default=self.DEFAULT_ALTITUDE))
                return self.DEFAULT_ALTITUDE

    @staticmethod
    def _parse_station_lat_lon(lat_lon_string):
        """
        Parse a station's latitude or longitude string. Will try and read it directly as a float, otherwise will try and
         read the first white-space separated part of the string (e.g. '80 degrees north' -> float(80)).
        :param lat_lon_string:
        :return:
        """
        from cis.exceptions import InvalidVariableError
        try:
            return float(lat_lon_string)
        except ValueError:
            try:
                return float(lat_lon_string.split()[0])
            except ValueError:
                raise InvalidVariableError("Couldn't parse station attribute '{}'".format(lat_lon_string))

    def _stationary_setup(self):
        """
        Set up object when latitude and longitude are fixed
        """
        from cis.exceptions import InvalidVariableError
        if self.STATION_LATITUDE_NAME.lower() not in self._attributes[0]:
            raise InvalidVariableError("No attributes indicating latitude, expecting '{}'"
                                       .format(self.STATION_LATITUDE_NAME))
        # We need a bunch of different latitudes for different files
        self.station_latitude = [self._parse_station_lat_lon(attr[self.STATION_LATITUDE_NAME.lower()])
                                 for attr in self._attributes]

        if self.STATION_LONGITUDE_NAME.lower() not in self._attributes[0]:
            raise InvalidVariableError("No attributes indicating longitude, expecting '{}'"
                                       .format(self.STATION_LONGITUDE_NAME))
        self.station_longitude = [self._parse_station_lat_lon(attr[self.STATION_LONGITUDE_NAME.lower()])
                                  for attr in self._attributes]
        self.station = True

        if self.STATION_ALTITUDE_NAME.lower() in self._attributes[0]:
            self.altitude = [self._parse_station_altitude(attr[self.STATION_ALTITUDE_NAME.lower()])
                             for attr in self._attributes]
        else:
            self.altitude = [self.DEFAULT_ALTITUDE for attr in self._attributes]

    def _check_has_variables_and_attributes(self):
        """
        Check that netcdf file has variables and attributes
        """
        if self._variables is None or len(self._variables) == 0:
            raise InvalidVariableError("No variables in the file so the type of data is unknown")
        if self._attributes[0] is None or len(self._attributes[0]) == 0:
            raise InvalidVariableError("No attributes in the file so type of data is unknown")

    def _lat_lon_var_specified_setup(self):
        """
        Set up object when latitude and longitude variables are being used
        """

        self.latitude_variable_name = self._get_coordinate_variable_name(self.LATITUDE_COORDINATE_NAME, "latitude")
        self.longitude_variable_name = self._get_coordinate_variable_name(self.LONGITUDE_COORDINATE_NAME, "longitude")

        if self.ALTITUDE_COORDINATE_NAME.lower() in self._attributes[0]:
            self.altitude_variable_name = self._get_coordinate_variable_name(self.ALTITUDE_COORDINATE_NAME, "vertical")
        else:
            self.altitude = [self.DEFAULT_ALTITUDE for attr in self._attributes]

    def _best_coordinates_setup(self):
        """
        Set up object when coordinates attribute is found
        """
        coordinates_vars = []
        coordinates = self._attributes[0][self.BEST_COORDINATES_NAME.lower()]
        if coordinates is not None:
            coordinates_vars = coordinates.split()  # split on whitespace

        if len(coordinates_vars) != 4:
            raise InvalidVariableError('The coordinate attribute does not have four entries. '
                                       'It should be space separated "longitude latitude altitude time"')

        for coordinates_var in coordinates_vars:
            if coordinates_var not in self._variables:
                raise InvalidVariableError("There is no variable for the co-ordinate '{}'".format(coordinates_var))

        self.longitude_variable_name, \
            self.latitude_variable_name, \
            self.altitude_variable_name, \
            self.time_variable_name \
            = coordinates_vars

    def find_auxiliary_coordinate(self, variable):
        """
        Find the variable name of an auxiliary coordinate for the given variable (if there is one).

        :param str variable: The data variable we're checking for any auxiliary coordinates
        :return str or None: The name of the variable holding the auxiliary coordinate or None
        """
        aux_coord_name = None
        dim_coord_names = [self.latitude_variable_name, self.longitude_variable_name,
                           self.altitude_variable_name, self.pressure_variable_name] + list(self.time_dimensions)
        # Find the *dimension* which corresponds to the auxiliary coordinate
        aux_coords = [dim for dim in self._variable_dimensions[0][variable] if dim not in dim_coord_names]
        if len(aux_coords) > 1:
            raise InvalidVariableError("CIS currently only supports reading data variables with one auxilliary "
                                       "coordinate")
        elif len(aux_coords) == 1:
            # If there is also a variable named after that dimension then this is the variable we're after
            if aux_coords[0] in self._variable_dimensions[0]:
                aux_coord_name = aux_coords[0]
            # Otherwise we need to look through all the variables and choose the first variable whose dimension is only
            #  the auxiliary dimension.
            else:
                for v, dims in self._variable_dimensions[0].items():
                    if dims[0] == aux_coords[0]:
                        aux_coord_name = v
                        break
        return aux_coord_name

    def get_variable_names_which_have_time_coord(self):
        variables = []
        for name, dimensions in list(self._variable_dimensions[0].items()):
            if len(dimensions) > 0 and dimensions_compatible(dimensions, self.time_dimensions):
                variables.append(name)
        return set(variables)


class NCAR_NetCDF_RAF(AProduct):
    """
    Data product for NCAR-RAF NetCDF files. This includes the subset of GASSP (which is its major use case)
    """

    # Set the priority to be higher than the other netcdf file types
    priority = 20

    # Name of the attribute in GASSP that defines the GASSP version
    GASSP_VERSION_ATTRIBUTE_NAME = "GASSP_Version"

    # Name of the attribute in NCAR_RAF that defines the converntion
    NCAR_RAF_CONVENTIONS_ATTRIBUTE_NAME = "Conventions"
    # Known NCAR RAF Converntions
    NCAR_RAF_KNOWN_CONVENTION = "NCAR-RAF/nimbus"
    # NCAR RAF Convention version name
    NCAR_RAF_CONVENTION_VERSION_ATTRIBUTE_NAME = "ConventionsVersion"

    def __init__(self, variable_selector_class=NCAR_NetCDF_RAF_variable_name_selector):
        """
        Setup NCAR RAF data product, allow a different variable selector class if needed
        :param variable_selector_class: the class to use for variable selection
        :return:nothing
        """
        super(NCAR_NetCDF_RAF, self).__init__()
        self.variableSelectorClass = variable_selector_class
        self.valid_dimensions = ["Time"]

    def get_file_signature(self):
        """
        Get the filename possibilities allowed for NCAR-RAF data
        :return: list of regular expressions for ncar raf data
        """
        return [r'.*\.nc$']

    def _get_file_format(self, filename):
        """
        Get the file type and any errors
        :param filename: the filename to read the type of
        :return: filetype
        :raises: FileFormatError if there is an error
        """
        if not os.path.isfile(filename):
            raise FileFormatError(["File does not exist"])
        try:
            attributes = get_netcdf_file_attributes(filename)
        except (RuntimeError, IOError) as ex:
            raise FileFormatError(["File is unreadable", ex.args[0]])

        attributes_lower = {attr.lower(): val for attr, val in list(attributes.items())}
        if self.GASSP_VERSION_ATTRIBUTE_NAME.lower() in attributes_lower:
            file_type = "NetCDF/GASSP/{}".format(attributes_lower[self.GASSP_VERSION_ATTRIBUTE_NAME.lower()])

        elif self.NCAR_RAF_CONVENTIONS_ATTRIBUTE_NAME.lower() in attributes_lower:
            ncarraf_convention = attributes_lower[self.NCAR_RAF_CONVENTIONS_ATTRIBUTE_NAME.lower()]
            version = ""
            if self.NCAR_RAF_CONVENTION_VERSION_ATTRIBUTE_NAME.lower() in attributes_lower:
                version = "/{}".format(attributes_lower[self.NCAR_RAF_CONVENTION_VERSION_ATTRIBUTE_NAME.lower()])
            if not ncarraf_convention == self.NCAR_RAF_KNOWN_CONVENTION:
                raise FileFormatError(["NCAR-RAF convention unknown, expecting '{}' was '{}'"
                                      .format(self.NCAR_RAF_KNOWN_CONVENTION, ncarraf_convention)])
            file_type = "NetCDF/{}{}".format(ncarraf_convention, version)

        else:
            raise FileFormatError(["File does not appear to be NCAR RAF or GASSP. No attributes for either '{}' or '{}'"
                                  .format(self.GASSP_VERSION_ATTRIBUTE_NAME, self.NCAR_RAF_CONVENTIONS_ATTRIBUTE_NAME)])

        return file_type

    def get_file_type_error(self, filename):
        """
        Test that the file is of the correct signature
        :param filename: the file name for the file
        :return: list fo errors or None
        """
        try:
            self._get_file_format(filename)
            return None
        except FileFormatError as ex:
            return ex.error_list

    def _load_data_definition(self, filenames):
        """
        Load the definition of the data
        :param filenames: filenames from which to load the data
        :return: variable selector containing the data definitions
        """
        variables_list = [get_netcdf_file_variables(f) for f in filenames]
        attributes = [get_netcdf_file_attributes(f) for f in filenames]

        variable_selector = self.variableSelectorClass(attributes, variables_list)
        return variable_selector

    def _load_data(self, filenames, variable):
        """
        Open the file and find the correct variables to load in
        :param filenames: the filenames to load
        :param variable: an extra variable to load
        :return: a list of load data and the variable selector used to load name it
        """

        variable_selector = self._load_data_definition(filenames)

        variables_list = [variable_selector.time_variable_name]
        add_to_list_if_not_none(variable_selector.latitude_variable_name, variables_list)
        add_to_list_if_not_none(variable_selector.longitude_variable_name, variables_list)
        add_to_list_if_not_none(variable_selector.altitude_variable_name, variables_list)
        add_to_list_if_not_none(variable_selector.pressure_variable_name, variables_list)

        logging.info("Listing coordinates: " + str(variables_list))
        add_to_list_if_not_none(variable, variables_list)

        data_variables = read_many_files_individually(filenames, variables_list)

        return data_variables, variable_selector

    def _create_coordinates_list(self, data_variables, variable_selector):
        """
        Create a co-ordinate list for the data
        :param data_variables: the load data
        :param variable_selector: the variable selector for the data
        :return: a list of coordinates
        """
        coords = CoordList()

        # Time
        time_coord = self._create_time_coord(variable_selector.time_stamp_info, variable_selector.time_variable_name,
                                             data_variables)
        coords.append(time_coord)

        # Lat and Lon
        # Multiple points counts for multiple files
        points_count = [np.product(var.shape) for var in data_variables[variable_selector.time_variable_name]]
        if variable_selector.station:
            lat_coord = self._create_fixed_value_coord("Y", variable_selector.station_latitude, "degrees_north",
                                                       points_count, "latitude")
            lon_coord = self._create_fixed_value_coord("X", variable_selector.station_longitude, "degrees_east",
                                                       points_count, "longitude")
        else:
            lat_coord = self._create_coord("Y", variable_selector.latitude_variable_name, data_variables, "latitude")
            lon_coord = self._create_coord("X", variable_selector.longitude_variable_name, data_variables, "longitude")
        coords.append(lat_coord)
        coords.append(lon_coord)

        # Altitude
        if variable_selector.altitude is None:
            altitude_coord = self._create_coord("Z", variable_selector.altitude_variable_name, data_variables,
                                                "altitude")
        else:
            altitude_coord = self._create_fixed_value_coord("Z", variable_selector.altitude, "meters", points_count,
                                                            "altitude")
        coords.append(altitude_coord)

        # Pressure
        if variable_selector.pressure_variable_name is not None:
            coords.append(
                self._create_coord("P", variable_selector.pressure_variable_name, data_variables, "air_pressure"))
        return coords

    @staticmethod
    def _add_aux_coordinate(dim_coords, filename, aux_coord_name, length):
        """
        Add an auxiliary coordinate to a list of (reshaped) dimension coordinates

        :param dim_coords: CoordList of one-dimensional coordinates representing physical dimensions
        :param filename: The data file containing the aux coord
        :param aux_coord_name: The name of the aux coord to add to the coord list
        :param length: The length of the data dimensions which this auxiliary coordinate should span
        :return: A CoordList of reshaped (2D) physical coordinates plus the 2D auxiliary coordinate
        """
        from cis.data_io.Coord import Coord
        from cis.utils import expand_1d_to_2d_array
        from cis.data_io.netcdf import read

        # We assume that the auxilliary coordinate is the same shape across files
        d = read(filename, [aux_coord_name])[aux_coord_name]
        # Reshape to the length given
        aux_data = expand_1d_to_2d_array(d[:], length, axis=0)
        # Get the length of the auxiliary coordinate
        len_y = d[:].size

        for dim_coord in dim_coords:
            dim_coord.data = expand_1d_to_2d_array(dim_coord.data, len_y, axis=1)

        all_coords = dim_coords + [Coord(aux_data, get_metadata(d))]

        return all_coords

    def create_coords(self, filenames, variable=None):
        """
        Reads the coordinates and data if required from the files
        :param filenames: List of filenames to read coordinates from
        :param variable: load a variable for the data
        :return: Coordinates
        """
        data_variables, variable_selector = self._load_data(filenames, variable)

        dim_coords = self._create_coordinates_list(data_variables, variable_selector)

        if variable is None:
            return UngriddedCoordinates(dim_coords)
        else:
            aux_coord_name = variable_selector.find_auxiliary_coordinate(variable)
            if aux_coord_name is not None:
                all_coords = self._add_aux_coordinate(dim_coords, filenames[0], aux_coord_name,
                                                      dim_coords.get_coord(standard_name='time').data.size)
            else:
                all_coords = dim_coords
            return UngriddedData(data_variables[variable], get_metadata(data_variables[variable][0]), all_coords)

    def create_data_object(self, filenames, variable):
        """
        Load the variable with it coordinates from the files
        :param filenames: filenames of the file
        :param variable: the variable to load
        :return: Data object
        """
        return self.create_coords(filenames, variable)

    def _create_coord(self, coord_axis, data_variable_name, data_variables, standard_name):
        """
        Create a coordinate for the co-ordinate list
        :param coord_axis: axis of the coordinate in the coords
        :param data_variable_name: the name of the variable in the data
        :param data_variables: the data variables
        :param standard_name: the standard name it should have
        :return: a coords object
        """
        from cis.data_io.Coord import Coord

        coordinate_data_objects = []
        for d in data_variables[data_variable_name]:
            m = get_metadata(d)
            m.standard_name = standard_name
            coordinate_data_objects.append(Coord(d, m, coord_axis))

        return Coord.from_many_coordinates(coordinate_data_objects)

    def _create_time_coord(self, timestamp, time_variable_name, data_variables, coord_axis='T', standard_name='time'):
        """
        Create a time coordinate, taking into account the fact that each file may have a different timestamp.
        :param timestamp: Timestamp or list of timestamps for
        :param time_variable_name: Name of the time variable
        :param data_variables: Dictionary containing one or multiple netCDF data variables for each variable name
        :param coord_axis: Axis, default 'T'
        :param standard_name: Coord standard name, default 'time'
        :return: Coordinate
        """
        from cis.data_io.Coord import Coord
        from six.moves import zip_longest

        timestamps = listify(timestamp)
        time_variables = data_variables[time_variable_name]
        time_coords = []
        # Create a coordinate for each separate file to account for differing timestamps
        for file_time_var, timestamp in zip_longest(time_variables, timestamps):
            metadata = get_metadata(file_time_var)
            metadata.standard_name = standard_name
            coord = Coord(file_time_var, metadata, coord_axis)
            coord.convert_to_std_time(timestamp)
            time_coords.append(coord)

        return Coord.from_many_coordinates(time_coords)

    def _create_fixed_value_coord(self, coord_axis, values, coord_units, points_counts, coord_name):
        """
        Create a coordinate with a fixed value
        :param coord_axis: Axis of the coordinate in the coords
        :param coord_name: The name of the coordinate
        :param coord_units: The units for the coordinate
        :param points_counts: Number of points for this coordinate, or list of sizes for multiple files
        :param values: Value of coordinate, or list of values for multiple files
        :return:
        """
        from cis.data_io.Coord import Coord

        values = listify(values)
        points_counts = listify(points_counts)
        all_points = np.array([])
        # Create separate arrays with values and sizes corresponding to each of the different input files.
        for value, points_count in zip(values, points_counts):
            file_points = np.ma.array(np.zeros(points_count) + float(value))
            all_points = np.append(all_points, file_points)
        metadata = Metadata(name=coord_name, shape=all_points.shape, units=coord_units,
                            range=(min(values), max(values)))
        return Coord(all_points, metadata, coord_axis)

    def get_variable_names(self, filenames, data_type=None):
        """
        Get a list of available variable names
        This can be overridden in specific products to improve on this
        """

        selector = self._load_data_definition(filenames)
        return selector.get_variable_names_which_have_time_coord()

    def get_file_format(self, filename):
        """
        Return the file format, in general this string is parent format/specific instance/version
        e.g. NetCDF/GASSP/1.0
        :param str filename: Filename of a an example file from the dataset
        :return: File format, of the form parent format/specific instance/version
        :rtype: str
        :raises: FileFormatError if files type is not determinable
        """
        return self._get_file_format(filename)
