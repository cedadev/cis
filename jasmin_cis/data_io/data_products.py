from abc import ABCMeta, abstractmethod
from data_io.hdf import read_hdf4
from ungridded_data import UngriddedData
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

class Cloudsat_2B_CWC_RVOD(AProduct):

    def concatenate_coords(self):
        pass

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


        # get coordinates
        lat = utils.concatenate([ hdf_vd.get_data(i) for i in vdata['Latitude'] ])
        lon = utils.concatenate([ hdf_vd.get_data(i) for i in vdata['Longitude'] ])
        alt = utils.concatenate([ hdf_sd.get_data(i) for i in sdata['Height'] ])

        arrays = []
        for i,j in zip(vdata['Profile_time'],vdata['TAI_start']):
            time = hdf_vd.get_data(i)
            start = hdf_vd.get_data(j)
            time += start
            arrays.append(time)
        time = utils.concatenate(arrays)

        return UngriddedData(sdata[usr_variable],[lat,lon,alt,time],'HDF_SD')


class NetCDF_CF(AProduct):

    def concatenate_coords(self):
        pass

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

def get_data(product, filenames, variable):
    """
        Top level routine for calling the correct product's create_ungridded_data routine.

    @param product: The product to read data from - this should be a string which matches the name of one of the subclasses of AProduct
    @param filenames: A list of filenames to read data from
    @param variable: The variable to create the UngriddedData object from
    @return: An Ungridded data variable
    """
    product_cls = None
    for cls in AProduct.__subclasses__():
        if product == cls.__name__:
            product_cls = cls
    if product_cls is None:
        raise(NotImplementedError)
    else:
        data = product_cls().create_ungridded_data(filenames, variable)
    return data