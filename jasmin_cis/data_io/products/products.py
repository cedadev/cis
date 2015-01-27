import logging

import iris
import iris.exceptions

from jasmin_cis.data_io.products.abstract_NetCDF_CF import abstract_NetCDF_CF

from jasmin_cis.exceptions import InvalidVariableError, CoordinateNotFoundError
from jasmin_cis.data_io.Coord import Coord, CoordList
from jasmin_cis.data_io.products.AProduct import AProduct
from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata, UngriddedCoordinates
import jasmin_cis.data_io.gridded_data as gridded_data
import jasmin_cis.utils as utils
import jasmin_cis.data_io.hdf as hdf


class CloudSat(AProduct):

    def get_file_signature(self):
        return [r'.*_CS_.*GRANULE.*\.hdf']

    def get_variable_names(self, filenames, data_type=None):
        from pyhdf.HDF import HDF
        from pyhdf.SD import SD

        valid_variables = set([])
        for filename in filenames:
            # Do VD variables
            datafile = HDF(filename)
            vdata = datafile.vstart()
            variables = vdata.vdatainfo()
            # Assumes that latitude shape == longitude shape (it should):
            dim_length = [var[3] for var in variables if var[0] == 'Latitude'][0]
            for var in variables:
                if var[3] == dim_length:
                    valid_variables.add(var[0])

            # Do SD variables:
            sd = SD(filename)
            datasets = sd.datasets()
            if 'Height' in datasets:
                valid_shape = datasets['Height'][1]
                for var in datasets:
                    if datasets[var][1] == valid_shape:
                        valid_variables.add(var)

        return valid_variables

    def _generate_time_array(self, vdata):
        import jasmin_cis.data_io.hdf_vd as hdf_vd
        import datetime as dt
        from jasmin_cis.time_util import convert_sec_since_to_std_time_array

        Cloudsat_start_time = dt.datetime(1993,1,1,0,0,0)

        arrays = []
        for i,j in zip(vdata['Profile_time'],vdata['TAI_start']):
            time = hdf_vd.get_data(i)
            start = hdf_vd.get_data(j)
            time += start
            # Do the conversion to standard time here before we expand the time array...
            time = convert_sec_since_to_std_time_array(time, Cloudsat_start_time)
            arrays.append(time)
        return utils.concatenate(arrays)

    def _create_coord_list(self, filenames):
        from jasmin_cis.time_util import cis_standard_time_unit
        # list of coordinate variables we are interested in
        variables = ['Latitude', 'Longitude', 'TAI_start', 'Profile_time', 'Height']

        # reading the various files
        try:
            logging.info("Listing coordinates: " + str(variables))
            sdata, vdata = hdf.read(filenames, variables)

            # altitude coordinate
            height = sdata['Height']
            height_data = hdf.read_data(height, "SD")
            height_metadata = hdf.read_metadata(height, "SD")
            height_coord = Coord(height_data, height_metadata, "Y")

        except InvalidVariableError:
            # This means we are reading a Cloudsat file without height, so remove height from the variables list
            variables.remove('Height')
            logging.info("Listing coordinates: " + str(variables))
            sdata, vdata = hdf.read(filenames, variables)

            height_data = None
            height_coord = None

        # latitude
        lat = vdata['Latitude']
        lat_data = hdf.read_data(lat, "VD")
        if height_data is not None:
            lat_data = utils.expand_1d_to_2d_array(lat_data, len(height_data[0]), axis=1)
        lat_metadata = hdf.read_metadata(lat,"VD")
        lat_metadata.shape = lat_data.shape
        lat_coord = Coord(lat_data, lat_metadata)

        # longitude
        lon = vdata['Longitude']
        lon_data = hdf.read_data(lon, "VD")
        if height_data is not None:
            lon_data = utils.expand_1d_to_2d_array(lon_data, len(height_data[0]), axis=1)
        lon_metadata = hdf.read_metadata(lon, "VD")
        lon_metadata.shape = lon_data.shape
        lon_coord = Coord(lon_data, lon_metadata)

        # time coordinate
        time_data = self._generate_time_array(vdata)
        if height_data is not None:
            time_data = utils.expand_1d_to_2d_array(time_data, len(height_data[0]), axis=1)
        time_coord = Coord(time_data,Metadata(name='Profile_time', standard_name='time', shape=time_data.shape,
                                              units=str(cis_standard_time_unit),
                                              calendar=cis_standard_time_unit.calendar),"X")


        # create object containing list of coordinates
        coords = CoordList()
        coords.append(lat_coord)
        coords.append(lon_coord)
        if height_coord is not None:
            coords.append(height_coord)
        coords.append(time_coord)

        return coords

    def create_coords(self, filenames, variable=None):
        return UngriddedCoordinates(self._create_coord_list(filenames))

    def create_data_object(self, filenames, variable):

        logging.debug("Creating data object for variable " + variable)

        # reading coordinates
        coords = self._create_coord_list(filenames)

        # reading of variables
        sdata, vdata = hdf.read(filenames, variable)

        #missing values
        missing_values = [0,-9999,-4444,-3333]

        # retrieve data + its metadata
        if variable in vdata:
            # vdata should be expanded in the same way as the coordinates are expanded
            try:
                height_length = coords.get_coord('Height').shape[1]
                var = utils.expand_1d_to_2d_array(hdf.read_data(vdata[variable], "VD", missing_values),
                                                  height_length, axis=1)
            except CoordinateNotFoundError:
                var = hdf.read_data(vdata[variable], "VD", missing_values)
            metadata = hdf.read_metadata(vdata[variable],"VD")
        elif variable in sdata:
            var = hdf.read_data(sdata[variable], "SD",missing_values)
            metadata = hdf.read_metadata(sdata[variable],"SD")
        else:
            raise ValueError("variable not found")

        return UngriddedData(var,metadata,coords)

    def get_file_format(self, filenames):
        """
        Get the file format
        :param filenames:
        :return:
        """

        return "HDF4/CloudSat"


