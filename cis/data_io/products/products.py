import logging
import iris
from iris.cube import Cube
from iris.coords import DimCoord, AuxCoord
from cis.data_io.products.AProduct import AProduct


class cis(AProduct):
    # If a file matches the CIS product signature as well as another signature (e.g. because we aggregated from another
    # data product) we need to prioritise the CIS data product
    # TODO This probably shouldn't be needed, consider a pull-request to Iris to automatically as AuxCoords
    priority = 100

    def get_file_signature(self):
        return [r'.*\.nc']

    def create_data_object(self, filenames, variable):
        from cis.data_io.netcdf import read_many_files_individually, get_metadata
        from cis.exceptions import InvalidVariableError

        variables = [("longitude", "x"), ("latitude", "y"), ("altitude", "z"), ("air_pressure", "p")]

        logging.info("Listing coordinates: " + str(variables))

        aux_coords = []
        for variable in variables:
            try:
                var_data = read_many_files_individually(filenames, variable[0])[variable[0]]
                # TODO think about how to deal with the Axis attribute
                aux_coords.append((AuxCoord(var_data, **get_metadata(var_data[0])), 0))
            except InvalidVariableError:
                pass

        # Note - We don't need to convert this time coord as it should have been written in our
        #  'standard' time unit

        usr_var = iris.load_cube(filenames, variable)
        usr_var.add_aux_coords(aux_coords)

        return usr_var

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
        return [r'.*\.lev20']

    def create_data_object(self, filenames, variable):
        from cis.data_io.aeronet import load_multiple_aeronet
        from cis.time_util import cis_standard_time_unit as ct

        data = load_multiple_aeronet(filenames, [variable])

        # The name is text before any brackets, the units is what's after it (minus the closing bracket)
        name_units = variable.split('(')
        name = name_units[0]
        # For Aeronet we can assume that if there are no units then it is unitless (AOT, Angstrom exponent, etc)
        units = name_units[1][:-1] if len(name_units) > 1 else '1'

        aux_coords = []
        aux_coords.append((AuxCoord(data['longitude'], standard_name="longitude"), 0))
        aux_coords.append((AuxCoord(data['latitude'], standard_name="latitude"), 0))
        aux_coords.append((AuxCoord(data['altitude'], standard_name="altitude"), 0))
        time_coord = DimCoord(data["datetime"], standard_name='time', units=ct)

        # TODO Check that the missing values get masked properly

        cube = Cube(data[variable], var_name=name, long_name=variable, units=units,
                    aux_coords_and_dims=aux_coords, dim_coords_and_dims=[(time_coord, 0)])
        return cube
