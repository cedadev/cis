import logging
import os
from jasmin_cis.data_io.Coord import CoordList
from jasmin_cis.exceptions import InvalidVariableError, FileFormatError
from jasmin_cis.data_io.products.abstract_NetCDF_CF import abstract_NetCDF_CF
from jasmin_cis.data_io.ungridded_data import UngriddedCoordinates, UngriddedData, Metadata
from jasmin_cis.utils import add_to_list_if_not_none, dimensions_equal
import numpy as np
from jasmin_cis.data_io.netcdf import read_many_files, get_metadata, read_attributes_and_variables_many_files, \
    get_netcdf_file_attributes
from jasmin_cis.data_io.Coord import Coord


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
    aggregation_dimensions: dimension over which variables should be aggregated when reading multiple files

    The choice are in order of preference:
    Aeroplane GASSP (Data with time, lat, lon and altitude vars)
    Ship GASSP (Data with time, lat and lon vars but fixed altitude)
    Station GASSP (Data with time vars but fixed lat, lon and altitude)
    NCAR-RAF: (Data with time, lat, lon and altitude, but names are defined in coordinates attribute)
    """

    #attribute name for the attribute holding the time coordinate
    TIME_COORDINATE_NAME = 'Time_Coordinate'
    #attribute name for the attribute holding the latitude coordinate
    LATITUDE_COORDINATE_NAME = 'Latitude_Coordinate'
    #attribute name for the attribute holding the longitude coordinate
    LONGITUDE_COORDINATE_NAME = 'Longitude_Coordinate'
    #attribute name for the attribute holding the altitude or vertical coordinate
    ALTITUDE_COORDINATE_NAME = 'Vertical_Coordinate'
    #variable name for the dataset for corrected pressure
    CORRECTED_PRESSURE_VAR_NAME = 'PSXC'
    #variable name for the dataset for pressure
    PRESSURE_VAR_NAME = 'PRE'
    #attribute name for the attribute holding the names of the best coordinates to use for lon, lat, alt and time
    BEST_COORDINATES_NAME = 'Coordinates'
    #attribute name for the attribute holding the stations latitude
    STATION_LATITUDE_NAME = 'Station_Lat'
    #attribute name for the attribute holding the stations longitude
    STATION_LONGITUDE_NAME = 'Station_Lon'
    #attribute name for the attribute holding the stations altitude
    STATION_ALTITUDE_NAME = 'Station_Altitude'
    #attribute name for the attribute holding the time stamp info (this is used for where time is measured from
    TIME_STAMP_INFO_NAME = 'Time_Stamp_Info'
    #the default altitude to use if it is not set, for instance ship based GASSP does not contain altitude
    DEFAULT_ALTITUDE = 0

    def __init__(self, attributes, variables, variable_dimensions):
        """
        Initialisation
        :param attributes: dictionary of attributes and their values
        :param variables: list of variable names
        :param variable_dimensions: a dictionary of the dimensions of each variable
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
        self.aggregation_dimensions = None
        self.time_dimensions = None

        self._attributes = {k.lower(): v for k, v in attributes.items()}
        self._variables = variables
        self._variable_dimensions = variable_dimensions
        self._check_have_variables_and_attribure()

        if self.TIME_COORDINATE_NAME.lower() in self._attributes:
            self.time_variable_name = self._get_coordinate_variable_name(self.TIME_COORDINATE_NAME, "time")

            if self.LATITUDE_COORDINATE_NAME.lower() in self._attributes:
                self._lat_lon_var_specified_setup()
            elif self.STATION_LATITUDE_NAME.lower() in self._attributes:
                self._stationary_setup()
            else:
                raise InvalidVariableError("No attributes indicating latitude, expecting '{}' or '{}'"
                                           .format(self.STATION_LATITUDE_NAME, self.LONGITUDE_COORDINATE_NAME))
        elif self.BEST_COORDINATES_NAME.lower() in self._attributes:
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

        if self.TIME_STAMP_INFO_NAME.lower() in self._attributes:
            self.time_stamp_info = self._attributes[self.TIME_STAMP_INFO_NAME.lower()]

        self.time_dimensions = self._variable_dimensions[self.time_variable_name]
        self.aggregation_dimensions = self.time_dimensions[0]

    def _get_coordinate_variable_name(self, attribute_name, coordinate_display_name):
        """
        Reads an attribute value for a co-ordinate and returns the value. Checks that value is a variables in the data
        Throws InvalidVariableError if the attribute or variable does not exist
        :param attribute_name: the name of the attribute to read
        :param coordinate_display_name: the display name of the attribute read
        :returns: the variable name
        """
        if attribute_name.lower() in self._attributes:
            variable_name = self._attributes[attribute_name.lower()]
            if variable_name not in self._variables:
                raise InvalidVariableError("There is no variable for the {} co-ordinate '{}'"
                                           .format(coordinate_display_name, variable_name))
            return variable_name

        raise InvalidVariableError(
            "No attributes indicating {} variable name, expecting '{}'"
            .format(coordinate_display_name, attribute_name))

    def _stationary_setup(self):
        """
        Set up object when latitude and longitude are fixed
        """
        if self.STATION_LATITUDE_NAME.lower() not in self._attributes:
            raise InvalidVariableError("No attributes indicating latitude, expecting '{}'"
                                       .format(self.STATION_LATITUDE_NAME))
        self.station_latitude = self._attributes[self.STATION_LATITUDE_NAME.lower()]

        if self.STATION_LONGITUDE_NAME.lower() not in self._attributes:
            raise InvalidVariableError("No attributes indicating longitude, expecting '{}'"
                                       .format(self.STATION_LONGITUDE_NAME))
        self.station_longitude = self._attributes[self.STATION_LONGITUDE_NAME.lower()]
        self.station = True

        if self.STATION_ALTITUDE_NAME.lower() in self._attributes:
            self.altitude = self._attributes[self.STATION_ALTITUDE_NAME.lower()]
        else:
            self.altitude = self.DEFAULT_ALTITUDE

    def _check_have_variables_and_attribure(self):
        """
        Check that netcdf file has variables and attributes
        """
        if self._variables is None or len(self._variables) == 0:
            raise InvalidVariableError("No variables in the file so the type of data is unknown")
        if self._attributes is None or len(self._attributes) == 0:
            raise InvalidVariableError("No attributes in the file so type of data is unknown")

    def _lat_lon_var_specified_setup(self):
        """
        Set up object when latitude and longitude variables are being used
        """

        self.latitude_variable_name = self._get_coordinate_variable_name(self.LATITUDE_COORDINATE_NAME, "latitude")
        self.longitude_variable_name = self._get_coordinate_variable_name(self.LONGITUDE_COORDINATE_NAME, "longitude")

        if self.ALTITUDE_COORDINATE_NAME.lower() in self._attributes:
            self.altitude_variable_name = self._get_coordinate_variable_name(self.ALTITUDE_COORDINATE_NAME, "vertical")
        else:
            self.altitude = self.DEFAULT_ALTITUDE

    def _best_coordinates_setup(self):
        """
        Set up object when coordinates attribute is found
        """
        coordinates_vars = []
        coordinates = self._attributes[self.BEST_COORDINATES_NAME.lower()]
        if coordinates is not None:
            coordinates_vars = coordinates.split()  # split on whitespace

        if len(coordinates_vars) is not 4:
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

    def get_variable_names_with_same_dimensions_as_time_coord(self):
        variables = []
        for name, dimensions in self._variable_dimensions.items():
            if dimensions_equal(dimensions, self.time_dimensions):
                variables.append(name)
        return set(variables)

