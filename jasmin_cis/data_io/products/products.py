import logging

from jasmin_cis.data_io.Coord import Coord, CoordList
from jasmin_cis.data_io.products.AProduct import AProduct
from jasmin_cis.data_io.ungridded_data import UngriddedData, Metadata
import jasmin_cis.utils as utils
import jasmin_cis.data_io.hdf as hdf

class Cloudsat_2B_CWC_RVOD(AProduct):

    def get_file_signature(self):
        return [r'.*2B.CWC.RVOD.*\.hdf']

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

    def create_coords(self, filenames):
        from jasmin_cis.time_util import cis_standard_time_unit
        # list of coordinate variables we are interested in
        variables = [ 'Latitude','Longitude','TAI_start','Profile_time','Height']

        logging.info("Listing coordinates: " + str(variables))

        # reading the various files
        sdata, vdata = hdf.read(filenames,variables)

        # altitude coordinate
        height = sdata['Height']
        height_data = hdf.read_data(height, "SD")
        height_metadata = hdf.read_metadata(height, "SD")
        height_coord = Coord(height_data, height_metadata)

        # latitude
        lat = vdata['Latitude']
        lat_data = utils.expand_1d_to_2d_array(hdf.read_data(lat, "VD"),len(height_data[0]),axis=1)
        lat_metadata = hdf.read_metadata(lat,"VD")
        lat_metadata.shape = lat_data.shape
        lat_coord = Coord(lat_data, lat_metadata, "Y")

        # longitude
        lon = vdata['Longitude']
        lon_data = utils.expand_1d_to_2d_array(hdf.read_data(lon, "VD"),len(height_data[0]),axis=1)
        lon_metadata = hdf.read_metadata(lon, "VD")
        lon_metadata.shape = lon_data.shape
        lon_coord = Coord(lon_data, lon_metadata, "X")

        # time coordinate
        time_data = self._generate_time_array(vdata)
        time_data = utils.expand_1d_to_2d_array(time_data,len(height_data[0]),axis=1)
        time_coord = Coord(time_data,Metadata(standard_name='time', shape=time_data.shape,
                                              units=str(cis_standard_time_unit),
                                              calendar=cis_standard_time_unit.calendar),"T")


        # create object containing list of coordinates
        coords = CoordList()
        coords.append(lat_coord)
        coords.append(lon_coord)
        coords.append(height_coord)
        coords.append(time_coord)

        return coords

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

    def _parse_datetime(self,metadata_dict,keyword):
        import re
        res = ""
        for s in metadata_dict.itervalues():
            i_start = s.find(keyword)
            ssub = s[i_start:len(s)]
            i_end = ssub.find("END_OBJECT")
            ssubsub = s[i_start:i_start+i_end]
            matches = re.findall('".*"',ssubsub)
            if len(matches) > 0:
                res = matches[0].replace('\"','')
                if res is not "":
                    break
        return res

    def _get_start_date(self, filename):
        from jasmin_cis.time_util import parse_datetimestr_to_std_time
        metadata_dict = hdf.get_hdf4_file_metadata(filename)
        date = self._parse_datetime(metadata_dict,'RANGEBEGINNINGDATE')
        time = self._parse_datetime(metadata_dict,'RANGEBEGINNINGTIME')
        datetime_str = date + " " + time
        return parse_datetimestr_to_std_time(datetime_str)

    def _get_end_date(self, filename):
        from jasmin_cis.time_util import parse_datetimestr_to_std_time
        metadata_dict = hdf.get_hdf4_file_metadata(filename)
        date = self._parse_datetime(metadata_dict,'RANGEENDINGDATE')
        time = self._parse_datetime(metadata_dict,'RANGEENDINGTIME')
        datetime_str = date + " " + time
        return parse_datetimestr_to_std_time(datetime_str)

    def get_file_signature(self):
        product_names = ['MYD08_D3','MOD08_D3',"MOD08_E3"]
        regex_list = [ r'.*' + product + '.*\.hdf' for product in product_names]
        return regex_list

    def create_coords(self, filenames):
        import numpy as np
        from jasmin_cis.time_util import calculate_mid_time, cis_standard_time_unit

        variables = ['XDim','YDim']
        logging.info("Listing coordinates: " + str(variables))

        sdata, vdata = hdf.read(filenames,variables)

        lat = sdata['YDim']
        lat_metadata = hdf.read_metadata(lat, "SD")

        lon = sdata['XDim']
        lon_metadata = hdf.read_metadata(lon, "SD")

        # expand lat and lon data array so that they have the same shape
        lat_data = utils.expand_1d_to_2d_array(hdf.read_data(lat,"SD"),lon_metadata.shape,axis=1) # expand latitude column wise
        lon_data = utils.expand_1d_to_2d_array(hdf.read_data(lon,"SD"),lat_metadata.shape,axis=0) # expand longitude row wise

        lat_metadata.shape = lat_data.shape
        lon_metadata.shape = lon_data.shape

        # to make sure "Latitude" and "Longitude", i.e. the standard_name is displayed instead of "YDim"and "XDim"
        lat_metadata.standard_name = "latitude"
        lat_metadata._name = ""
        lon_metadata.standard_name = "longitude"
        lon_metadata._name = ""

        # create arrays for time coordinate using the midpoint of the time delta between the start date and the end date
        time_data_array = []
        for filename in filenames:
            mid_datetime = calculate_mid_time(self._get_start_date(filename),self._get_end_date(filename))
            time_data = np.empty(lat_metadata.shape,dtype='float64')
            time_data.fill(mid_datetime)
            time_data_array.append(time_data)
        time_data = utils.concatenate(time_data_array)
        time_metadata = Metadata(name='Date Time', standard_name='time', shape=time_data.shape,
                                 units=str(cis_standard_time_unit),calendar=cis_standard_time_unit.calendar)

        coords = CoordList()
        coords.append(Coord(lon_data, lon_metadata,'X'))
        coords.append(Coord(lat_data, lat_metadata,'Y'))
        coords.append(Coord(time_data, time_metadata,'T'))

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
        product_names = ['MYD06_L2','MOD06_L2','MYD04_L2','MOD04_L2','MYDATML2','MODATML2']
        regex_list = [ r'.*' + product + '.*\.hdf' for product in product_names]
        return regex_list

    def __get_data_scale(self, filename, variable):
        from jasmin_cis.exceptions import InvalidVariableError
        from pyhdf import SD

        try:
            meta = SD.SD(filename).datasets()[variable][0][0]
        except KeyError:
            raise InvalidVariableError("Variable "+variable+" not found")

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
        import datetime as dt

        variables = [ 'Latitude','Longitude','Scan_Start_Time']
        logging.info("Listing coordinates: " + str(variables))

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

        time = sdata['Scan_Start_Time']
        time_metadata = hdf.read_metadata(time,"SD")
        time_coord = Coord(time,time_metadata,"T")
        time_coord.convert_TAI_time_to_std_time(dt.datetime(1993,1,1,0,0,0))

        return CoordList([lat_coord,lon_coord,time_coord])

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

        from jasmin_cis.data_io.netcdf import read_many_files_individually, get_metadata
        from jasmin_cis.data_io.Coord import Coord

        variables = ["lat", "lon", "time"]
        logging.info("Listing coordinates: " + str(variables))

        var_data = read_many_files_individually(filenames, variables)

        coords = CoordList()
        coords.append(Coord(var_data['lat'], get_metadata(var_data['lat'][0]), 'Y'))
        coords.append(Coord(var_data['lon'], get_metadata(var_data['lon'][0]),'X'))
        time_coord = Coord(var_data['time'], get_metadata(var_data['time'][0]))

        # TODO: Is this really julian?
        time_coord.convert_julian_to_std_time()
        coords.append(time_coord)

        return coords

    def create_data_object(self, filenames, variable):

        from jasmin_cis.data_io.netcdf import get_metadata, read_many_files_individually

        coords = self.create_coords(filenames)
        var = read_many_files_individually(filenames, [variable])
        metadata = get_metadata(var[variable][0])

        return UngriddedData(var[variable], metadata, coords)

