from abc import ABCMeta, abstractmethod
import logging
import traceback
from jasmin_cis.data_io.aeronet import get_aeronet_file_variables
from jasmin_cis.data_io.hdf import get_hdf4_file_variables
from jasmin_cis.data_io.netcdf import get_netcdf_file_variables


class AProduct(object):
    """
    Abstract class for the various possible data products. This just defines the interface which
    the subclasses must implement.
    """
    __metaclass__ = ABCMeta

    # If a filename matches two data products' file signatures, the data product with the higher priority will be used
    priority = 10

    @abstractmethod
    def create_data_object(self, filenames, variable):
        """
        Create a an ungridded data object for a given variable from many files

        :param filenames:    List of filenames of files to read
        :param variable:    Variable to read from the files
        :return: An UngriddedData object for the specified variable

        :raise FileIOError: Unable to read a file
        :raise InvalidVariableError: Variable not present in file
        """

    @abstractmethod
    def create_coords(self, filenames):
        """
        Reads the coordinates from a bunch of files
        :param filenames: List of filenames to read coordinates from
        :return: L{CoordList} object
        """

    @abstractmethod
    def get_file_signature(self):
        """
        :return: a list of regex to match the product's file naming convention.

        Example
        -------

        return [r'.*CODE*.nc']
        This will match all files with a name containing the string 'CODE' and with the 'nc' extension.

        Additional
        ----------

        If the signature has matched the framework will call get_file_type_error(filename), this gives the product a
        chance to open the file and check the contents. If this returns None then the match is complete otherwise
        the error may be printed for the user
        """

    def get_variable_names(self, filenames, data_type=None):
        """
        Get a list of available variable names
        This can be overridden in specific products to improve on this
        """
        variables = []
        for filename in filenames:
            file_variables = None
            if filename.endswith(".nc"):
                file_variables = get_netcdf_file_variables(filename)
            elif filename.endswith(".hdf"):
                if data_type is None:
                    data_type = "SD"
                sd_vars, vd_vars = get_hdf4_file_variables(filename, data_type)
                file_variables = sd_vars + vd_vars
            elif filename.endswith(".lev20"):
                file_variables = get_aeronet_file_variables(filename)
            variables.extend(file_variables)
        return set(variables)


def __get_class(filename, product=None):
    """
    Identify the subclass of L{AProduct} to a given product name if specified.
    If the product name is not specified, the routine uses the signature (regex)
    given by get_file_signature() to infer the product class from the filename.

    Note, only the first filename of the list is use here.

    :param filename: A single filename
    :param product: name of the product
    :return: a subclass of L{AProduct}
    """
    import re
    import os
    import jasmin_cis.plugin as plugin
    from jasmin_cis.exceptions import ClassNotFoundError

    # Ensure the filename doesn't include the path
    basename = os.path.basename(filename)

    product_classes = plugin.find_plugin_classes(AProduct, 'jasmin_cis.data_io.products')
    product_classes = sorted(product_classes, key=lambda cls: cls.priority, reverse=True)

    for cls in product_classes:

        if product is None:
            # search for a pattern that matches file signature
            class_instance = cls()
            patterns = class_instance.get_file_signature()
            for pattern in patterns:
                # Match the pattern - re.I allows for case insensitive matches
                if re.match(pattern, basename, re.I) is not None:
                    logging.debug("Found product class " + cls.__name__ + " matching regex pattern " + pattern)
                    try:
                        errors = class_instance.get_file_type_error(filename)
                        if errors is None:
                            return cls
                        else:
                            logging.info("Product class {} is not right because {}".format(cls.__name__, errors))
                    except AttributeError:
                        return cls
        else:
            # product specified directly
            if product == cls.__name__:
                logging.debug("Selected product class " + cls.__name__)
                return cls
    error_message = "Product cannot be found for given file.\nSupported products and signatures are:\n"
    for cls in product_classes:
        error_message += cls().__class__.__name__ + ": " + str(cls().get_file_signature()) + "\n"
    raise ClassNotFoundError(error_message)


def get_data(filenames, variable, product=None):
    """
    Top level routine for calling the correct product's create_ungridded_data routine.

    :param product: The product to read data from - this should be a string which matches the name of one of the
    subclasses of AProduct
    :param filenames: A list of filenames to read data from
    :param variable: The variable to create the UngriddedData object from
    :return: An Ungridded data variable
    """
    product_cls = __get_class(filenames[0], product)

    logging.info("Retrieving data using product " + product_cls.__name__ + "...")
    try:
        data = product_cls().create_data_object(filenames, variable)
        return data
    except Exception as e:
        logging.error("Error in product plugin %s:\n%s" % (product_cls.__name__, traceback.format_exc()))
        raise ProductPluginException("An error occurred retrieving data using the product %s. Check that this "
                                     "is the correct product plugin for your chosen data. Exception was %s: %s."
                                     % (product_cls.__name__, type(e).__name__, e.message), e)


def get_coordinates(filenames, product=None):
    """
    Top level routine for calling the correct product's create_coords routine.

    :param product: The product to read data from - this should be a string which matches the name of one of the
    subclasses of AProduct
    :param filenames: A list of filenames to read data from
    :return: A CoordList object
    """
    product_cls = __get_class(filenames[0], product)

    logging.info("Retrieving coordinates using product " + product_cls.__name__)
    try:
        coord = product_cls().create_coords(filenames)
        return coord
    except Exception as e:
        logging.error("Error in product plugin %s:\n%s" % (product_cls.__name__, traceback.format_exc()))
        raise ProductPluginException("An error occurred retrieving coordinates using the product %s. Check that this "
                                     "is the correct product plugin for your chosen data. Exception was %s: %s."
                                     % (product_cls.__name__, type(e).__name__, e.message), e)


def get_variables(filenames, product=None):
    product_cls = __get_class(filenames[0], product)

    logging.info("Retrieving variables using product " + product_cls.__name__ + "...")
    try:
        variables = product_cls().get_variable_names(filenames)
        return variables
    except Exception as e:
        logging.error("Error in product plugin %s:\n%s" % (product_cls.__name__, traceback.format_exc()))
        raise ProductPluginException("An error occurred retrieving variables using the product %s. Check that this "
                                     "is the correct product plugin for your chosen data. Exception was %s: %s."
                                     % (product_cls.__name__, type(e).__name__, e.message), e)


class ProductPluginException(Exception):
    """
    Represents an error which has occurred inside of a Product plugin
    """

    original_exception = None

    def __init__(self, message, original_exception):
        super(ProductPluginException, self).__init__(message)
        self.original_exception = original_exception