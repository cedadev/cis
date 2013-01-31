from pyhdf.SD import SD, SDC 

def __create_variable(hdf_file, name, data):
    '''
    Create a variable in the given hdf file
    
    @param hdf_file:    The hdf file in which to create the variable
    @param name:        The name of the variable
    @param data:        An (numpy) array containing the data
    '''
    # Create the variable
    var = hdf_file.create(name, SDC.FLOAT32, len(data))
    # Give it a description
    var.description = name
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
    
    @param obj:        The ungridded data object to write
    @param filename:   The filename of the file to be written 
    '''
    # Create file, open in read-write mode, and overwrite any existing data
    hdf_file = SD(filename, SDC.WRITE|SDC.CREATE|SDC.TRUNC)
    
    # Create variables
    __create_variable(hdf_file, obj.short_name, obj.data)
    __create_variable(hdf_file, obj.coords()[0].name(), obj.x)
    
    if obj.y is not None:
        __create_variable(hdf_file, obj.coords()[1].name(), obj.y)
    
    # Close file
    hdf_file.end()