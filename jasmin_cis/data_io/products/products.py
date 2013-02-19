from data_io.Coord import Coord, CoordList
from data_io.products.AProduct import AProduct
from data_io.ungridded_data import UngriddedData
import jasmin_cis.utils as utils
import data_io.hdf as hdf

import logging

class Cloudsat_2B_CWC_RVOD(AProduct):

    def get_file_signature(self):
        return [r'.*2B.CWC.RVOD.*\.hdf']

    def __generate_real_time_coord(self, filenames, xsize, ysize):
        import numpy as np
        from os.path import basename
        from datetime import timedelta, time, datetime
        from iris.unit import date2julian_day, CALENDAR_STANDARD
        from data_io.ungridded_data import Metadata
        # Work out a 'rough' real time for the data - for use in colocation
        all_times = []
        for a_file in filenames:
            a_file = basename(a_file)
            year = a_file[0:4]
            day = a_file[4:7]
            t = a_file[7:13]
            #t = time(a_file[7:9],a_file[9:11],a_file[11:13])
            #time_array = np.zeros() +
            d = timedelta(days=int(day),seconds=int(a_file[11:13]),minutes=int(a_file[9:11]),hours=int(a_file[7:9]))
            dt = datetime(int(year),1,1)+d
            all_times.append(np.zeros((xsize, ysize)) + date2julian_day(dt, CALENDAR_STANDARD))
        time_data = utils.concatenate(all_times)
        real_time_coord = Coord(time_data, Metadata(name='time', standard_name='time', units='Julian days'))
        return real_time_coord

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
        lat_data = utils.expand_1d_to_2d_array(hdf.read_data(lat, "VD"),len(height_data[0]),axis=1)
        lat_metadata = hdf.read_metadata(lat,"VD")
        lat_coord = Coord(lat_data, lat_metadata, "X")

        lon = vdata['Longitude']
        lon_data = utils.expand_1d_to_2d_array(hdf.read_data(lon, "VD"),len(height_data[0]),axis=1)
        lon_metadata = hdf.read_metadata(lon, "VD")
        lon_coord = Coord(lon_data, lon_metadata)

        real_time_coord = self.__generate_real_time_coord(filenames, len(height_data[:,0]), len(height_data[0]))

        import data_io.hdf_vd as hdf_vd
        arrays = []
        for i,j in zip(vdata['Profile_time'],vdata['TAI_start']):
            time = hdf_vd.get_data(i)
            start = hdf_vd.get_data(j)
            time += start
            arrays.append(time)
        time_data = utils.concatenate(arrays)
        time_data = utils.expand_1d_to_2d_array(time_data,len(height_data[0]),axis=1)
        time_metadata = hdf.read_metadata(vdata['Profile_time'], "VD")
        time_coord = Coord(time_data, time_metadata)

        return CoordList([lat_coord,lon_coord,height_coord,time_coord, real_time_coord])

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

class MODIS_L3(AProduct):


    def get_file_signature(self):
        product_names = ['MYD08_D3','MOD08_D3']
        regex_list = [ r'.*' + product + '.*\.hdf' for product in product_names]
        return regex_list


    def create_coords(self, filenames):

        variables = ['XDim','YDim']
        logging.debug("Listing coordinates: " + str(variables))

        sdata, vdata = hdf.read(filenames,variables)

        lat = sdata['YDim']
        lat_data = hdf.read_data(lat,"SD")
        lat_metadata = hdf.read_metadata(lat, "SD")

        lon = sdata['XDim']
        lon_data = hdf.read_data(lon,"SD")
        lon_metadata = hdf.read_metadata(lon, "SD")

        # to make sure "Latitude" and "Longitude", i.e. the standard_name is displayed instead of "YDim"and "XDim"
        lat_metadata.standard_name = "latitude"
        lat_metadata._name = ""
        lon_metadata.standard_name = "longitude"
        lon_metadata._name = ""

        coords = CoordList()
        coords.append(Coord(lon_data, lon_metadata,'X'))
        coords.append(Coord(lat_data, lat_metadata,'Y'))

        return coords


    def create_data_object(self, filenames, variable):

        logging.debug("Creating data object for variable " + variable)

        # reading coordinates
        # the variable here is needed to work out whether to apply interpolation to the lat/lon data or not
        coords = self.create_coords(filenames)

        # reading of variables
        sdata, vdata = hdf.read(filenames, variable)

        # retrieve data + its metadata
        var = sdata[variable]
        metadata = hdf.read_metadata(var, "SD")

        return UngriddedData(var, metadata, coords)

