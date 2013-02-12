from abc import ABCMeta, abstractmethod

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

    @abstractmethod
    def get_file_signature(self):
        '''
        @return: a list of regex to match the product's file naming convention.

        Example
        -------

        return [r'.*CODE*.nc']
        This will match all files with a name containing the string 'CODE' and with the 'nc' extension.

        '''
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

    import products
    import re

    product_cls = None

    for cls in products.AProduct.__subclasses__():

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