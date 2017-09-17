from abc import ABCMeta, abstractmethod
import logging
import traceback
from cis.data_io.aeronet import get_aeronet_file_variables
from cis.data_io.hdf import get_hdf4_file_variables
from cis.data_io.netcdf import get_netcdf_file_variables, remove_variables_with_non_spatiotemporal_dimensions
from cis import __version__
import six


@six.add_metaclass(ABCMeta)
class AProduct(object):
    """
    Abstract class for the various possible data products. This just defines the interface which
    the subclasses must implement.
    """

    # If a filename matches two data products' file signatures, the data product with the higher priority will be used
    priority = 10

    # Contains a list of valid spatiotemporal variable names
    valid_dimensions = None

    @abstractmethod
    def create_data_object(self, filenames, variable):
        """
        Create and return an :class:`.CommonData` object for a given variable from one or more files.

        :param list filenames: List of filenames of files to read
        :param str variable: Variable to read from the files
        :return: An :class:`.CommonData` object representing the specified variable

        :raise FileIOError: Unable to read a file
        :raise InvalidVariableError: Variable not present in file
        """

    @abstractmethod
    def get_file_signature(self):
        """
        This method should return a list of regular expressions, which CIS uses to decide which data
        product to use for a given file. If more than one regular expression is provided in the list then the file can
        match `any` of the expressions. The first product with a signature that matches the filename will be used.
        The order in which the products are searched is determined by the priority property, highest value first;
        internal products generally have a priority of 10.

        For example, this would match all files with a name containing the string 'CODE' and with the 'nc' extension.::

            return [r'.*CODE*.nc']

        .. note::

            If the signature has matched the framework will call :meth:`.AProduct.get_file_type_error`, this gives the
            product a chance to open the file and check the contents.

        :return: A list of regex to match the product's file naming convention.
        :rtype: list
        """

    def get_variable_names(self, filenames, data_type=None):
        """
        Get a list of available variable names from the filenames list passed in. This general implementation can be
        overridden in specific products to include/exclude variables which may or may not be relevant.
        The data_type parameter can be used to specify extra information.

        :param list filenames: List of string filenames of files to be read from
        :param str data_type: 'SD' or 'VD' to specify only return SD or VD variables from HDF files. This may take on
         other values in specific product implementations.
        :return: A set of variable names as strings
        :rtype: str
        """
        variables = []
        for filename in filenames:
            file_variables = None
            if filename.endswith(".nc"):
                file_variables = get_netcdf_file_variables(filename)
                remove_variables_with_non_spatiotemporal_dimensions(file_variables, self.valid_dimensions)
            elif filename.endswith(".hdf"):
                if data_type is None:
                    data_type = "SD"
                sd_vars, vd_vars = get_hdf4_file_variables(filename, data_type)
                file_variables = list((sd_vars or {}).keys()) + list((vd_vars or {}).keys())
            elif filename.endswith(".lev20"):
                file_variables = get_aeronet_file_variables(filename)
            variables.extend(file_variables)
        return set(variables)

    def get_file_type_error(self, filename):
        """
        Check a single file to see if it is of the correct type, and if not return
        a list of errors. If the return is None then there are no errors and
        this is the correct data product to use for this file.

        This method gives a mechanism for a data product to identify itself as the
        correct product when a specific enough file signature cannot be provided. For
        example GASSP is a type of NetCDF file and so filenames end with .nc but
        so do other NetCDF files, so the data product opens the file and looks
        for the GASSP version attribute, and if it doesn't find it returns an
        error.

        :param str filename: The filename for the file
        :return: List of errors, or None
        :rtype: list or None
        """
        return None


def __get_class(filename, product=None):
    """
    Identify the subclass of :class:`.AProduct` to a given product name if specified.
    If the product name is not specified, the routine uses the signature (regex)
    given by :meth:`get_file_signature` to infer the product class from the filename.

    Note, only the first filename of the list is use here.

    :param filename: A single filename
    :param product: name of the product
    :return: a subclass of :class:`.AProduct`
    """
    import re
    import os
    import cis.plugin as plugin
    from cis.exceptions import ClassNotFoundError

    # Ensure the filename doesn't include the path
    basename = os.path.basename(filename)

    product_classes = plugin.find_plugin_classes(AProduct, 'cis.data_io.products')
    product_classes = sorted(product_classes, key=lambda cls: cls.priority, reverse=True)

    for cls in product_classes:

        if product is None:
            # search for a pattern that matches file signature
            class_instance = cls()
            patterns = class_instance.get_file_signature()
            for pattern in patterns:
                # Match the pattern - re.I allows for case insensitive matches.
                # Appending '$' to the pattern ensures we match the whole string
                if re.match(pattern+'$', basename, re.I) is not None:
                    logging.debug("Found product class " + cls.__name__ + " matching regex pattern " + pattern)
                    errors = class_instance.get_file_type_error(filename)
                    if errors is None:
                        return cls
                    else:
                        logging.info("Product class {} is not right because {}".format(cls.__name__, errors))
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
    Top level routine for calling the correct product's :meth:`create_data_object` routine.

    :param list filenames: A list of filenames to read data from
    :param str variable: The variable to create the :class:`.CommonData` object from
    :param str product: The product to read data with - this should be a string which matches the name of one of the
     subclasses of :class:`.AProduct`. If none is supplied it is guessed from the filename signature.
    :return: A :class:`.CommonData` variable
    """
    product_cls = __get_class(filenames[0], product)

    logging.info("Retrieving data using product " + product_cls.__name__ + "...")
    try:
        data = product_cls().create_data_object(filenames, variable)
        return data
    except Exception as e:
        logging.debug("Error in product plugin %s:\n%s" % (product_cls.__name__, traceback.format_exc()))
        raise ProductPluginException("An error occurred retrieving data using the product %s. Check that this "
                                     "is the correct product plugin for your chosen data. Exception was %s: %s."
                                     % (product_cls.__name__, type(e).__name__, e.args[0]), e)


def get_variables(filenames, product=None, data_type=None):
    """
    Top level routine for calling the correct product's :meth:`get_variable_names` routine.

    :param list filenames: A list of filenames to read the variables from
    :param str product: The product to read data with - this should be a string which matches the name of one of the
     subclasses of AProduct
    :return: A set of variable names as strings
    """
    product_cls = __get_class(filenames[0], product)

    logging.info("Retrieving variables using product " + product_cls.__name__ + "...")
    try:
        variables = product_cls().get_variable_names(filenames, data_type)
        return variables
    except Exception as e:
        logging.debug("Error in product plugin %s:\n%s" % (product_cls.__name__, traceback.format_exc()))
        raise ProductPluginException("An error occurred retrieving variables using the product %s. Check that this "
                                     "is the correct product plugin for your chosen data. Exception was %s: %s."
                                     % (product_cls.__name__, type(e).__name__, e.args[0]), e)


def get_product_full_name(filenames, product=None):
    """
    Get the full name of the product which would read this file

    :param list filenames: list of filenames to read
    :param str product: specified product to use
    """

    product_cls = __get_class(filenames[0], product)
    logging.info("Retrieving product fill name using product " + product_cls.__name__ + "...")

    return "CIS/{product}/{version}".format(product=product_cls.__name__, version=__version__)


class ProductPluginException(Exception):
    """
    Represents an error which has occurred inside of a Product plugin
    """

    original_exception = None

    def __init__(self, message, original_exception):
        super(ProductPluginException, self).__init__(message)
        self.original_exception = original_exception