class MODIS_L2(AProduct):

    modis_scaling = ["1km","5km","10km"]

    def get_file_signature(self):
        product_names = ['MYD06_L2','MOD06_L2','MYD04_L2','MYD04_L2','MYDATML2','MODATML2']
        regex_list = [ r'.*' + product + '.*\.hdf' for product in product_names]
        return regex_list

    def __get_data_scale(self, filename, variable):

        from pyhdf import SD
        meta = SD.SD(filename).datasets()[variable][0][0]

        for scaling in self.modis_scaling:
            if scaling in meta:
                return scaling
        return None

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

    def create_coords(self, filenames, variable=None):

        variables = [ 'Latitude','Longitude','Scan_Start_Time']

        logging.debug("Listing coordinates: " + str(variables))

        sdata, vdata = hdf.read(filenames,variables)

        apply_interpolation = False
        if variable is not None:
            scale = self.__get_data_scale(filenames[0], variable)
            apply_interpolation = True if scale is "1km" else False

        lat = sdata['Latitude']
        lat_data = self.__field_interpolate(hdf.read_data(lat,"SD")) if apply_interpolation else hdf.read_data(lat,"SD")
        lat_metadata = hdf.read_metadata(lat, "SD")
        lat_coord = Coord(lat_data, lat_metadata,'Y')

        lon = sdata['Longitude']
        lon_data = self.__field_interpolate(hdf.read_data(lon,"SD")) if apply_interpolation else hdf.read_data(lon,"SD")
        lon_metadata = hdf.read_metadata(lon,"SD")
        lon_coord = Coord(lon_data, lon_metadata,'X')

        return CoordList([lat_coord,lon_coord])

    def create_data_object(self, filenames, variable):
        logging.debug("Creating data object for variable " + variable)

        # reading coordinates
        # the variable here is needed to work out whether to apply interpolation to the lat/lon data or not
        coords = self.create_coords(filenames, variable)

        # reading of variables
        sdata, vdata = hdf.read(filenames, variable)

        # retrieve data + its metadata
        var = sdata[variable]
        metadata = hdf.read_metadata(var, "SD")

        return UngriddedData(var, metadata, coords)

class Cloud_CCI(AProduct):

    def get_file_signature(self):
        return [r'..*ESACCI.*CLOUD.*']

    def create_coords(self, filenames):

        from data_io.netcdf import read_many_files, get_metadata
        from data_io.Coord import Coord

        variables = ["lat", "lon", "time"]

        data = read_many_files(filenames, variables, dim="across_track")
        #data = read_many_files(filenames, variables)
        #data = read_many_files(filenames, variables, dim="time")

        coords = CoordList()
        coords.append(Coord(data["lon"], get_metadata(data["lon"]), "X"))
        coords.append(Coord(data["lat"], get_metadata(data["lat"]), "Y"))
        coords.append(Coord(data["time"], get_metadata(data["time"]), "T"))

        return coords

    def create_data_object(self, filenames, variable):

        from data_io.netcdf import read_many_files, get_metadata

        coords = self.create_coords(filenames)
        data = read_many_files(filenames, variable, dim="across_track")
        metadata = get_metadata(data[variable])

        return UngriddedData(data[variable], metadata, coords)

class Aerosol_CCI(AProduct):

    def get_file_signature(self):
        return [r'.*ESACCI.*AEROSOL.*']

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