class cis(AProduct):

    # If a file matches the CIS product signature as well as another signature (e.g. because we aggregated from another
    # data product) we need to prioritise the CIS data product
    priority = 100

    def get_file_signature(self):
        return [r'cis\-.*\.nc']

    def create_coords(self, filenames, usr_variable=None):
        from jasmin_cis.data_io.netcdf import read_many_files_individually, get_metadata
        from jasmin_cis.data_io.Coord import Coord
        from jasmin_cis.exceptions import InvalidVariableError

        variables = [("longitude", "x"), ("latitude", "y"), ("altitude", "z"), ("time", "t"), ("air_pressure", "p")]

        logging.info("Listing coordinates: " + str(variables))

        coords = CoordList()
        for variable in variables:
            try:
                var_data = read_many_files_individually(filenames,variable[0])[variable[0]]
                coords.append(Coord(var_data, get_metadata(var_data[0]),axis=variable[1]))
            except InvalidVariableError:
                pass

        # Note - We don't need to convert this time coord as it should have been written in our
        #  'standard' time unit

        if usr_variable is None:
            res = UngriddedCoordinates(coords)
        else:
            usr_var_data = read_many_files_individually(filenames,usr_variable)[usr_variable]
            res = UngriddedData(usr_var_data, get_metadata(usr_var_data[0]), coords)

        return res

    def create_data_object(self, filenames, variable):
        return self.create_coords(filenames, variable)

    def get_file_format(self, filenames):
        """
        Get the file format
        :param filenames:
        :return:
        """

        return "NetCDF/CIS"


