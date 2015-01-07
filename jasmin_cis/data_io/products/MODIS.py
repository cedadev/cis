import logging
from jasmin_cis.data_io import hdf as hdf
from jasmin_cis.data_io.Coord import CoordList, Coord
from jasmin_cis.data_io.products import AProduct
from jasmin_cis.data_io.ungridded_data import Metadata, UngriddedCoordinates, UngriddedData
import jasmin_cis.utils as utils


class MODIS_L3(AProduct):
    """
    Data product for MODIS Level 3 data
    """

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
        date = self._parse_datetime(metadata_dict, 'RANGEBEGINNINGDATE')
        time = self._parse_datetime(metadata_dict, 'RANGEBEGINNINGTIME')
        datetime_str = date + " " + time
        return parse_datetimestr_to_std_time(datetime_str)

    def _get_end_date(self, filename):
        from jasmin_cis.time_util import parse_datetimestr_to_std_time
        metadata_dict = hdf.get_hdf4_file_metadata(filename)
        date = self._parse_datetime(metadata_dict, 'RANGEENDINGDATE')
        time = self._parse_datetime(metadata_dict, 'RANGEENDINGTIME')
        datetime_str = date + " " + time
        return parse_datetimestr_to_std_time(datetime_str)

    def get_file_signature(self):
        product_names = ['MYD08_D3', 'MOD08_D3', "MOD08_E3"]
        regex_list = [r'.*' + product + '.*\.hdf' for product in product_names]
        return regex_list

    def get_variable_names(self, filenames, data_type=None):
        import pyhdf.SD

        variables = set([])
        for filename in filenames:
            sd = pyhdf.SD.SD(filename)
            for var_name, var_info in sd.datasets().iteritems():
                # Check that the dimensions are correct
                if var_info[0] == ('YDim:mod08', 'XDim:mod08'):
                    variables.add(var_name)

        return variables

    def _create_coord_list(self, filenames):
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
            logging.debug("Using "+str(mid_datetime)+" as datetime for file "+str(filename))
            # Only use part of the full lat shape as it has already been concatenated
            time_data = np.empty((lat_metadata.shape[0]/len(filenames), lat_metadata.shape[1]), dtype='float64')
            time_data.fill(mid_datetime)
            time_data_array.append(time_data)
        time_data = utils.concatenate(time_data_array)
        time_metadata = Metadata(name='DateTime', standard_name='time', shape=time_data.shape,
                                 units=str(cis_standard_time_unit),calendar=cis_standard_time_unit.calendar)

        coords = CoordList()
        coords.append(Coord(lon_data, lon_metadata, 'X'))
        coords.append(Coord(lat_data, lat_metadata, 'Y'))
        coords.append(Coord(time_data, time_metadata, 'T'))

        return coords

    def create_coords(self, filenames, variable=None):
        return UngriddedCoordinates(self._create_coord_list(filenames))

    def create_data_object(self, filenames, variable):

        logging.debug("Creating data object for variable " + variable)

        # reading coordinates
        # the variable here is needed to work out whether to apply interpolation to the lat/lon data or not
        coords = self._create_coord_list(filenames)

        # reading of variables
        sdata, vdata = hdf.read(filenames, variable)

        # retrieve data + its metadata
        var = sdata[variable]
        metadata = hdf.read_metadata(var, "SD")

        data = UngriddedData(var, metadata, coords)
        return data

    def get_file_format(self, filenames):
        """
        Get the file format
        :param filenames: the filesnames of the file
        :return: file format
        """

        return "HDF4/ModisL3"


class MODIS_L2(AProduct):

    modis_scaling = ["1km", "5km", "10km"]

    def get_file_signature(self):
        product_names = ['MYD06_L2', 'MOD06_L2', 'MYD04_L2', 'MOD04_L2']
        regex_list = [r'.*' + product + '.*\.hdf' for product in product_names]
        return regex_list

    def get_variable_names(self, filenames, data_type=None):
        import pyhdf.SD

        # Determine the valid shape for variables
        sd = pyhdf.SD.SD(filenames[0])
        datasets = sd.datasets()
        valid_shape = datasets['Latitude'][1]  # Assumes that latitude shape == longitude shape (it should)

        variables = set([])
        for filename in filenames:
            sd = pyhdf.SD.SD(filename)
            for var_name, var_info in sd.datasets().iteritems():
                if var_info[1] == valid_shape:
                    variables.add(var_name)

        return variables

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

    def _create_coord_list(self, filenames, variable=None):
        import datetime as dt

        variables = ['Latitude', 'Longitude', 'Scan_Start_Time']
        logging.info("Listing coordinates: " + str(variables))

        sdata, vdata = hdf.read(filenames, variables)

        apply_interpolation = False
        if variable is not None:
            scale = self.__get_data_scale(filenames[0], variable)
            apply_interpolation = True if scale is "1km" else False

        lat = sdata['Latitude']
        sd_lat = hdf.read_data(lat, "SD")
        lat_data = self.__field_interpolate(sd_lat) if apply_interpolation else sd_lat
        lat_metadata = hdf.read_metadata(lat, "SD")
        lat_coord = Coord(lat_data, lat_metadata,'Y')

        lon = sdata['Longitude']
        lon_data = self.__field_interpolate(hdf.read_data(lon,"SD")) if apply_interpolation else hdf.read_data(lon,"SD")
        lon_metadata = hdf.read_metadata(lon,"SD")
        lon_coord = Coord(lon_data, lon_metadata,'X')

        time = sdata['Scan_Start_Time']
        time_metadata = hdf.read_metadata(time,"SD")
        # Ensure the standard name is set
        time_metadata.standard_name = 'time'
        time_coord = Coord(time,time_metadata,"T")
        time_coord.convert_TAI_time_to_std_time(dt.datetime(1993,1,1,0,0,0))

        return CoordList([lat_coord,lon_coord,time_coord])

    def create_coords(self, filenames, variable=None):
        return UngriddedCoordinates(self._create_coord_list(filenames))

    def create_data_object(self, filenames, variable):
        logging.debug("Creating data object for variable " + variable)

        # reading coordinates
        # the variable here is needed to work out whether to apply interpolation to the lat/lon data or not
        coords = self._create_coord_list(filenames, variable)

        # reading of variables
        sdata, vdata = hdf.read(filenames, variable)

        # retrieve data + its metadata
        var = sdata[variable]
        metadata = hdf.read_metadata(var, "SD")

        return UngriddedData(var, metadata, coords)

    def get_file_format(self, filenames):
        """
        Get the file format
        :param filenames: the filenames of the file
        :return: file format
        """

        return "HDF4/ModisL2"