class Aerosol_CCI(AProduct):

    def get_file_signature(self):
        return [r'.*ESACCI.*AEROSOL.*']

    def create_coords(self, filenames):

        from jasmin_cis.data_io.netcdf import read_many_files, get_metadata
        from jasmin_cis.data_io.Coord import Coord
        import datetime

        variables = ["lat", "lon", "time"]
        logging.info("Listing coordinates: " + str(variables))

        data = read_many_files(filenames, variables, dim="pixel_number")

        coords = CoordList()
        coords.append(Coord(data["lon"], get_metadata(data["lon"]), "X"))
        coords.append(Coord(data["lat"], get_metadata(data["lat"]), "Y"))
        time_coord = Coord(data["time"], get_metadata(data["time"]), "T")
        time_coord.convert_TAI_time_to_std_time(datetime.datetime(1970,1,1))
        coords.append(time_coord)
        
        return coords

    def create_data_object(self, filenames, variable):
        from jasmin_cis.data_io.netcdf import read_many_files, get_metadata

        coords = self.create_coords(filenames)
        data = read_many_files(filenames, variable, dim="pixel_number")
        metadata = get_metadata(data[variable])

        return UngriddedData(data[variable], metadata, coords)

class Caliop_L2(AProduct):

    def get_file_signature(self):
        return [r'CAL_LID_L2_05kmAPro-Prov-V3-01.*hdf']

    def create_coords(self, filenames):

        from jasmin_cis.data_io.hdf_vd import get_data
        from jasmin_cis.data_io.hdf_vd import VDS
        from pyhdf.error import HDF4Error
        from jasmin_cis.data_io import hdf_sd
        import datetime as dt
        from jasmin_cis.time_util import convert_sec_since_to_std_time_array, cis_standard_time_unit

        variables = [ 'Latitude','Longitude', "Profile_Time"]
        logging.info("Listing coordinates: " + str(variables))

        # reading data from files
        sdata = {}
        alt_data_arr = []
        for filename in filenames:

            try:
                sds_dict = hdf_sd.read(filename, variables)
            except HDF4Error as e:
                raise IOError(str(e))

            for var in sds_dict.keys():
                utils.add_element_to_list_in_dict(sdata, var, sds_dict[var])

            alt_data_arr.append(get_data(VDS(filename,"Lidar_Data_Altitudes"), True))

        # work out size of data arrays
        # the coordinate variables will be reshaped to match that.
        len_x = utils.concatenate(alt_data_arr).shape[0]
        len_y = hdf.read_data(sdata['Latitude'],"SD").shape[0]
        new_shape = (len_x, len_y)

        # altitude
        alt_data = utils.concatenate(alt_data_arr)
        alt_data = utils.expand_1d_to_2d_array(alt_data,len_y,axis=0)
        alt_metadata = Metadata(standard_name="altitude", shape=new_shape)
        alt_coord = Coord(alt_data,alt_metadata)

        # latitude
        lat = sdata['Latitude']
        lat_data = hdf.read_data(lat,"SD")
        lat_data = utils.expand_1d_to_2d_array(lat_data[:,1],len_x,axis=1)
        lat_metadata = hdf.read_metadata(lat, "SD")
        lat_metadata.shape = new_shape
        lat_coord = Coord(lat_data, lat_metadata, 'Y')

        # longitude
        lon = sdata['Longitude']
        lon_data = hdf.read_data(lon,"SD")
        lon_data = utils.expand_1d_to_2d_array(lon_data[:,1],len_x,axis=1)
        lon_metadata = hdf.read_metadata(lon,"SD")
        lon_metadata.shape = new_shape
        lon_coord = Coord(lon_data, lon_metadata,'X')

        #profile time, x
        time = sdata['Profile_Time']
        time_data = hdf.read_data(time,"SD")
        time_data = convert_sec_since_to_std_time_array(time_data, dt.datetime(1993,1,1,0,0,0))
        time_data = utils.expand_1d_to_2d_array(time_data[:,1],len_x,axis=1)
        time_coord = Coord(time_data,Metadata(standard_name='time', shape=time_data.shape,
                                              units=str(cis_standard_time_unit),
                                              calendar=cis_standard_time_unit.calendar),"T")

        # create the object containing all coordinates
        coords = CoordList()
        coords.append(lat_coord)
        coords.append(lon_coord)
        coords.append(time_coord)
        coords.append(alt_coord)

        return coords


    def create_data_object(self, filenames, variable):
        from jasmin_cis.data_io.hdf_sd import get_calipso_data
        logging.debug("Creating data object for variable " + variable)

        # reading coordinates
        # the variable here is needed to work out whether to apply interpolation to the lat/lon data or not
        coords = self.create_coords(filenames)

        # reading of variables
        sdata, vdata = hdf.read(filenames, variable)

        # retrieve data + its metadata
        var = sdata[variable]
        metadata = hdf.read_metadata(var, "SD")

        return UngriddedData(var, metadata, coords, get_calipso_data)


