import logging
from cis.data_io import hdf as hdf
from cis.data_io.Coord import Coord, CoordList
from cis.data_io.products import AProduct
from cis.exceptions import InvalidVariableError, CoordinateNotFoundError
from cis.data_io.ungridded_data import Metadata, UngriddedCoordinates, UngriddedData
import cis.utils as utils


class CloudSat(AProduct):

    def get_file_signature(self):
        return [r'.*_CS_.*GRANULE.*\.hdf']

    def get_variable_names(self, filenames, data_type=None):
        try:
            from pyhdf.SD import SD
            from pyhdf.HDF import HDF
        except ImportError:
            raise ImportError("HDF support was not installed, please reinstall with pyhdf to read HDF files.")

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
        import cis.data_io.hdf_vd as hdf_vd
        import datetime as dt
        from cis.time_util import convert_sec_since_to_std_time_array

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
        from cis.time_util import cis_standard_time_unit
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