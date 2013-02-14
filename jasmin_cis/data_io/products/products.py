from data_io.Coord import Coord, CoordList
from data_io.products.AProduct import AProduct
from data_io.ungridded_data import UngriddedData
import jasmin_cis.utils as utils
import data_io.hdf as hdf

import logging

class Cloudsat_2B_CWC_RVOD(AProduct):

    def get_file_signature(self):
        return [r'.*2B.CWC.RVOD.*\.hdf']


    def create_coords(self, filenames):

        # list of coordinate variables we are interested in
        variables = [ 'Latitude','Longitude','TAI_start','Profile_time','Height']

        logging.debug("Listing coordinates: " + str(variables))

        # reading the various files
        sdata, vdata = hdf.read(filenames,variables)

        height = sdata['Height']
        height_data = hdf.read_data(height, "SD")
        height_metadata = hdf.read_metadata(height, "SD")
        height_coord = Coord(height_data, height_metadata,'Y')

        lat = vdata['Latitude']
        lat_data = utils.expand_1d_to_2d_array(hdf.read_data(lat, "VD"),len(height_data[1]),axis=1)
        lat_metadata = hdf.read_metadata(lat,"VD")
        lat_coord = Coord(lat_data, lat_metadata)

        lon = vdata['Longitude']
        lon_data = utils.expand_1d_to_2d_array(hdf.read_data(lon, "VD"),len(height_data[1]),axis=1)
        lon_metadata = hdf.read_metadata(lon, "VD")
        lon_coord = Coord(lon_data, lon_metadata)

        import data_io.hdf_vd as hdf_vd
        arrays = []
        for i,j in zip(vdata['Profile_time'],vdata['TAI_start']):
            time = hdf_vd.get_data(i)
            start = hdf_vd.get_data(j)
            time += start
            arrays.append(time)
        time_data = utils.concatenate(arrays)
        time_data = utils.expand_1d_to_2d_array(time_data,len(height_data[1]),axis=1)
        time_metadata = hdf.read_metadata(vdata['Profile_time'], "VD")
        time_coord = Coord(time_data, time_metadata,'X')

        return CoordList([lat_coord,lon_coord,height_coord,time_coord])

    def create_data_object(self, filenames, variable):

        logging.debug("Creating data object for variable " + variable)

        # reading coordinates
        coords = self.create_coords(filenames)

        # reading of variables
        sdata, vdata = hdf.read(filenames, variable)

        # retrieve data + its metadata
        var = sdata[variable]
        metadata = hdf.read_metadata(var,"SD")

        return UngriddedData(var,metadata,coords)

class MODIS_L2(AProduct):

    def get_file_signature(self):

        product_names = ['MYD06_L2','MOD06_L2','MYD04_L2','MYD04_L2','MYDATML2','MODATML2']
        regex_list = [ r'.*' + product + '.*\.hdf' for product in product_names]
        return regex_list


    def __field_interpolate(self,data,factor=5):
        '''
        Interpolates the given 2D field by the factor,
        edge pixels are defined by the ones in the centre,
        odd factords only!
        '''
        import numpy as np

        logging.debug("Performing interpolation...")

        output = np.zeros((factor*data.shape[0],factor*data.shape[1]))*np.nan
        output[int(factor/2)::factor,int(factor/2)::factor] = data
        for i in range(1,factor+1):
            output[(int(factor/2)+i):(-1*factor/2+1):factor,:] = i*((output[int(factor/2)+factor::factor,:]-output[int(factor/2):(-1*factor):factor,:])
                                                                    /float(factor))+output[int(factor/2):(-1*factor):factor,:]
        for i in range(1,factor+1):
            output[:,(int(factor/2)+i):(-1*factor/2+1):factor] = i*((output[:,int(factor/2)+factor::factor]-output[:,int(factor/2):(-1*factor):factor])
                                                                    /float(factor))+output[:,int(factor/2):(-1*factor):factor]
        return output


    def create_coords(self, filenames):

        variables = [ 'Latitude','Longitude','Scan_Start_Time']

        logging.debug("Listing coordinates: " + str(variables))

        sdata, vdata = hdf.read(filenames,variables)

        lat = sdata['Latitude']
        lat_data = self.__field_interpolate(hdf.read_data(lat,"SD"))
        #lat_data = hdf.read_data(lat,"SD")
        lat_metadata = hdf.read_metadata(lat, "SD")
        lat_coord = Coord(lat_data, lat_metadata,'Y')

        lon = sdata['Longitude']
        lon_data = self.__field_interpolate(hdf.read_data(lon,"SD"))
        #lon_data = hdf.read_data(lon,"SD")
        lon_metadata = hdf.read_metadata(lon,"SD")
        lon_coord = Coord(lon_data, lon_metadata,'X')

        return CoordList([lat_coord,lon_coord])

    def create_data_object(self, filenames, variable):

        logging.debug("Creating data object for variable " + variable)

        # reading coordinates
        coords = self.create_coords(filenames)

        # reading of variables
        sdata, vdata = hdf.read(filenames, variable)

        # retrieve data + its metadata
        var = sdata[variable]
        metadata = hdf.read_metadata(var, "SD")

        return UngriddedData(var, metadata, coords)