class Caliop_L1(AProduct):

    def get_file_signature(self):
        return [r'CAL_LID_L1-ValStage1-V3-01.*hdf']

    def create_coords(self, filenames):

        from jasmin_cis.data_io.hdf_vd import get_data
        from jasmin_cis.data_io.hdf_vd import VDS
        from pyhdf.error import HDF4Error
        from jasmin_cis.data_io import hdf_sd
        import datetime as dt
        from jasmin_cis.time_util import convert_sec_since_to_std_time_array, cis_standard_time_unit

        variables = [ 'Latitude','Longitude', "Profile_Time"]
        logging.info("Listing coordinates: " + str(variables))

        # reading data from files
        sdata = {}
        alt_data_arr = []
        for filename in filenames:

            try:
                sds_dict = hdf_sd.read(filename, variables)
            except HDF4Error as e:
                raise IOError(str(e))

            for var in sds_dict.keys():
                utils.add_element_to_list_in_dict(sdata, var, sds_dict[var])

            alt_data_arr.append(get_data(VDS(filename,"Lidar_Data_Altitudes"), True))

        # work out size of data arrays
        # the coordinate variables will be reshaped to match that.
        len_x = utils.concatenate(alt_data_arr).shape[0]
        len_y = hdf.read_data(sdata['Latitude'],"SD").shape[0]
        new_shape = (len_x, len_y)

        # altitude
        alt_data = utils.concatenate(alt_data_arr)
        alt_data = utils.expand_1d_to_2d_array(alt_data,len_y,axis=0)
        alt_metadata = Metadata(standard_name="altitude", shape=new_shape)
        alt_coord = Coord(alt_data,alt_metadata)

        # latitude
        lat = sdata['Latitude']
        lat_data = hdf.read_data(lat,"SD")
        lat_data = utils.expand_1d_to_2d_array(lat_data[:,1],len_x,axis=1)
        lat_metadata = hdf.read_metadata(lat, "SD")
        lat_metadata.shape = new_shape
        lat_coord = Coord(lat_data, lat_metadata, 'Y')

        # longitude
        lon = sdata['Longitude']
        lon_data = hdf.read_data(lon,"SD")
        lon_data = utils.expand_1d_to_2d_array(lon_data[:,1],len_x,axis=1)
        lon_metadata = hdf.read_metadata(lon,"SD")
        lon_metadata.shape = new_shape
        lon_coord = Coord(lon_data, lon_metadata,'X')

        #profile time, x
        time = sdata['Profile_Time']
        time_data = hdf.read_data(time,"SD")
        time_data = convert_sec_since_to_std_time_array(time_data, dt.datetime(1993,1,1,0,0,0))
        time_data = utils.expand_1d_to_2d_array(time_data[:,1],len_x,axis=1)
        time_coord = Coord(time_data,Metadata(standard_name='time', shape=time_data.shape,
                                              units=str(cis_standard_time_unit),
                                              calendar=cis_standard_time_unit.calendar),"T")

        # create the object containing all coordinates
        coords = CoordList()
        coords.append(lat_coord)
        coords.append(lon_coord)
        coords.append(time_coord)
        coords.append(alt_coord)

        return coords


    def create_data_object(self, filenames, variable):
        from jasmin_cis.data_io.hdf_sd import get_calipso_data
        logging.debug("Creating data object for variable " + variable)

        # reading coordinates
        # the variable here is needed to work out whether to apply interpolation to the lat/lon data or not
        coords = self.create_coords(filenames)

        # reading of variables
        sdata, vdata = hdf.read(filenames, variable)

        # retrieve data + its metadata
        var = sdata[variable]
        metadata = hdf.read_metadata(var, "SD")

        return UngriddedData(var, metadata, coords, get_calipso_data)