class abstract_NetCDF_CF_Gridded(abstract_NetCDF_CF):

    def get_file_signature(self):
        # We don't know of any 'standard' netCDF CF model data yet...
        return []

    def get_variable_names(self, filenames, data_type=None):
        import iris
        import iris.unit as unit
        variables = []
        cubes = iris.load(filenames)

        for cube in cubes:
            is_time_lat_lon_pressure_altitude_or_has_only_1_point = True
            for dim in cube.dim_coords:
                units = dim.units
                if dim.points.size > 1 and \
                    not units.is_time() and \
                    not units.is_time_reference() and \
                    not units.is_vertical() and \
                    not units.is_convertible(unit.Unit('degrees')):
                    is_time_lat_lon_pressure_altitude_or_has_only_1_point = False
                    break
            if is_time_lat_lon_pressure_altitude_or_has_only_1_point:
                variables.append(cube.var_name)

        return set(variables)

    def create_coords(self, filenames, variable=None):
        """Reads the coordinates on which a variable depends.
        Note: This calls create_data_object because the coordinates are returned as a Cube.
        :param filenames: list of names of files from which to read coordinates
        :param variable: name of variable for which the coordinates are required (if file contains more than one use
        the first varible)
        :return: iris.cube.Cube
        """

        if variable is None:

            variable_names = self.get_variable_names(filenames)
            if len(variable_names) > 1:
                variable_name = str(variable_names.pop())
            else:
                variable_name = None
        else:
            variable_name = variable
        return self._create_cube(filenames, variable_name, False)

    def create_data_object(self, filenames, variable):
        """

        :param filenames: List of filenames to read coordinates from
        :param variable: Optional variable to read while we're reading the coordinates, can be a string or a VariableConstraint object
        :return: If variable was specified this will return an UngriddedData object, otherwise a CoordList
        """
        return self._create_cube(filenames, variable, True)

    def _create_cube(self, filenames, variable, remove_length_one_dimensions):
        """Creates a cube for the specified variable.
        :param filenames: List of filenames to read coordinates from
        :param variable: Optional variable to read while we're reading the coordinates, can be a string or a VariableConstraint object
        :return: If variable was specified this will return an UngriddedData object, otherwise a CoordList
        """
        from jasmin_cis.exceptions import InvalidVariableError

        # Check if the files given actually exist.
        for filename in filenames:
            with open(filename) as f: pass

        variable_constraint = variable
        if isinstance(variable, basestring):
            variable_constraint = DisplayConstraint(cube_func=(lambda c: c.var_name == variable or
                                                                         c.standard_name == variable or
                                                                         c.long_name == variable), display=variable)

        try:
            cube = gridded_data.load_cube(filenames, variable_constraint)
        except iris.exceptions.ConstraintMismatchError:
            if variable is None:
                message = "File contains more than one cube variable name must be specified"
            else:
                message = "Variable not found: {} \nTo see a list of variables run: cis info {}"\
                    .format(str(variable), filenames[0])
            raise InvalidVariableError(message)
        except ValueError as e:
            raise IOError(str(e))

        # Fix to create a hybrid pressure factory in Iris. More attempts may be required for different file types. This
        # should be removed once the relevant Iris issue is resolved https://github.com/SciTools/iris/issues/933.
        try:
            cube.add_aux_factory(iris.aux_factory.HybridPressureFactory(
                cube.coord(var_name="hyam"), cube.coord(var_name="hybm"), cube.coord(var_name="PS")))
        except iris.exceptions.CoordinateNotFoundError:
            pass

        sub_cube = list(cube.slices([ coord for coord in cube.coords(dim_coords=True) if coord.points.size > 1]))[0]
        #  Ensure that there are no extra dimensions which can confuse the plotting.
        # E.g. the shape of the cube might be (1, 145, 165) and so we don't need to know about
        #  the dimension whose length is one. The above list comprehension would return a cube of
        #  shape (145, 165)

        return sub_cube


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


class NetCDF_Gridded(abstract_NetCDF_CF_Gridded):
    """Reads gridded netCDF identifying variable by variable name.
    """
    def get_file_signature(self):
        # Generic product class so no signature.
        return []

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
        from jasmin_cis.time_util import convert_cube_time_coord_to_standard_time

        cube = super(NetCDF_Gridded, self).create_data_object(filenames, variable)

        try:
            cube = convert_cube_time_coord_to_standard_time(cube)
        except iris.exceptions.CoordinateNotFoundError:
            pass
        return cube

    def get_file_format(self, filenames):
        """
        Returns the file format
        """
        return "NetCDF/Gridded"


