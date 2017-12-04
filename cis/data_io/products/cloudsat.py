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
        from cis.time_util import convert_sec_since_to_std_time

        Cloudsat_start_time = dt.datetime(1993, 1, 1, 0, 0, 0)

        arrays = []
        for i, j in zip(vdata['Profile_time'], vdata['TAI_start']):
            time = hdf_vd.get_data(i)
            start = hdf_vd.get_data(j)
            time += start
            # Do the conversion to standard time here before we expand the time array...
            time = convert_sec_since_to_std_time(time, Cloudsat_start_time)
            arrays.append(time)
        return utils.concatenate(arrays)

    def _create_one_dimensional_coord_list(self, filenames):
        from cis.time_util import cis_standard_time_unit
        # list of coordinate variables we are interested in
        variables = ['Latitude', 'Longitude', 'TAI_start', 'Profile_time']

        # reading the various files
        logging.info("Listing coordinates: " + str(variables))
        sdata, vdata = hdf.read(filenames, variables)

        # latitude
        lat = vdata['Latitude']
        lat_data = hdf.read_data(lat, self._get_cloudsat_vds_data)
        lat_metadata = hdf.read_metadata(lat, "VD")
        lat_metadata.shape = lat_data.shape
        lat_coord = Coord(lat_data, lat_metadata)

        # longitude
        lon = vdata['Longitude']
        lon_data = hdf.read_data(lon, self._get_cloudsat_vds_data)
        lon_metadata = hdf.read_metadata(lon, "VD")
        lon_metadata.shape = lon_data.shape
        lon_coord = Coord(lon_data, lon_metadata)

        # time coordinate
        time_data = self._generate_time_array(vdata)
        time_coord = Coord(time_data, Metadata(name='Profile_time', standard_name='time', shape=time_data.shape,
                                               units=cis_standard_time_unit), "X")

        # create object containing list of coordinates
        coords = CoordList()
        coords.append(lat_coord)
        coords.append(lon_coord)
        coords.append(time_coord)

        return coords

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
            height_data = hdf.read_data(height, self._get_cloudsat_sds_data)
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
        lat_data = hdf.read_data(lat, self._get_cloudsat_vds_data)
        if height_data is not None:
            lat_data = utils.expand_1d_to_2d_array(lat_data, len(height_data[0]), axis=1)
        lat_metadata = hdf.read_metadata(lat, "VD")
        lat_metadata.shape = lat_data.shape
        lat_coord = Coord(lat_data, lat_metadata)

        # longitude
        lon = vdata['Longitude']
        lon_data = hdf.read_data(lon, self._get_cloudsat_vds_data)
        if height_data is not None:
            lon_data = utils.expand_1d_to_2d_array(lon_data, len(height_data[0]), axis=1)
        lon_metadata = hdf.read_metadata(lon, "VD")
        lon_metadata.shape = lon_data.shape
        lon_coord = Coord(lon_data, lon_metadata)

        # time coordinate
        time_data = self._generate_time_array(vdata)
        if height_data is not None:
            time_data = utils.expand_1d_to_2d_array(time_data, len(height_data[0]), axis=1)
        time_coord = Coord(time_data, Metadata(name='Profile_time', standard_name='time', shape=time_data.shape,
                                               units=cis_standard_time_unit), "X")

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

        # reading of variables
        sdata, vdata = hdf.read(filenames, variable)

        # retrieve data + its metadata
        if variable in vdata:
            # reading (un-expanded) coordinates, since the data is 1-dimensional
            coords = self._create_one_dimensional_coord_list(filenames)
            var = hdf.read_data(vdata[variable], self._get_cloudsat_vds_data)
            metadata = hdf.read_metadata(vdata[variable], "VD")
        elif variable in sdata:
            # reading coordinates
            coords = self._create_coord_list(filenames)
            var = hdf.read_data(sdata[variable], self._get_cloudsat_sds_data)
            metadata = hdf.read_metadata(sdata[variable], "SD")
        else:
            raise ValueError("variable not found")

        return UngriddedData(var, metadata, coords)

    def _get_cloudsat_vds_data(self, vds):
        from cis.data_io.hdf_vd import _get_attribute_value, HDF, HDF4Error
        from cis.utils import create_masked_array_for_missing_data
        import numpy as np

        # get file and variable reference from tuple
        filename = vds.filename
        variable = vds.variable

        try:
            datafile = HDF(filename)
        except HDF4Error as e:
            raise IOError(e)

        vs = datafile.vstart()
        vd = vs.attach(variable)
        data = vd.read(nRec=vd.inquire()[0])

        # create numpy array from data
        data = np.array(data).flatten()

        missing_value = _get_attribute_value(vd, 'missing', None)

        if missing_value is not None:
            data = create_masked_array_for_missing_data(data, missing_value)

        valid_range = _get_attribute_value(vd, "valid_range")
        if valid_range is not None:
            # Assume it's the right data type already
            data = np.ma.masked_outside(data, *valid_range)

        factor = _get_attribute_value(vd, "factor", 1)
        offset = _get_attribute_value(vd, "offset", 0)
        data = self._apply_scaling_factor_CLOUDSAT(data, factor, offset)

        # detach and close
        vd.detach()
        vs.end()
        datafile.close()

        return data

    def _get_cloudsat_sds_data(self, sds):
        """
        Reads raw data from an SD instance. Automatically applies the
        scaling factors and offsets to the data arrays often found in NASA HDF-EOS
        data (e.g. MODIS)

        :param sds: The specific sds instance to read
        :return: A numpy array containing the raw data with missing data is replaced by NaN.
        """
        from cis.utils import create_masked_array_for_missing_data
        import numpy as np
        data = sds.get()
        attributes = sds.attributes()

        # First deal with the Fill value
        fill_value = attributes.get('_FillValue', None)

        if fill_value is not None:
            data = create_masked_array_for_missing_data(data, fill_value)

        # TODO: This needs some explict integration and unit tests
        # Then deal with missing values
        missop_fn = {'<': np.ma.masked_less,
                     '<=': np.ma.masked_less_equal,
                     '==': np.ma.masked_equal,
                     '=>': np.ma.masked_greater_equal,
                     '>': np.ma.masked_greater}

        missing = attributes.get('missing', None)
        missop = attributes.get('missop', None)
        if missing is not None and missop is not None:
            try:
                logging.debug("Masking all values v {} {}".format(missop, missing))
                data = missop_fn[missop](data, missing)
            except KeyError:
                logging.warning("Unable to identify missop {}, unable to "
                                "mask missing values for {}.".format(missop, sds.info()[0]))

        # Now handle valid range mask
        valid_range = attributes.get('valid_range', None)
        if valid_range is not None:
            # Assume it's the right data type already
            logging.debug("Masking all values {} > v > {}.".format(*valid_range))
            data = np.ma.masked_outside(data, *valid_range)

        # Offsets and scaling.
        offset = attributes.get('offset', 0)
        scale_factor = attributes.get('factor', 1)
        data = self._apply_scaling_factor_CLOUDSAT(data, scale_factor, offset)

        return data

    def _apply_scaling_factor_CLOUDSAT(self, data, scale_factor, offset):
        """
        Using transformation supplied by Phil Partain (cloudsat@colostate.edu) by email on 5th August 2016

        :param data:
        :param scale_factor:
        :param offset:
        :return:
        """
        logging.debug("Applying 'science_data = (packed_data - {offset}) / {scale}' "
                      "transformation to data.".format(scale=scale_factor, offset=offset))
        return (data - offset) / scale_factor

    def get_file_format(self, filename):
        return "HDF4/CloudSat"