class CisCol(AProduct):

    def get_file_signature(self):
        return [r'cis\-col\-.*\.nc']

    def create_coords(self, filenames, variable = None):
        from jasmin_cis.data_io.netcdf import read_many_files_individually, get_metadata
        from jasmin_cis.data_io.Coord import Coord

        variables = [ "latitude", "longitude", "altitude", "time" ]

        if variable is not None:
            variables.append(variable)

        logging.info("Listing coordinates: " + str(variables))

        var_data = read_many_files_individually(filenames, variables)

        coords = CoordList()
        coords.append(Coord(var_data["longitude"], get_metadata(var_data["longitude"][0])))
        coords.append(Coord(var_data["latitude"], get_metadata(var_data["latitude"][0])))
        coords.append(Coord(var_data["altitude"], get_metadata(var_data["altitude"][0])))
        # We don't need to convert this time coord as it should have been written in our
        #  'standard' time
        coords.append(Coord(var_data["time"], get_metadata(var_data["time"][0]), 'X'))

        if variable is None:
            return coords
        else:
            return UngriddedData(var_data[variable], get_metadata(var_data[variable][0]), coords)

    def create_data_object(self, filenames, variable):
        return self.create_coords(filenames, variable)

class NetCDF_CF(AProduct):

    def get_file_signature(self):
        # We don't know of any 'standard' netCDF CF data yet...
        return []

    def create_coords(self, filenames, variable = None):
        from jasmin_cis.data_io.netcdf import read_many_files, get_metadata
        from jasmin_cis.data_io.Coord import Coord

        variables = [ "latitude", "longitude", "altitude", "time" ]
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
            return coords
        else:
            return UngriddedData(data_variables[variable], get_metadata(data_variables[variable]), coords)

    def create_data_object(self, filenames, variable):
        return self.create_coords(filenames, variable)


