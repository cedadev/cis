import logging
from cis.data_io.Coord import Coord, CoordList
from cis.data_io.products.AProduct import AProduct
from cis.data_io.ungridded_data import UngriddedData, Metadata, UngriddedCoordinates
import cis.utils as utils


class cis(AProduct):
    # If a file matches the CIS product signature as well as another signature (e.g. because we aggregated from another
    # data product) we need to prioritise the CIS data product
    priority = 100

    def get_file_signature(self):
        return [r'.*\.nc']

    def create_coords(self, filenames, usr_variable=None):
        from cis.data_io.netcdf import read_many_files_individually, get_metadata, get_netcdf_file_variables
        from cis.data_io.Coord import Coord, CoordList
        from cis.data_io.ungridded_data import UngriddedCoordinates, UngriddedData
        from cis.exceptions import InvalidVariableError

        # We have to read it once first to find out which variables are in there. We assume the set of coordinates in
        # all the files are the same
        file_variables = get_netcdf_file_variables(filenames[0])

        axis_lookup = {"longitude": "x", 'latitude': 'y', 'altitude': 'z', 'time': 't', 'air_pressure': 'p'}

        coord_variables = [(v, axis_lookup[v]) for v in file_variables if v in axis_lookup]

        # Create a copy to contain all the variables to read
        all_variables = list(coord_variables)
        if usr_variable is not None:
            all_variables.append((usr_variable, ''))

        logging.info("Listing coordinates: " + str(all_variables))

        coords = CoordList()
        var_data = read_many_files_individually(filenames, [v[0] for v in all_variables])
        for name, axis in coord_variables:
            try:
                coords.append(Coord(var_data[name], get_metadata(var_data[name][0]), axis=axis))
            except InvalidVariableError:
                pass

        # Note - We don't need to convert this time coord as it should have been written in our
        #  'standard' time unit

        if usr_variable is None:
            res = UngriddedCoordinates(coords)
        else:
            res = UngriddedData(var_data[usr_variable], get_metadata(var_data[usr_variable][0]), coords)

        return res

    def create_data_object(self, filenames, variable):
        return self.create_coords(filenames, variable)

    def get_file_format(self, filename):
        return "NetCDF/CIS"

    def get_file_type_error(self, filename):
        """
        Test that the file is of the correct signature
        :param filename: the file name for the file
        :return: list fo errors or None
        """
        from cis.data_io.netcdf import get_netcdf_file_attributes
        atts = get_netcdf_file_attributes(filename)
        errors = None
        try:
            source = atts['source']
        except KeyError as ex:
            errors = ['No source attribute found in {}'.format(filename)]
        else:
            if not source.startswith('CIS'):
                errors = ['Source ({}) does not match CIS in {}'.format(source, filename)]
        return errors


class Aeronet(AProduct):
    def get_file_signature(self):
        return [r'.*\.lev20', r'.*\.ONEILL_lev20', r'.*\.ONEILL_20', r'.*\.lev15',
                r'.*\.ONEILL_lev15', r'.*\.ONEILL_15', r'.*All_Sites_Times.*dat',
                r'.*\.all']

    def _create_coord_list(self, filenames, data=None):
        from cis.data_io.ungridded_data import Metadata
        from cis.data_io.aeronet import load_multiple_aeronet
        from cis.time_util import cis_standard_time_unit as ct

        if data is None:
            data = load_multiple_aeronet(filenames)

        coords = CoordList()
        coords.append(Coord(data['longitude'], Metadata(name="Longitude", shape=(len(data),),
                                                        units="degrees_east", range=(-180, 180))))
        coords.append(Coord(data['latitude'], Metadata(name="Latitude", shape=(len(data),),
                                                       units="degrees_north", range=(-90, 90))))
        coords.append(Coord(data['altitude'], Metadata(name="Altitude", shape=(len(data),), units="meters")))
        coords.append(Coord(data["datetime"], Metadata(name="DateTime", standard_name='time', shape=(len(data),),
                                                       units=ct), "X"))

        return coords

    def create_coords(self, filenames, variable=None):
        return UngriddedCoordinates(self._create_coord_list(filenames))

    def create_data_object(self, filenames, variable):
        from cis.data_io.aeronet import load_multiple_aeronet

        data_obj = load_multiple_aeronet(filenames, [variable])

        coords = self._create_coord_list(filenames, data_obj)

        if variable[-1] == ')':
            # The name is text before any brackets, the units is what's after it (minus the closing bracket)
            name_units = variable.split('(')
            name = name_units[0]
            # For Aeronet we can assume that if there are no units then it is unitless (AOT, Angstrom exponent, etc)
            units = name_units[1][:-1] if len(name_units) > 1 else '1'
        else:
            # SDA variable names include () that don't specify units. Ignoring Exact_Wavelengths.
            name = variable
            units = '1'

        return UngriddedData(data_obj[variable],
                             Metadata(name=name, long_name=variable, shape=(len(data_obj),), units=units,
                                      missing_value=-999.0), coords)

    def get_variable_names(self, filenames, data_type=None):
        from cis.data_io.aeronet import get_aeronet_file_variables

        variables = []
        for filename in filenames:
            file_variables = get_aeronet_file_variables(filename)
            variables.extend(file_variables)
        return set(variables)

    def get_file_format(self, filename):
        from cis.data_io.aeronet import get_aeronet_version

        return "ASCII" + get_aeronet_version(filename)


class ASCII_Hyperpoints(AProduct):
    def get_file_signature(self):
        return [r'.*\.txt']

    def get_variable_names(self, filenames, data_type=None):
        return ['value']

    def create_coords(self, filenames, variable=None):
        from cis.data_io.ungridded_data import Metadata
        from numpy import genfromtxt, NaN
        from cis.exceptions import InvalidVariableError
        from cis.time_util import convert_datetime_to_std_time
        import dateutil.parser as du

        array_list = []

        for filename in filenames:
            try:
                array_list.append(genfromtxt(filename, dtype="f8,f8,f8,O,f8",
                                             names=['latitude', 'longitude', 'altitude', 'time', 'value'],
                                             delimiter=',', missing_values='', usemask=True, invalid_raise=True,
                                             converters={"time": du.parse}))
            except:
                raise IOError('Unable to read file ' + filename)

        data_array = utils.concatenate(array_list)
        n_elements = len(data_array['latitude'])

        coords = CoordList()
        coords.append(Coord(data_array["latitude"],
                            Metadata(standard_name="latitude", shape=(n_elements,), units="degrees_north")))
        coords.append(Coord(data_array["longitude"],
                            Metadata(standard_name="longitude", shape=(n_elements,), units="degrees_east")))
        coords.append(
            Coord(data_array["altitude"], Metadata(standard_name="altitude", shape=(n_elements,), units="meters")))

        time_arr = convert_datetime_to_std_time(data_array["time"])
        time = Coord(time_arr,
                     Metadata(standard_name="time", shape=(n_elements,), units="days since 1600-01-01 00:00:00"))
        coords.append(time)

        if variable:
            try:
                data = UngriddedData(data_array['value'], Metadata(name="value", shape=(n_elements,), units="unknown",
                                                                   missing_value=NaN), coords)
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