class Caliop(AProduct):

    def get_file_signature(self):
        return [r'CAL.*hdf']

    def create_coords(self, filenames, variable=None):
        variables = [ 'Latitude','Longitude']

        logging.debug("Listing coordinates: " + str(variables))

        sdata, vdata = hdf.read(filenames,variables)

        apply_interpolation = False
        if variable is not None:
            pass
            #scale = self.__get_data_scale(filenames[0], variable)
            #apply_interpolation = True if scale is "1km" else False

        lat = sdata['Latitude']
        lat_data = self.__field_interpolate(hdf.read_data(lat,"SD")) if apply_interpolation else hdf.read_data(lat,"SD")
        lat_metadata = hdf.read_metadata(lat, "SD")
        lat_coord = Coord(lat_data, lat_metadata,'Y')

        lon = sdata['Longitude']
        lon_data = self.__field_interpolate(hdf.read_data(lon,"SD")) if apply_interpolation else hdf.read_data(lon,"SD")
        lon_metadata = hdf.read_metadata(lon,"SD")
        lon_coord = Coord(lon_data, lon_metadata,'X')

        return CoordList([lat_coord,lon_coord])

    def create_data_object(self, filenames, variable):
        logging.debug("Creating data object for variable " + variable)

        # reading coordinates
        # the variable here is needed to work out whether to apply interpolation to the lat/lon data or not
        coords = self.create_coords(filenames, variable)

        # reading of variables
        sdata, vdata = hdf.read(filenames, variable)

        # retrieve data + its metadata
        var = sdata[variable]
        metadata = hdf.read_metadata(var, "SD")

        return UngriddedData(var, metadata, coords)

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
        coords.append(Coord(alt, get_metadata(alt)))
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
            raise InvalidVariableError("Variable not found: " + str(variable) +
                                       "\nTo see a list of variables run: cis info " + filenames[0] + " -h")

        sub_cube = list(cube.slices([ coord for coord in cube.coords(dim_coords=True) if coord.points.size > 1]))[0]
        #  Ensure that there are no extra dimensions which can confuse the plotting.
        # E.g. the shape of the cube might be (1, 145, 165) and so we don't need to know about
        #  the dimension whose length is one. The above list comprehension would return a cube of
        #  shape (145, 165)

        return sub_cube

class Xglnwa_vprof(NetCDF_CF_Gridded):

    def get_file_signature(self):
        return [r'.*xglnwa.*vprof.*\.nc']

    def create_coords(self, filenames, variable = None):
        from data_io.netcdf import read_many_files, get_metadata
        from data_io.Coord import Coord

        variables = [ "latitude" ]

        if variable is not None:
            variables.append(variable)

        data_variables = read_many_files(filenames, variables)

        coords = CoordList()
        coords.append(Coord(data_variables["latitude"], get_metadata(data_variables["latitude"]), "X"))

        if variable is None:
            return coords
        else:
            return UngriddedData(data_variables[variable], get_metadata(data_variables[variable]), coords)


    def create_data_object(self, filenames, variable):
        from iris import AttributeConstraint
        # In this case we use the variable as a name constraint as the variable names themselves aren't obvious
        var_constraint = AttributeConstraint(name=variable)

        return super(Xglnwa_vprof, self).create_data_object(filenames, var_constraint)


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
        from iris import AttributeConstraint
        # In this case we use the variable as a name constraint as the variable names themselves aren't obvious
        var_constraint = AttributeConstraint(name=variable)

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
        from iris.aux_factory import HybridHeightFactory
        cube = super(Xenida, self).create_data_object(filenames, variable)
        cube.add_aux_factory(HybridHeightFactory(cube.coords()[5]))
        return cube

class Aeronet(AProduct):

    def get_file_signature(self):
        #TODO Update this
        return [r'.*\.lev20']

    def create_coords(self, filenames, data_obj = None, variable = None):
        from data_io.ungridded_data import Metadata
        from numpy import array
        from data_io.aeronet import load_aeronet, get_file_metadata

        for filename in filenames:
            if data_obj is None:
                data_obj = load_aeronet(filename)
            metadata = get_file_metadata(filename, variable)
            lon = metadata.misc[2][1].split("=")[1]
            lat = metadata.misc[2][2].split("=")[1]

            coords = CoordList()
            coords.append(Coord(array([lon]), Metadata(name="Longitude", shape=(1,), units="degrees_east", range=(-180,180), missing_value=-999)))
            coords.append(Coord(array([lat]), Metadata(name="Latitude", shape=(1,), units="degrees_north", range=(-90,90), missing_value=-999)))
            date_time_data = data_obj["datetime"]
            coords.append(Coord(date_time_data, Metadata(name="Date time", shape=(len(date_time_data),)), "X"))

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
        return UngriddedData(var_data, metadata, self.create_coords([filename], data_obj, variable))
