import logging
from cis.data_io import hdf as hdf
from cis.data_io.Coord import CoordList, Coord
from cis.data_io.products import AProduct
from cis.data_io.ungridded_data import UngriddedCoordinates, UngriddedData, UngriddedDataList


def _get_MODIS_SDS_data(sds):
    """
    Reads raw data from an SD instance.

    :param sds: The specific sds instance to read
    :return: A numpy array containing the raw data with missing data is replaced by NaN.
    """
    from cis.utils import create_masked_array_for_missing_data
    import numpy as np

    data = sds.get()
    attributes = sds.attributes()

    # Squeeze dimensions that have been sliced
    if sds._count is not None and any(np.array(sds._count) == 1):
        data = data.squeeze()

    # Apply Fill Value
    missing_value = attributes.get('_FillValue', None)
    if missing_value is not None:
        data = create_masked_array_for_missing_data(data, missing_value)

    # Check for valid_range
    valid_range = attributes.get('valid_range', None)
    if valid_range is not None:
        logging.debug("Masking all values {} > v > {}.".format(*valid_range))
        data = np.ma.masked_outside(data, *valid_range)

    # Offsets and scaling.
    add_offset = attributes.get('add_offset', 0.0)
    scale_factor = attributes.get('scale_factor', 1.0)
    data = _apply_scaling_factor_MODIS(data, scale_factor, add_offset)

    return data


def _apply_scaling_factor_MODIS(data, scale_factor, offset):
    """
    Apply scaling factor (applicable to MODIS data) of the form:
    ``data = (data - offset) * scale_factor``

    Ref:
    MODIS Atmosphere L3 Gridded Product Algorithm Theoretical Basis Document,
    MODIS Algorithm Theoretical Basis Document No. ATBD-MOD-30 for
    Level-3 Global Gridded Atmosphere Products (08_D3, 08_E3, 08_M3)
    by PAUL A. HUBANKS, MICHAEL D. KING, STEVEN PLATNICK, AND ROBERT PINCUS
    (Collection 005 Version 1.1, 4 December 2008)

    :param data: A numpy array like object
    :param scale_factor:
    :param offset:
    :return: Scaled data
    """
    logging.debug("Applying 'science_data = (packed_data - {offset}) * {scale}' "
                  "transformation to data.".format(scale=scale_factor, offset=offset))
    return (data - offset) * scale_factor


