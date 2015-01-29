import logging
import pyhdf.SD
from jasmin_cis.data_io import hdf as hdf
from jasmin_cis.data_io.Coord import Coord, CoordList
from jasmin_cis.data_io.hdf_vd import get_data, VDS
from jasmin_cis.data_io.products import AProduct
from jasmin_cis.data_io.ungridded_data import Metadata, UngriddedCoordinates, UngriddedData
import jasmin_cis.utils as utils


class abstract_Caliop(AProduct):

    def get_file_signature(self):
        '''
        To be implemented by subclcass
        :return:
        '''
        return []

    def get_variable_names(self, filenames, data_type=None):
        import pyhdf.SD
        import pyhdf.HDF
        variables = set([])

        # Determine the valid shape for variables
        sd = pyhdf.SD.SD(filenames[0])
        datasets = sd.datasets()
        len_x = datasets['Latitude'][1][0]  # Assumes that latitude shape == longitude shape (it should)
        alt_data = get_data(VDS(filenames[0], "Lidar_Data_Altitudes"), True)
        len_y = alt_data.shape[0]
        valid_shape = (len_x, len_y)

        for filename in filenames:
            sd = pyhdf.SD.SD(filename)
            for var_name, var_info in sd.datasets().iteritems():
                if var_info[1] == valid_shape:
                    variables.add(var_name)

        return variables

    def _create_coord_list(self, filenames, index_offset=0):
        from jasmin_cis.data_io.hdf_vd import get_data
        from jasmin_cis.data_io.hdf_vd import VDS
        from pyhdf.error import HDF4Error
        from jasmin_cis.data_io import hdf_sd
        import datetime as dt
        from jasmin_cis.time_util import convert_sec_since_to_std_time_array, cis_standard_time_unit

        variables = ['Latitude','Longitude', "Profile_Time", "Pressure"]
        logging.info("Listing coordinates: " + str(variables))

        # reading data from files
        sdata = {}
        for filename in filenames:
            try:
                sds_dict = hdf_sd.read(filename, variables)
            except HDF4Error as e:
                raise IOError(str(e))

            for var in sds_dict.keys():
                utils.add_element_to_list_in_dict(sdata, var, sds_dict[var])

        alt_name = "altitude"
        logging.info("Additional coordinates: '" + alt_name + "'")

        # work out size of data arrays
        # the coordinate variables will be reshaped to match that.
        # NOTE: This assumes that all Caliop_L1 files have the same altitudes.
        #       If this is not the case, then the following line will need to be changed
        #       to concatenate the data from all the files and not just arbitrarily pick
        #       the altitudes from the first file.
        alt_data = get_data(VDS(filenames[0],"Lidar_Data_Altitudes"), True)
        alt_data *= 1000.0  # Convert to m
        len_x = alt_data.shape[0]

        lat_data = hdf.read_data(sdata['Latitude'],"SD")
        len_y = lat_data.shape[0]

        new_shape = (len_x, len_y)

        # altitude
        alt_data = utils.expand_1d_to_2d_array(alt_data,len_y,axis=0)
        alt_metadata = Metadata(name=alt_name, standard_name=alt_name, shape=new_shape)
        alt_coord = Coord(alt_data,alt_metadata)

        # pressure
        pres_data = hdf.read_data(sdata['Pressure'],"SD")
        pres_metadata = hdf.read_metadata(sdata['Pressure'], "SD")
        pres_metadata.shape = new_shape
        pres_coord = Coord(pres_data, pres_metadata, 'P')

        # latitude
        lat_data = utils.expand_1d_to_2d_array(lat_data[:,index_offset],len_x,axis=1)
        lat_metadata = hdf.read_metadata(sdata['Latitude'], "SD")
        lat_metadata.shape = new_shape
        lat_coord = Coord(lat_data, lat_metadata, 'Y')

        # longitude
        lon = sdata['Longitude']
        lon_data = hdf.read_data(lon,"SD")
        lon_data = utils.expand_1d_to_2d_array(lon_data[:,index_offset],len_x,axis=1)
        lon_metadata = hdf.read_metadata(lon, "SD")
        lon_metadata.shape = new_shape
        lon_coord = Coord(lon_data, lon_metadata, 'X')

        #profile time, x
        time = sdata['Profile_Time']
        time_data = hdf.read_data(time,"SD")
        time_data = convert_sec_since_to_std_time_array(time_data, dt.datetime(1993, 1, 1, 0, 0, 0))
        time_data = utils.expand_1d_to_2d_array(time_data[:, index_offset], len_x, axis=1)
        time_coord = Coord(time_data,Metadata(name='Profile_Time', standard_name='time', shape=time_data.shape,
                                              units=str(cis_standard_time_unit),
                                              calendar=cis_standard_time_unit.calendar),"T")

        # create the object containing all coordinates
        coords = CoordList()
        coords.append(lat_coord)
        coords.append(lon_coord)
        coords.append(time_coord)
        coords.append(alt_coord)
        if pres_data.shape == alt_data.shape:
            # For MODIS L1 this may is not be true, so skips the air pressure reading. If required for MODIS L1 then
            # some kind of interpolation of the air pressure would be required, as it is on a different (smaller) grid
            # than for the Lidar_Data_Altitudes.
            coords.append(pres_coord)

        return coords

    def create_coords(self, filenames, variable=None):
        return UngriddedCoordinates(self._create_coord_list(filenames))

    def create_data_object(self, filenames, variable):
        '''
        To be implemented by subclass
        :param filenames:
        :param variable:
        :return:
        '''
        return None

    def get_calipso_data(self, sds):
        """
        Reads raw data from an SD instance. Automatically applies the
        scaling factors and offsets to the data arrays found in Calipso data.

        Returns:
            A numpy array containing the raw data with missing data is replaced by NaN.

        Arguments:
            sds        -- The specific sds instance to read

        """
        from jasmin_cis.utils import create_masked_array_for_missing_data

        calipso_fill_values = {'Float_32' : -9999.0,
                               #'Int_8' : 'See SDS description',
                               'Int_16' : -9999,
                               'Int_32' : -9999,
                               'UInt_8' : -127,
                               #'UInt_16' : 'See SDS description',
                               #'UInt_32' : 'See SDS description',
                               'ExtinctionQC Fill Value' : 32768,
                               'FeatureFinderQC No Features Found' : 32767,
                               'FeatureFinderQC Fill Value' : 65535}

        data = sds.get()
        attributes = sds.attributes()

        # Missing data.
        missing_val = attributes.get('fillvalue', None)
        if missing_val is None:
            try:
                missing_val = calipso_fill_values[attributes.get('format', None)]
            except KeyError:
                # Last guess
                missing_val = attributes.get('_FillValue', None)

        data = create_masked_array_for_missing_data(data, missing_val)

        # Offsets and scaling.
        offset  = attributes.get('add_offset', 0)
        scale_factor = attributes.get('scale_factor', 1)
        data = self.apply_scaling_factor_CALIPSO(data, scale_factor, offset)

        return data

    def apply_scaling_factor_CALIPSO(self,data, scale_factor, offset):
        '''
        Apply scaling factor Calipso data
        :param data:
        :param scale_factor:
        :param offset:
        :return:
        '''
        return (data/scale_factor) + offset


class Caliop_L2(abstract_Caliop):

    def get_file_signature(self):
        return [r'CAL_LID_L2_05kmAPro-Prov-V3.*hdf']

    def create_coords(self, filenames, variable=None):
        return UngriddedCoordinates(super(Caliop_L2, self)._create_coord_list(filenames, index_offset=1))

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

        return UngriddedData(var, metadata, coords, self.get_calipso_data)

    def get_file_format(self, filenames):
        """
        Get the file format
        :param filenames: the filenames of the file
        :return: file format
        """

        return "HDF4/CaliopL2"


class Caliop_L1(abstract_Caliop):

    def get_file_signature(self):
        return [r'CAL_LID_L1-ValStage1-V3.*hdf']

    def offset(self):
        return 0

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

        return UngriddedData(var, metadata, coords, self.get_calipso_data)

    def get_file_format(self, filenames):
        """
        Get the file format
        :param filenames: the filenames of the file
        :return: file format
        """

        return "HDF4/CaliopL1"