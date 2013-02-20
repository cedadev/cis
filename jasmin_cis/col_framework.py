from abc import ABCMeta, abstractmethod

class Colocator(object):
    '''
    Class which provides a method for performing colocation. This just defines the interface which
    the subclasses must implement.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def colocate(self, points, data, constraint, kernel):
        '''

        @param points:
        @param data:
        @param constraint:
        @param kernel:
        @return:

        Example
        -------

        return [r'.*CODE*.nc']
        This will match all files with a name containing the string 'CODE' and with the 'nc' extension.

        '''

class Kernel(object):
    '''
    Class which provides a method for performing colocation. This just defines the interface which
    the subclasses must implement.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def kernel(self, point, data):
        '''
        @return: a list of regex to match the product's file naming convention.

        Example
        -------

        return [r'.*CODE*.nc']
        This will match all files with a name containing the string 'CODE' and with the 'nc' extension.

        '''

class Constraint(object):
    '''
    Class which provides a method for performing colocation. This just defines the interface which
    the subclasses must implement.
    '''
    __metaclass__ = ABCMeta

    def __init__(self):
        import numpy as np
        self.fill_value = np.Infinity

    @abstractmethod
    def constraint(self, point, data):
        '''
        @return: a list of regex to match the product's file naming convention.

        Example
        -------

        return [r'.*CODE*.nc']
        This will match all files with a name containing the string 'CODE' and with the 'nc' extension.

        '''


def __get_class(parent_class, name=None):
    '''
    Identify the subclass of L{AProduct} to a given product name if specified.
    If the product name is not specified, the routine uses the signature (regex)
    given by get_file_signature() to infer the product class from the filename.

    Note, only the first filename of the list is use here.

    @param filename: A single filename
    @param product: name of the product
    @return: a subclass of L{AProduct}
    '''
    import plugin
    from jasmin_cis.exceptions import ClassNotFoundError
    import logging

    all_classes = plugin.find_plugin_classes(parent_class, 'jasmin_cis.col_implementation')
    product_cls = None
    for cls in all_classes:

        if name is None:
            # Use default
            pass
        else:
            # Method specified directly
            if name == cls.__name__:
                logging.debug("Selected class " +  cls.__name__)
                return cls

    raise ClassNotFoundError("Method cannot be found")


def get_constraint(method=None):
    '''
    Top level routine for calling the correct product's create_ungridded_data routine.

    @param product: The product to read data from - this should be a string which matches the name of one of the subclasses of AProduct
    @param filenames: A list of filenames to read data from
    @param variable: The variable to create the UngriddedData object from
    @return: An Ungridded data variable
    '''
    constraint_cls = __get_class(Constraint, method)
    return constraint_cls()

def get_kernel(method=None):
    '''
    Top level routine for calling the correct product's create_ungridded_data routine.

    @param product: The product to read data from - this should be a string which matches the name of one of the subclasses of AProduct
    @param filenames: A list of filenames to read data from
    @param variable: The variable to create the UngriddedData object from
    @return: An Ungridded data variable
    '''
    kernel_cls = __get_class(Kernel, method)
    return kernel_cls()

def get_colocator(method=None):
    '''
    Top level routine for calling the correct product's create_ungridded_data routine.

    @param product: The product to read data from - this should be a string which matches the name of one of the subclasses of AProduct
    @param filenames: A list of filenames to read data from
    @param variable: The variable to create the UngriddedData object from
    @return: An Ungridded data variable
    '''
    colocate_cls = __get_class(Colocator, method)
    return colocate_cls()