class NCAR_NetCDF_RAF(abstract_NetCDF_CF):
    """
    Data product for NCAR-RAF NetCDF files. This includes the subset of GASSP (which is its major use case)
    """

    #set the priority to be higher than the other netcdf file types
    priority = 20

    #name of the attribute in GASSP that defines the GASSP version
    GASSP_VERSION_ATTRIBUTE_NAME = "GASSP_Version"

    #name of the attribute in NCAR_RAF that defines the converntion
    NCAR_RAF_CONVENTIONS_ATTRIBUTE_NAME = "Conventions"
    #known NCAR RAF Converntions
    NCAR_RAF_KNOWN_CONVENTION = "NCAR-RAF/nimbus"
    #NCAR RAF Convention version name
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
        except RuntimeError as ex:
            raise FileFormatError(["File is unreadable", ex.message])

        attributes_lower = {attr.lower(): val for attr, val in attributes.items()}
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
        attributes, variables_list, variable_dimensions = read_attributes_and_variables_many_files(filenames)
        variable_selector = self.variableSelectorClass(attributes, variables_list, variable_dimensions)
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

        data_variables = read_many_files(filenames, variables_list, dim=variable_selector.aggregation_dimensions)

        return data_variables, variable_selector

    def _create_coordinates_list(self, data_variables, variable_selector):
        """
        Create a co-ordinate list for the data
        :param data_variables: the load data
        :param variable_selector: the variable selector for the data
        :return: a list of coordinates
        """
        coords = CoordList()

        #Time
        time_coord = self._create_coord("T", variable_selector.time_variable_name, data_variables, "time")
        time_coord.convert_to_std_time(variable_selector.time_stamp_info)
        coords.append(time_coord)

        #Lat and Lon
        points_count = np.product(data_variables[variable_selector.time_variable_name].shape)
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

        #Altitude
        if variable_selector.altitude is None:
            altitude_coord = self._create_coord("Z", variable_selector.altitude_variable_name, data_variables,
                                                "altitude")
        else:
            altitude_coord = self._create_fixed_value_coord("Z", variable_selector.altitude, "meters", points_count,
                                                            "altitude")
        coords.append(altitude_coord)

        #Pressure
        if variable_selector.pressure_variable_name is not None:
            coords.append(
                self._create_coord("P", variable_selector.pressure_variable_name, data_variables, "air_pressure"))
        return coords

    def create_coords(self, filenames, variable=None):
        """
        Reads the coordinates and data if required from the files
        :param filenames: List of filenames to read coordinates from
        :param variable: load a variable for the data
        :return: Coordinates
        """
        data_variables, variable_selector = self._load_data(filenames, variable)

        coords = self._create_coordinates_list(data_variables, variable_selector)

        if variable is None:
            return UngriddedCoordinates(coords)
        else:
            return UngriddedData(data_variables[variable], get_metadata(data_variables[variable]), coords)

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
        from jasmin_cis.data_io.netcdf import get_metadata
        from jasmin_cis.data_io.Coord import Coord

        data_variable = data_variables[data_variable_name]
        metadata = get_metadata(data_variable)
        metadata.alter_standard_name(standard_name)
        return Coord(data_variable, metadata, coord_axis)

    def _create_fixed_value_coord(self, coord_axis, value, coord_units, points_count, coord_name):
        """
        Create a coordinate with a fixed value
        :param coord_axis: axis of the coordinate in the coords
        :param coord_name: the name of the coordinate
        :param coord_units: the units for the coordinate
        :param points_count: number of points
        :param value: the value of the coordinate
        :return:
        """
        coordinate_value = float(value)
        data_variable = np.ma.array(np.zeros(points_count) + coordinate_value)
        metadata = Metadata(name=coord_name, shape=(points_count,), units=coord_units,
                            range=(coordinate_value, coordinate_value))
        return Coord(data_variable, metadata, coord_axis)

    def get_variable_names(self, filenames, data_type=None):
        """
        Get a list of available variable names
        This can be overridden in specific products to improve on this
        """

        selector = self._load_data_definition(filenames)
        return selector.get_variable_names_with_same_dimensions_as_time_coord()

    def get_file_format(self, filenames):
        """
        Return the file format, in general this string is parent format/specific instance/version
        e.g. NetCDF/GASSP/1.0
        :param filenames: filenames of files that make up the dataset
        :returns: file format, of the form parent format/specific instance/version, if there is not a specific fileformat
        for the data product returns the data product name
        :raises: FileFormatError if files type is not determinable
        """
        return self._get_file_format(filenames)