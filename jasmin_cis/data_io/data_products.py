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

    def create_ungridded_data(self, filenames, usr_variable):

        import utils
        import hdf_vd as hdf_vd
        import hdf_sd as hdf_sd

        # if filenames is not a list, make it a list of 1 element
        if not isinstance(filenames,list): filenames = [ filenames ]

        # list of variables we are interested in
        variables = [ usr_variable, 'Latitude','Longitude','TAI_start','Profile_time','Height']

        sdata = {}
        vdata = {}
        for filename in filenames:
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


        # retrieve coordinates
        lat_data = utils.concatenate([ hdf_vd.get_data(i) for i in vdata['Latitude'] ])
        lat_metadata = Coord(lat_data, hdf_vd.get_metadata(vdata['Latitude'][0]))

        lon_data = utils.concatenate([ hdf_vd.get_data(i) for i in vdata['Longitude'] ])
        lon_metadata = Coord(lon_data, hdf_vd.get_metadata(vdata['Longitude'][0]))

        alt_data = utils.concatenate([ hdf_sd.get_data(i) for i in sdata['Height'] ])
        alt_metadata = Coord(alt_data, hdf_sd.get_metadata(sdata['Height'][0]),'Y')

        arrays = []
        for i,j in zip(vdata['Profile_time'],vdata['TAI_start']):
            time = hdf_vd.get_data(i)
            start = hdf_vd.get_data(j)
            time += start
            arrays.append(time)
        time_data = utils.concatenate(arrays)
        time_metadata = Coord(time_data, hdf_vd.get_metadata(vdata['Profile_time'][0]),'X')

        return UngriddedData(sdata[usr_variable],[lat_data,lon_data,alt_data,time_data],'HDF_SD')


class NetCDF_CF(AProduct):

    def get_file_signature(self):
        return [r'.*.nc'];

    def create_ungridded_data(self, filenames, usr_variable):

        import utils
        from data_io.netcdf import read_many_files

        # if filenames is not a list, make it a list of 1 element
        if not isinstance(filenames,list): filenames = [ filenames ]

        # get variable and coords
        var, coords = read_many_files(filenames, usr_variable)

        # get coordinates
        #coords = [ read_many_files(filenames, dim) for dim in var.dimensions ]

        return UngriddedData(var, coords,'netCDF')

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


class Cloud_CCI(NetCDF_CF):
    pass

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
                print pattern
                print filenames[0]
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