class Cloud_CCI(AProduct):

    def get_file_signature(self):
        return [r'.*ESACCI.*']

    def create_coords(self, filenames):

        from data_io.netcdf import read_many_files, get_metadata
        from data_io.Coord import Coord

        variables = ["lat", "lon", "time"]

        data = read_many_files(filenames, variables, dim="pixel_number")

        coords = CoordList()
        coords.append(Coord(data["lon"], get_metadata(data["lon"]), "X"))
        coords.append(Coord(data["lat"], get_metadata(data["lat"]), "Y"))
        coords.append(Coord(data["time"], get_metadata(data["time"]), "T"))
        
        return coords

    def create_data_object(self, filenames, variable):

        from data_io.netcdf import read_many_files, get_metadata

        coords = self.create_coords(filenames)
        data = read_many_files(filenames, variable, dim="pixel_number")
        metadata = get_metadata(data[variable])

        return UngriddedData(data[variable], metadata, coords)

class CisCol(AProduct):

    def get_file_signature(self):
        return [r'cis\-col\-.*\.nc']

    def create_coords(self, filenames, variable = None):
        from data_io.netcdf import read, get_metadata
        from data_io.Coord import Coord

        if variable is not None:
            var = read(filenames[0], variable)

        lon = read(filenames[0], "Longitude")
        lat = read(filenames[0], "Latitude")
        alt = read(filenames[0], "Height")
        time = read(filenames[0], "Profile_time")

        coords = CoordList()
        coords.append(Coord(lon, get_metadata(lon), "X"))
        coords.append(Coord(lat, get_metadata(lat), "Y"))
        coords.append(Coord(alt, get_metadata(alt), "Z"))
        coords.append(Coord(time, get_metadata(time), "T"))

        if variable is None:
            return coords
        else:
            return UngriddedData(var, get_metadata(var), coords)

    def create_data_object(self, filenames, variable):
        return self.create_coords(filenames, variable)

class NetCDF_CF(AProduct):

    def get_file_signature(self):
        return [r'.*\.nc']

    def create_coords(self, filenames, variable = None):
        from data_io.netcdf import read_many_files, get_metadata
        from data_io.Coord import Coord

        variables = [ "latitude", "longitude", "altitude", "time" ]

        if variable is not None:
            variables.append(variable)

        data_variables = read_many_files(filenames, variables)

        coords = CoordList()
        coords.append(Coord(data_variables["longitude"], get_metadata(data_variables["longitude"]), "X"))
        coords.append(Coord(data_variables["latitude"], get_metadata(data_variables["latitude"]), "Y"))
        coords.append(Coord(data_variables["altitude"], get_metadata(data_variables["altitude"]), "Z"))
        coords.append(Coord(data_variables["time"], get_metadata(data_variables["time"]), "T"))

        if variable is None:
            return coords
        else:
            return UngriddedData(data_variables[variable], get_metadata(data_variables[variable]), coords)

    def create_data_object(self, filenames, variable):
        return self.create_coords(filenames, variable)


class NetCDF_CF_Gridded(NetCDF_CF):

    def get_file_signature(self):
        # We don't know of any 'standard' netCDF CF model data yet...
        return []

    def create_coords(self, filenames, variable = None):
        # TODO Expand coordinates
        # For gridded data sets this will actually return coordinates which are too short
        #  we need to think about how to expand them here
        """

        @param filenames: List of filenames to read coordinates from
        @param variable: Optional variable to read while we're reading the coordinates
        @return: If variable was specified this will return an UngriddedData object, otherwise a CoordList
        """
        return super(NetCDF_CF_Gridded, self).create_coords(filenames, variable)


    def create_data_object(self, filenames, variable):
        """

        @param filenames: List of filenames to read coordinates from
        @param variable: Optional variable to read while we're reading the coordinates, can be a string or a VariableConstraint object
        @return: If variable was specified this will return an UngriddedData object, otherwise a CoordList
        """
        from jasmin_cis.exceptions import InvalidVariableError
        import iris

        try:
            cube = iris.load_cube(filenames, variable)
        except iris.exceptions.ConstraintMismatchError:
            raise InvalidVariableError("Variable not found: " + variable +
                                       "\nTo see a list of variables run: cis info " + filenames[0] + " -h")

        sub_cube = list(cube.slices([ coord for coord in cube.coords(dim_coords=True) if coord.points.size > 1]))[0]
        #  Ensure that there are no extra dimensions which can confuse the plotting.
        # E.g. the shape of the cube might be (1, 145, 165) and so we don't need to know about
        #  the dimension whose length is one. The above list comprehension would return a cube of
        #  shape (145, 165)

        return sub_cube

