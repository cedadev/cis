from abc import ABCMeta, abstractmethod
import logging

class AProduct(object):
    '''
    Abstract class for the various possible data products. This just defines the interface which
    the subclasses must implement.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_data_object(self, filenames, variable):
        '''
        Create a an ungridded data object for a given variable from many files

        @param filenames:    List of filenames of files to read
        @param usr_variable:    Variable to read from the files
        @return: An UngriddedData object for the specified variable

        @raise FileIOError: Unable to read a file
        @raise InvalidVariableError: Variable not present in file
        '''

    @abstractmethod
    def create_coords(self, filenames):
        '''
        Reads the coordinates from a bunch of files
        @param filenames: List of filenames to read coordinates from
        @return: L{CoordList} object
        '''

    @abstractmethod
    def get_file_signature(self):
        '''
        @return: a list of regex to match the product's file naming convention.

        Example
        -------

        return [r'.*CODE*.nc']
        This will match all files with a name containing the string 'CODE' and with the 'nc' extension.

        '''


def __get_all_subclasses(cls):
    '''
    Recursively find all subclasses of a given class

    @param cls: The class to find subclasses of
    @return: A list of all subclasses
    '''
    subclasses = []
    for subclass in cls.__subclasses__():
        subclasses += __get_all_subclasses(subclass)
    subclasses += cls.__subclasses__()
    return subclasses


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
    import products
    import re
    import os
    import cis
    import plugin

    # find plugin product classes, if any
    ENV_PATH = "_".join([cis.__name__.upper(),"PLUGIN","HOME"])
    plugin_dir = os.environ.get(ENV_PATH, None)
    plugin_classes = plugin.__find_plugins(plugin_dir,__name__)

    # find built-in product classes, i.e. subclasses of L{AProduct}
    subclasses = __get_all_subclasses(products.AProduct)
    product_classes = plugin_classes + subclasses

    logging.debug("AProduct subclasses are: " + str(product_classes))

    product_cls = None
    for cls in product_classes:

        if product is None:
            # search for a pattern that matches file signature
            patterns = cls().get_file_signature()
            for pattern in patterns:
                # Match the pattern - re.I allows for case insensitive matchess
                if re.match(pattern,filenames[0],re.I) is not None:
                    logging.debug("Found product class " + cls.__name__ + " matching regex pattern " + pattern)
                    return cls
        else:
            # product specified directly
            if product == cls.__name__:
                logging.debug("Selected product class " +  cls.__name__)
                return cls

    return None


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
        logging.info("Retrieving data using product " +  product_cls.__name__)
        data = product_cls().create_data_object(filenames, variable)
    return data


def get_coordinates(filenames, product=None):
    '''
    Top level routine for calling the correct product's create_coords routine.

    @param product: The product to read data from - this should be a string which matches the name of one of the subclasses of AProduct
    @param filenames: A list of filenames to read data from
    @return: A CoordList object
    '''
    product_cls = __get_class(filenames, product)

    if product_cls is None:
        raise(NotImplementedError)
    else:
        logging.info("Retrieving coordinates using product " +  product_cls.__name__)
        coord = product_cls().create_coords(filenames)
    return coord