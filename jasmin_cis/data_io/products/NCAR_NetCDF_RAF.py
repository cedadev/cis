import logging
from data_io.Coord import CoordList
from jasmin_cis.data_io.products.abstract_NetCDF_CF import abstract_NetCDF_CF
from data_io.ungridded_data import UngriddedCoordinates, UngriddedData


class NCAR_NetCDF_RAF(abstract_NetCDF_CF):
    """
    Data product for NCAR-RAF NetCDF files. This includes the subset of GASSP (which is its major use case)
    """

    def get_file_signature(self):
        return [r'.*\.nc']

    def create_coords(self, filenames, variable=None):
        from jasmin_cis.data_io.netcdf import read_many_files, get_metadata
        from jasmin_cis.data_io.Coord import Coord

        variables = ["LATC", "LONC", "GGALTC", "Time", "PSXC"]
        logging.info("Listing coordinates: " + str(variables))

        if variable is not None:
            variables.append(variable)

        data_variables = read_many_files(filenames, variables, dim='Time')

        coords = CoordList()
        coords.append(Coord(data_variables["LATC"], get_metadata(data_variables["LATC"]), "Y"))
        coords.append(Coord(data_variables["LONC"], get_metadata(data_variables["LONC"]), "X"))
        coords.append(Coord(data_variables["GGALTC"], get_metadata(data_variables["GGALTC"]), "Z"))
        time_coord = Coord(data_variables["Time"], get_metadata(data_variables["Time"]), "T")
        time_coord.convert_to_std_time()
        coords.append(time_coord)
        coords.append(Coord(data_variables["PSXC"], get_metadata(data_variables["PSXC"]), "P"))

        if variable is None:
            return UngriddedCoordinates(coords)
        else:
            return UngriddedData(data_variables[variable], get_metadata(data_variables[variable]), coords)

    def create_data_object(self, filenames, variable):
        return self.create_coords(filenames, variable)