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


def __get_class(filename, product=None):
    '''
    Identify the subclass of L{AProduct} to a given product name if specified.
    If the product name is not specified, the routine uses the signature (regex)
    given by get_file_signature() to infer the product class from the filename.

    Note, only the first filename of the list is use here.

    @param filename: A single filename
    @param product: name of the product
    @return: a subclass of L{AProduct}
    '''
    import re
    import os
    import jasmin_cis.plugin as plugin
    from jasmin_cis.exceptions import ClassNotFoundError

    # Ensure the filename doesn't include the path
    filename = os.path.basename(filename)

    product_classes = plugin.find_plugin_classes(AProduct, 'jasmin_cis.data_io.products.products')

    for cls in product_classes:

        if product is None:
            # search for a pattern that matches file signature
            patterns = cls().get_file_signature()
            for pattern in patterns:
                # Match the pattern - re.I allows for case insensitive matches
                if re.match(pattern,filename,re.I) is not None:
                    logging.debug("Found product class " + cls.__name__ + " matching regex pattern " + pattern)
                    return cls
        else:
            # product specified directly
            if product == cls.__name__:
                logging.debug("Selected product class " +  cls.__name__)
                return cls
    error_message = "Product cannot be found for given file.\nSupported products and signatures are:\n"
    for cls in product_classes:
        error_message += cls().__class__.__name__ + ": " + str(cls().get_file_signature()) + "\n"
    raise ClassNotFoundError(error_message)


def get_data(filenames, variable, product=None):
    '''
    Top level routine for calling the correct product's create_ungridded_data routine.

    @param product: The product to read data from - this should be a string which matches the name of one of the subclasses of AProduct
    @param filenames: A list of filenames to read data from
    @param variable: The variable to create the UngriddedData object from
    @return: An Ungridded data variable
    '''
    product_cls = __get_class(filenames[0], product)

    logging.info("Retrieving data using product " +  product_cls.__name__ + "...")
    data = product_cls().create_data_object(filenames, variable)
    return data


def get_coordinates(filenames, product=None):
    '''
    Top level routine for calling the correct product's create_coords routine.

    @param product: The product to read data from - this should be a string which matches the name of one of the subclasses of AProduct
    @param filenames: A list of filenames to read data from
    @return: A CoordList object
    '''
    product_cls = __get_class(filenames[0], product)

    logging.info("Retrieving coordinates using product " +  product_cls.__name__)
    coord = product_cls().create_coords(filenames)
    return coord