class NCAR_NetCDF_RAF(NetCDF_CF):

    def get_file_signature(self):
        return [r'RF.*\.nc']

    def create_coords(self, filenames, variable = None):
        from jasmin_cis.data_io.netcdf import read_many_files, get_metadata
        from jasmin_cis.data_io.Coord import Coord

        variables = [ "LATC", "LONC", "GGALTC", "Time" ]
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

        # checking if the files given actually exist
        for filename in filenames:
            with open(filename) as f: pass

        try:
            cube = iris.load_cube(filenames, variable)
        except iris.exceptions.ConstraintMismatchError:
            raise InvalidVariableError("Variable not found: " + str(variable) +
                                       "\nTo see a list of variables run: cis info " + filenames[0] + " -h")
        except ValueError as e:
            raise IOError(e)

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
        from jasmin_cis.data_io.netcdf import read_many_files, get_metadata
        from jasmin_cis.data_io.Coord import Coord

        variables = [ "latitude" ]
        logging.info("Listing coordinates: " + str(variables))

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
        # TODO Expand coordinates and read multiple files
        # For gridded data sets this will actually return coordinates which are too short
        #  we need to think about how to expand them here
        """

        @param filenames: List of filenames to read coordinates from
        @param variable: Optional variable to read while we're reading the coordinates
        @return: If variable was specified this will return an UngriddedData object, otherwise a CoordList
        """
        from jasmin_cis.data_io.netcdf import read, get_metadata
        from jasmin_cis.data_io.Coord import Coord

        variables = [ "latitude", "longitude", "atmosphere_hybrid_height_coordinate_ak", "time" ]
        logging.info("Listing coordinates: " + str(variables))

        data_variables = read(filenames[0], variables)

        coords = CoordList()
        coords.append(Coord(data_variables["longitude"], get_metadata(data_variables["longitude"]), "X"))
        coords.append(Coord(data_variables["latitude"], get_metadata(data_variables["latitude"]), "Y"))


        altitude = Coord(data_variables["atmosphere_hybrid_height_coordinate_ak"], get_metadata(data_variables["atmosphere_hybrid_height_coordinate_ak"]), "Z")
        altitude.standard_name = 'altitude'


        coords.append(altitude)

        #days since 1979-4-1
        time = Coord(data_variables["time"], get_metadata(data_variables["time"]), "T")
        time.convert_to_std_time()
        coords.append(time)

        return coords

    def create_data_object(self, filenames, variable):
        from iris.aux_factory import HybridHeightFactory
        from jasmin_cis.time_util import convert_cube_time_coord_to_standard_time

        cube = super(Xenida, self).create_data_object(filenames, variable)
        cube.add_aux_factory(HybridHeightFactory(cube.coords()[5]))
        cube = convert_cube_time_coord_to_standard_time(cube)

        return cube