class Aeronet(AProduct):

    def get_file_signature(self):
        return [r'.*\.lev20']

    def _create_coord_list(self, filenames, data=None):
        from jasmin_cis.data_io.ungridded_data import Metadata
        from jasmin_cis.data_io.aeronet import load_multiple_aeronet

        if data is None:
            data = load_multiple_aeronet(filenames)

        coords = CoordList()
        coords.append(Coord(data['longitude'], Metadata(name="Longitude", shape=(len(data),),
                                                        units="degrees_east", range=(-180, 180))))
        coords.append(Coord(data['latitude'], Metadata(name="Latitude", shape=(len(data),),
                                                       units="degrees_north", range=(-90, 90))))
        coords.append(Coord(data['altitude'], Metadata(name="Altitude", shape=(len(data),), units="meters")))
        time_coord = Coord(data["datetime"], Metadata(name="DateTime", standard_name='time', shape=(len(data),),
                                                      units="DateTime Object"), "X")
        time_coord.convert_datetime_to_standard_time()
        coords.append(time_coord)

        return coords

    def create_coords(self, filenames, variable=None):
        return UngriddedCoordinates(self._create_coord_list(filenames))

    def create_data_object(self, filenames, variable):
        from jasmin_cis.data_io.aeronet import load_multiple_aeronet
        from jasmin_cis.exceptions import InvalidVariableError

        try:
            data_obj = load_multiple_aeronet(filenames, [variable])
        except ValueError:
            raise InvalidVariableError(variable + " does not exist in " + str(filenames))

        coords = self._create_coord_list(filenames, data_obj)

        return UngriddedData(data_obj[variable],
                             Metadata(name=variable, long_name=variable, shape=(len(data_obj),), missing_value=-999.0),
                             coords)


class ASCII_Hyperpoints(AProduct):

    def get_file_signature(self):
        return [r'.*\.txt']

    def get_variable_names(self, filenames, data_type=None):
        return ['value']

    def create_coords(self, filenames, variable=None):
        from jasmin_cis.data_io.ungridded_data import Metadata
        from numpy import genfromtxt
        from jasmin_cis.exceptions import InvalidVariableError
        from jasmin_cis.time_util import parse_datetimestr_to_std_time_array

        array_list = []

        for filename in filenames:
            try:
                array_list.append(genfromtxt(filename, dtype="f8,f8,f8,S20,f8",
                                             names=['latitude', 'longitude', 'altitude', 'time', 'value'],
                                             delimiter=',', missing_values='', usemask=True, invalid_raise=True))
            except:
                raise IOError('Unable to read file '+filename)

        data_array = utils.concatenate(array_list)
        n_elements = len(data_array['latitude'])

        coords = CoordList()
        coords.append(Coord(data_array["latitude"], Metadata(standard_name="latitude", shape=(n_elements,), units="degrees_north")))
        coords.append(Coord(data_array["longitude"], Metadata(standard_name="longitude", shape=(n_elements,), units="degrees_east")))
        coords.append(Coord(data_array["altitude"], Metadata(standard_name="altitude", shape=(n_elements,), units="meters")))

        time_arr = parse_datetimestr_to_std_time_array(data_array["time"])
        time = Coord(time_arr, Metadata(standard_name="time", shape=(n_elements,), units="days since 1600-01-01 00:00:00"))
        coords.append(time)

        if variable:
            try:
                data = UngriddedData(data_array['value'], Metadata(name="value", shape=(n_elements,), units="unknown"), coords)
            except:
                InvalidVariableError("Value column does not exist in file " + filenames)
            return data
        else:
            return UngriddedCoordinates(coords)

    def create_data_object(self, filenames, variable):
        return self.create_coords(filenames, True)

    def get_file_format(self, filenames):
        """
        Returns the file format
        """
        return "ASCII/ASCIIHyperpoints"

class default_NetCDF(NetCDF_Gridded):
    """
    This class should always be the last in the sorted list (last alphabetically) - and hence the default for *.nc
    files which have not otherwise been matched.
    """
    def get_file_signature(self):
        return [r'.*\.nc']