class Xglnwa(NetCDF_CF_Gridded):

    def get_file_signature(self):
        return [r'.*xglnwa.*\.nc']

    def create_coords(self, filenames, variable = None):
        # TODO Expand coordinates
        # For gridded data sets this will actually return coordinates which are too short
        #  we need to think about how to expand them here
        """

        @param filenames: List of filenames to read coordinates from
        @param variable: Optional variable to read while we're reading the coordinates
        @return: If variable was specified this will return an UngriddedData object, otherwise a CoordList
        """
        return super(Xglnwa, self).create_coords(filenames, variable)


    def create_data_object(self, filenames, variable):
        import iris.AttributeConstraint
        # In this case we use the variable as a name constraint as the variable names themselves aren't obvious
        var_constraint = iris.AttributeConstraint(name=variable)

        return super(Xglnwa, self).create_data_object(filenames, var_constraint)


class Xenida(NetCDF_CF_Gridded):

    def get_file_signature(self):
        return [r'.*xenida.*\.nc']

    def create_coords(self, filenames, variable=None):
        # TODO Expand coordinates
        # For gridded data sets this will actually return coordinates which are too short
        #  we need to think about how to expand them here
        """

        @param filenames: List of filenames to read coordinates from
        @param variable: Optional variable to read while we're reading the coordinates
        @return: If variable was specified this will return an UngriddedData object, otherwise a CoordList
        """
        from data_io.netcdf import read, get_metadata
        from data_io.Coord import Coord

        variables = [ "latitude", "longitude", "altitude", "time" ]

        data_variables = read(filenames[0], variables)

        coords = CoordList()
        coords.append(Coord(data_variables["longitude"], get_metadata(data_variables["longitude"]), "X"))
        coords.append(Coord(data_variables["latitude"], get_metadata(data_variables["latitude"]), "Y"))
        coords.append(Coord(data_variables["altitude"], get_metadata(data_variables["altitude"]), "Z"))
        coords.append(Coord(data_variables["time"], get_metadata(data_variables["time"]), "T"))

        return coords

    def create_data_object(self, filenames, variable):
        return super(Xenida, self).create_data_object(filenames, variable)

class Aeronet(AProduct):

    def get_file_signature(self):
        #TODO Update this
        return [r'.*\.lev20']

    def create_coords(self, filenames, data_obj = None):
        from data_io.ungridded_data import Metadata
        from numpy import array
        from data_io.aeronet import load_aeronet, get_file_metadata

        for filename in filenames:
            if data_obj is None:
                data_obj = load_aeronet(filename)
            metadata = get_file_metadata(filename)
            lon = metadata.misc[2][1].split("=")[1]
            lat = metadata.misc[2][2].split("=")[1]

            coords = CoordList()
            coords.append(Coord(array([lon]), Metadata(name="Longitude", shape=(1,), units="degrees_east", range=(-180,180), missing_value=-999)))
            coords.append(Coord(array([lat]), Metadata(name="Latitude", shape=(1,), units="degrees_north", range=(-90,90), missing_value=-999)))
            date_time_data = data_obj["datetime"]
            coords.append(Coord(date_time_data, Metadata(name="Date time", shape=(len(date_time_data),), units="Time_units"), "X"))

        return coords

    def create_data_object(self, filenames, variable):
        from data_io.aeronet import load_aeronet, get_file_metadata
        from jasmin_cis.exceptions import InvalidVariableError
        data = []
        filename = filenames[0]
        data_obj = load_aeronet(filename)
        try:
            var_data = data_obj[variable]
        except ValueError:
            raise InvalidVariableError(variable + " does not exist in file " + filename)
        metadata = get_file_metadata(filename, variable, (len(var_data),))
        return UngriddedData(var_data, metadata, self.create_coords([filename], data_obj))
