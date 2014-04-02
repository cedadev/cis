from pyhdf.SD import SD, SDC, SDAttr

def set_hdf4_attr(obj, name, value):
    import types
    from pyhdf.error import HDF4Error
    # Called by the __setattr__ method of the SD, SDS and SDim objects.

    # Be careful with private attributes.
    #if name in privAttr:
#    if name[0] == '_':
#        obj.__dict__[name] = value
#        return

    # Treat everything else as an HDF attribute.
    if type(value) not in [types.ListType, types.TupleType]:
        value = [value]
    typeList = []
    for v in value:
        t = type(v)
        # Prohibit mixing numeric types and strings.
        if t in [types.IntType, types.FloatType] and \
               not types.StringType in typeList:
            if t not in typeList:
                typeList.append(t)
        # Prohibit sequence of strings or a mix of numbers and string.
        elif t == types.StringType and not typeList:
            typeList.append(t)
        else:
            typeList = []
            break
    if types.StringType in typeList:
        xtype = SDC.CHAR8
        value = value[0]
    # double is "stronger" than int
    elif types.FloatType in typeList:
        xtype = SDC.FLOAT64
    elif types.IntType in typeList:
        xtype = SDC.INT32
    else:
        raise HDF4Error, "Illegal attribute value"

    # Assign value
    try:
        a = SDAttr(obj, name)
        a.set(xtype, value)
    except HDF4Error, msg:
        raise HDF4Error, "cannot set attribute: %s" % msg


def __create_variable(hdf_file, name, data, **kwargs):
    '''
    Create a variable in the given hdf file
    
    :param hdf_file:    The hdf file in which to create the variable
    :param name:        The name of the variable
    :param data:        An (numpy) array containing the data
    '''
    # Create the variable
    var = hdf_file.create(name, SDC.FLOAT32, len(data))
    
    # Set any extra attributes
    for attr_name, value in kwargs.items():
        #att = var.attr(attr_name)
        #att.set(type(value), value)
        set_hdf4_attr(var,attr_name, value)
    # Build up a tuple of the data points
    t = ()
    for point in data:
        t = t + (point,)
    # Assign the tuple of data points to the variable
    var[0] = t
    # End access to the variable
    var.endaccess()
    
def write(obj, filename):
    '''
    Writes an object to a file
    
    :param obj:        The ungridded data object to write
    :param filename:   The filename of the file to be written 
    '''
    # Create file, open in read-write mode, and overwrite any existing data
    hdf_file = SD(filename, SDC.WRITE|SDC.CREATE|SDC.TRUNC)
    
    # Create variables
    __create_variable(hdf_file, obj.standard_name, obj.data, _FillValue=obj.missing_value, units=str(obj.units), long_name='Model Data')
    __create_variable(hdf_file, obj.coords()[0].name().title(), obj.x)
    
    if obj.y is not None:
        __create_variable(hdf_file, obj.coords()[1].name().title(), obj.y)
    
    # Close file
    hdf_file.end()