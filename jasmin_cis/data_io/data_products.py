from abc import ABCMeta, abstractmethod
from data_io.hdf import read_hdf4
from ungridded_data import UngriddedData, Coord
import sys

class AProduct(object):
    """
        Abstract class for the various possible data products. This just defines the interface which
         the subclasses must implement.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_ungridded_data(self, filenames, variable):
        """
        Create a an ungridded data object for a given variable from many files

        @param filenames:    List of filenames of files to read
        @param usr_variable:    Variable to read from the files
        @return: An UngriddedData object for the specified variable

        @raise FileIOError: Unable to read a file
        @raise InvalidVariableError: Variable not present in file
        """
        pass

    @abstractmethod
    def get_file_signature(self):
        '''
        TODO !!!
        @return:
        '''
        pass

class Cloudsat_2B_CWC_RVOD(AProduct):

    def get_file_signature(self):
        return [r'.*2B.CWC.RVOD*'];

    def create_ungridded_data(self, filenames, variable):

        import utils
        import hdf_vd as hdf_vd
        import hdf_sd as hdf_sd

        # if filenames is not a list, make it a list of 1 element
        if not isinstance(filenames,list): filenames = [ filenames ]

        # list of variables we are interested in
        variables = [ variable, 'Latitude','Longitude','TAI_start','Profile_time','Height']

        # reading of all variables
        sdata = {}
        vdata = {}
        for filename in filenames:

            print filename

            try:

                # reading in all variables into a 2 dictionaries:
                # sdata, key: variable name, value: list of sds
                # vdata, key: variable name, value: list of vds
                sds_dict, vds_dict = read_hdf4(filename,variables)
                for var in sds_dict.keys():
                    utils.add_element_to_list_in_dict(sdata,var,sds_dict[var])
                for var in vds_dict.keys():
                    utils.add_element_to_list_in_dict(vdata,var,vds_dict[var])

            except:
                print 'Error while reading file ', filename

        # retrieve data + its metadata
        data = sdata[variable]
        metadata = hdf_sd.get_metadata(sdata[variable][0])

        # retrieve coordinates
        alt_data = utils.concatenate([hdf_sd.get_data(i) for i in sdata['Height'] ])
        alt_metadata = hdf_sd.get_metadata(sdata['Height'][0])
        alt_coord = Coord(alt_data, alt_metadata,'Y')

        lat_data = utils.concatenate([hdf_vd.get_data(i) for i in vdata['Latitude'] ])
        lat_data = utils.expand_1d_to_2d_array(lat_data,len(alt_data[1]),axis=1)
        lat_metadata = hdf_vd.get_metadata(vdata['Latitude'][0])
        lat_coord = Coord(lat_data, lat_metadata)

        lon_data = utils.concatenate([hdf_vd.get_data(i) for i in vdata['Longitude'] ])
        lon_data = utils.expand_1d_to_2d_array(lon_data,len(alt_data[1]),axis=1)
        lon_metadata = hdf_vd.get_metadata(vdata['Longitude'][0])
        lon_coord = Coord(lon_data, lon_metadata)

        arrays = []
        for i,j in zip(vdata['Profile_time'],vdata['TAI_start']):
            time = hdf_vd.get_data(i)
            start = hdf_vd.get_data(j)
            time += start
            arrays.append(time)
        time_data = utils.concatenate(arrays)
        time_data = utils.expand_1d_to_2d_array(time_data,len(alt_data[1]),axis=1)
        time_metadata = hdf_vd.get_metadata(vdata['Profile_time'][0])
        time_coord = Coord(time_data, time_metadata,'X')

        coords= [lat_coord,lon_coord,alt_coord,time_coord]

        return UngriddedData(data,metadata,coords)


class NetCDF_CF(AProduct):

    def get_file_signature(self):
        return [r'.*.nc'];

    def create_ungridded_data(self, filenames, variable):

        import utils
        from data_io.netcdf import read_many_files

        # if filenames is not a list, make it a list of 1 element
        if not isinstance(filenames,list): filenames = [ filenames ]

        # get variable
        var = read_many_files(filenames, [variable, "Latitude", "Longitude", "Time"])

        # get coordinates
        #coords = [ read_many_files(filenames, dim) for dim in var.dimensions ]

        return UngriddedData(var, metadata=var["Longitude"], coords=var["Latitude"])

    '''
    def get_coords_from_variable(self):
        coord_standard_names = [coord for coord in data.coordinates.split()]
        coords = []
        for standard_name in coord_standard_names:
            for variable in datafile.variables:
                try:
                    if datafile.variables[variable].standard_name == standard_name:
                        coords.append(datafile.variables[variable])
                        break
                except AttributeError:
                    pass
    '''


class Cloud_CCI(AProduct):
    def get_file_signature(self):
        return [r'.*.nc'];

    def create_ungridded_data(self, filenames, variable):
        from data_io.netcdf import read_many_files, get_metadata
        from data_io.ungridded_data import Coord

        variables = read_many_files(filenames, [variable, "lat", "lon", "time"], dim="pixel_number") #i.e. datafile.variables[usr_variable]
        coords = []
        coords.append(Coord(variables["lon"], get_metadata(variables["lon"]), "X"))
        coords.append(Coord(variables["lat"], get_metadata(variables["lat"]), "Y"))
        coords.append(Coord(variables["time"], get_metadata(variables["time"]), "T"))
        return UngriddedData(variables[variable], get_metadata(variables[variable]), coords)

def __get_class(filenames, product=None):
    '''
    Identify the subclass of L{AProduct} to a given product name if specified.
    If the product name is not specified, the routine uses the signature (regex)
    given by get_file_signature() to infer the product class from the filenames.

    Note, only the first filename of the list is use here.

    @param filenames: list of filenames
    @param product: name of the product
    @return: a subclass of L{AProduct}
    '''

    import re

    product_cls = None
    for cls in AProduct.__subclasses__():

        if product is None:
            # search for a pattern that matches
            patterns = cls().get_file_signature()
            for pattern in patterns:
                if re.match(pattern,filenames[0],re.I) is not None:
                    product_cls = cls
                    break
        else:
            if product == cls.__name__:
                product_cls = cls

    return product_cls


def get_data(filenames, variable, product=None):
    '''
    Top level routine for calling the correct product's create_ungridded_data routine.
    @param product: The product to read data from - this should be a string which matches the name of one of the subclasses of AProduct
    @param filenames: A list of filenames to read data from
    @param variable: The variable to create the UngriddedData object from
    @return: An Ungridded data variable
    '''

    product_cls = __get_class(filenames, product)

    if product_cls is None:
        raise(NotImplementedError)
    else:
        data = product_cls().create_ungridded_data(filenames, variable)
    return data