class Aeronet(AProduct):

    def get_file_signature(self):
        return [r'.*\.lev20']

    def create_coords(self, filenames, data = None):
        from jasmin_cis.data_io.ungridded_data import Metadata
        from jasmin_cis.data_io.aeronet import load_multiple_aeronet

        if data is None:
            data = load_multiple_aeronet(filenames)

        coords = CoordList()
        coords.append(Coord(data['longitude'], Metadata(name="Longitude", shape=(len(data),), units="degrees_east", range=(-180,180))))
        coords.append(Coord(data['latitude'], Metadata(name="Latitude", shape=(len(data),), units="degrees_north", range=(-90,90))))
        coords.append(Coord(data['altitude'], Metadata(name="Altitude", shape=(len(data),), units="meters", range=(-90,90))))
        time_coord = Coord(data["datetime"], Metadata(name="Date time",standard_name='time', shape=(len(data),), units="DateTime Object"), "X")
        time_coord.convert_datetime_to_standard_time()
        coords.append(time_coord)

        return coords

    def create_data_object(self, filenames, variable):
        from jasmin_cis.data_io.aeronet import load_multiple_aeronet
        from jasmin_cis.exceptions import InvalidVariableError

        try:
            data_obj = load_multiple_aeronet(filenames, [variable])
        except ValueError:
            raise InvalidVariableError(variable + " does not exist in " + str(filenames))

        coords = self.create_coords(filenames, data_obj)

        return UngriddedData(data_obj[variable], Metadata(name=variable, long_name=variable,shape=(len(data_obj),)), coords)

class ASCII_Hyperpoints(AProduct):

    def get_file_signature(self):
        return [r'.*\.txt']

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
        time = Coord(time_arr, Metadata(standard_name="time", shape=(n_elements,), units="DateTime Object"))
        coords.append(time)

        if variable:
            try:
                data = UngriddedData(data_array['value'], Metadata(name="Altitude", shape=(n_elements,), units="meters"), coords)
            except:
                InvalidVariableError("Value column does not exist in file " + filenames)
            return data
        else:
            return coords

    def create_data_object(self, filenames, variable):
        return self.create_coords(filenames, True)
