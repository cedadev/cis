import logging
from jasmin_cis.data_io.Coord import CoordList
from jasmin_cis.data_io.products.AProduct import AProduct
from jasmin_cis.data_io.ungridded_data import UngriddedCoordinates, UngriddedData


class abstract_NetCDF_CF(AProduct):
    """
    Abstract data product class for NetCDF CF compliant files
    """

    def get_file_signature(self):
        # We don't know of any 'standard' netCDF CF data yet...
        return []

    def create_coords(self, filenames, variable=None):
        from jasmin_cis.data_io.netcdf import read_many_files, get_metadata
        from jasmin_cis.data_io.Coord import Coord

        variables = ["latitude", "longitude", "altitude", "time"]
        logging.info("Listing coordinates: " + str(variables))

        if variable is not None:
            variables.append(variable)

        data_variables = read_many_files(filenames, variables)

        coords = CoordList()
        coords.append(Coord(data_variables["longitude"], get_metadata(data_variables["longitude"]), "X"))
        coords.append(Coord(data_variables["latitude"], get_metadata(data_variables["latitude"]), "Y"))
        coords.append(Coord(data_variables["altitude"], get_metadata(data_variables["altitude"]), "Z"))
        coords.append(Coord(data_variables["time"], get_metadata(data_variables["time"]), "T"))

        if variable is None:
            return UngriddedCoordinates(coords)
        else:
            return UngriddedData(data_variables[variable], get_metadata(data_variables[variable]), coords)

    def create_data_object(self, filenames, variable):
        return self.create_coords(filenames, variable)