class MODIS_L3(AProduct):
    """
    Data product for MODIS Level 3 data
    """

    def _parse_datetime(self, metadata_dict, keyword):
        import re
        res = ""
        for s in metadata_dict.values():
            i_start = s.find(keyword)
            ssub = s[i_start:len(s)]
            i_end = ssub.find("END_OBJECT")
            ssubsub = s[i_start:i_start + i_end]
            matches = re.findall('".*"', ssubsub)
            if len(matches) > 0:
                res = matches[0].replace('\"', '')
                if res != "":
                    break
        return res

    def _get_start_date(self, filename):
        from cis.parse_datetime import parse_datetimestr_to_std_time
        metadata_dict = hdf.get_hdf4_file_metadata(filename)
        date = self._parse_datetime(metadata_dict, 'RANGEBEGINNINGDATE')
        time = self._parse_datetime(metadata_dict, 'RANGEBEGINNINGTIME')
        datetime_str = date + " " + time
        return parse_datetimestr_to_std_time(datetime_str)

    def _get_end_date(self, filename):
        from cis.parse_datetime import parse_datetimestr_to_std_time
        metadata_dict = hdf.get_hdf4_file_metadata(filename)
        date = self._parse_datetime(metadata_dict, 'RANGEENDINGDATE')
        time = self._parse_datetime(metadata_dict, 'RANGEENDINGTIME')
        datetime_str = date + " " + time
        return parse_datetimestr_to_std_time(datetime_str)

    def get_file_signature(self):
        product_names = ['MYD08_D3', 'MOD08_D3', 'MYD08_M3', 'MOD08_M3', "MOD08_E3"]
        regex_list = [r'.*' + product + '.*\.hdf' for product in product_names]
        return regex_list

    def get_variable_names(self, filenames, data_type=None):
        try:
            from pyhdf.SD import SD
        except ImportError:
            raise ImportError("HDF support was not installed, please reinstall with pyhdf to read HDF files.")

        variables = set([])
        for filename in filenames:
            sd = SD(filename)
            for var_name, var_info in sd.datasets().items():
                # Check that the dimensions are correct
                if var_info[0] == ('YDim:mod08', 'XDim:mod08'):
                    variables.add(var_name)

        return variables

    def _create_cube(self, filenames, variable):
        import numpy as np
        from cis.data_io.hdf import _read_hdf4
        from iris.cube import Cube, CubeList
        from iris.coords import DimCoord, AuxCoord
        from cis.time_util import calculate_mid_time, cis_standard_time_unit
        from cis.data_io.hdf_sd import get_metadata
        from cf_units import Unit

        variables = ['XDim', 'YDim', variable]
        logging.info("Listing coordinates: " + str(variables))

        cube_list = CubeList()
        # Read each file individually, let Iris do the merging at the end.
        for f in filenames:
            sdata, vdata = _read_hdf4(f, variables)

            lat_coord = DimCoord(_get_MODIS_SDS_data(sdata['YDim']), standard_name='latitude', units='degrees')
            lon_coord = DimCoord(_get_MODIS_SDS_data(sdata['XDim']), standard_name='longitude', units='degrees')

            # create time coordinate using the midpoint of the time delta between the start date and the end date
            start_datetime = self._get_start_date(f)
            end_datetime = self._get_end_date(f)
            mid_datetime = calculate_mid_time(start_datetime, end_datetime)
            logging.debug("Using {} as datetime for file {}".format(mid_datetime, f))
            time_coord = AuxCoord(mid_datetime, standard_name='time', units=cis_standard_time_unit,
                                  bounds=[start_datetime, end_datetime])

            var = sdata[variable]
            metadata = get_metadata(var)

            try:
                units = Unit(metadata.units)
            except ValueError:
                logging.warning("Unable to parse units '{}' in {} for {}.".format(metadata.units, f, variable))
                units = None

            cube = Cube(_get_MODIS_SDS_data(sdata[variable]),
                        dim_coords_and_dims=[(lon_coord, 1), (lat_coord, 0)],
                        aux_coords_and_dims=[(time_coord, None)],
                        var_name=metadata._name, long_name=metadata.long_name, units=units)

            cube_list.append(cube)

        # Merge the cube list across the scalar time coordinates before returning a single cube.
        return cube_list.merge_cube()

    def create_coords(self, filenames, variable=None):
        """Reads the coordinates on which a variable depends.
        Note: This calls create_data_object because the coordinates are returned as a Cube.
        :param filenames: list of names of files from which to read coordinates
        :param variable: name of variable for which the coordinates are required
        :return: iris.cube.Cube
        """
        if variable is None:
            variable_names = self.get_variable_names(filenames)
            variable_name = str(variable_names.pop())
            logging.debug("Reading an IRIS Cube for the coordinates based on the variable %s" % variable_names)
        else:
            variable_name = variable

        return self.create_data_object(filenames, variable_name)

    def create_data_object(self, filenames, variable):
        from cis.data_io.gridded_data import make_from_cube
        logging.debug("Creating data object for variable " + variable)

        cube = self._create_cube(filenames, variable)
        return make_from_cube(cube)

    def get_file_format(self, filename):
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
            for var_name, var_info in sd.datasets().items():
                if var_info[1] == valid_shape:
                    variables.add(var_name)

        return variables

    def __get_data_scale(self, filename, variable):
        from cis.exceptions import InvalidVariableError
        from pyhdf.SD import SD

        try:
            meta = SD(filename).datasets()[variable][0][0]
        except KeyError:
            raise InvalidVariableError("Variable " + variable + " not found")

        for scaling in self.modis_scaling:
            if scaling in meta:
                return scaling
        return None

    def __field_interpolate(self, data, factor=5):
        """
        Interpolates the given 2D field by the factor,
        edge pixels are defined by the ones in the centre,
        odd factors only!
        """
        import numpy as np

        logging.debug("Performing interpolation...")

        output = np.zeros((factor * data.shape[0], factor * data.shape[1])) * np.nan
        output[int(factor / 2)::factor, int(factor / 2)::factor] = data
        for i in range(1, factor + 1):
            output[(int(factor / 2) + i):(-1 * factor / 2 + 1):factor, :] = i * (
                (output[int(factor / 2) + factor::factor, :] - output[int(factor / 2):(-1 * factor):factor, :]) /
                float(factor)) + output[int(factor / 2):(-1 * factor):factor, :]
        for i in range(1, factor + 1):
            output[:, (int(factor / 2) + i):(-1 * factor / 2 + 1):factor] = i * (
                (output[:, int(factor / 2) + factor::factor] - output[:, int(factor / 2):(-1 * factor):factor]) /
                float(factor)) + output[:, int(factor / 2):(-1 * factor):factor]
        return output

    def _create_coord_list(self, filenames, variable=None):
        import datetime as dt

        variables = ['Latitude', 'Longitude', 'Scan_Start_Time']
        logging.info("Listing coordinates: " + str(variables))

        sdata, vdata = hdf.read(filenames, variables)

        apply_interpolation = False
        if variable is not None:
            scale = self.__get_data_scale(filenames[0], variable)
            apply_interpolation = True if scale == "1km" else False

        lat = sdata['Latitude']
        sd_lat = hdf.read_data(lat, _get_MODIS_SDS_data)
        lat_data = self.__field_interpolate(sd_lat) if apply_interpolation else sd_lat
        lat_metadata = hdf.read_metadata(lat, "SD")
        lat_coord = Coord(lat_data, lat_metadata, 'Y')

        lon = sdata['Longitude']
        if apply_interpolation:
            lon_data = self.__field_interpolate(hdf.read_data(lon, _get_MODIS_SDS_data))
        else:
            lon_data = hdf.read_data(lon, _get_MODIS_SDS_data)

        lon_metadata = hdf.read_metadata(lon, "SD")
        lon_coord = Coord(lon_data, lon_metadata, 'X')

        time = sdata['Scan_Start_Time']
        time_metadata = hdf.read_metadata(time, "SD")
        # Ensure the standard name is set
        time_metadata.standard_name = 'time'
        time_coord = Coord(time, time_metadata, "T", _get_MODIS_SDS_data)
        time_coord.convert_TAI_time_to_std_time(dt.datetime(1993, 1, 1, 0, 0, 0))

        return CoordList([lat_coord, lon_coord, time_coord])

    def create_coords(self, filenames, variable=None):
        return UngriddedCoordinates(self._create_coord_list(filenames))

    def create_data_object(self, filenames, variable):
        from itertools import product

        logging.debug("Creating data object for variable " + variable)

        # reading coordinates
        # the variable here is needed to work out whether to apply interpolation to the lat/lon data or not
        coords = self._create_coord_list(filenames, variable)

        # reading of variables
        sdata, vdata = hdf.read(filenames, variable)

        # retrieve data + its metadata
        var = sdata[variable]
        metadata = hdf.read_metadata(var, "SD")

        # Check the dimension of this variable
        _, ndim, dim_len, _, _ = var[0].info()
        if ndim == 2:
            return UngriddedData(var, metadata, coords, _get_MODIS_SDS_data)

        elif ndim < 2:
            raise NotImplementedError("1D field in MODIS L2 data.")

        else:
            result = UngriddedDataList()

            # Iterate over all but the last two dimensions
            ranges = [range(n) for n in dim_len[:-2]]
            for indices in product(*ranges):
                for manager in var:
                    manager._start = list(indices) + [0, 0]
                    manager._count = [1] * len(indices) + manager.info()[2][-2:]
                result.append(UngriddedData(var, metadata, coords.copy(), _get_MODIS_SDS_data))
            return result

    def get_file_format(self, filenames):
        """
        Get the file format
        :param filenames: the filenames of the file
        :return: file format
        """

        return "HDF4/ModisL2"
