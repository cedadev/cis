import iris.io.format_picker as format_picker

defaultdeletechars = """~!@#$%^&*=+~\|]}[{'; /?.>,<"""


def get_aeronet_file_variables(filename):
    """
    Return a list of valid Aeronet file variables with invalid characters removed. We need to remove invalid characters
    primarily for writing back out to CF-compliant NetCDF.
    :param filename: Full path to the file to read
    :return: A list of Aeronet variable names in the order they appear in the file
    """
    import linecache
    vars = linecache.getline(filename, 5).split(",")
    for i in range(0, len(vars)):
        for char in defaultdeletechars:
            vars[i] = vars[i].replace(char, "")
    return [var.strip() for var in vars]


def load_aeronet(fname):
    """
    loads aeronet lev 2.0 csv file.

        Originally from http://code.google.com/p/metamet/
        License: GNU GPL v3

    :param fname: data file name
    :param variables: A list of variables to return
    :return: A dictionary of variables names and numpy arrays containing the data for that variable
    """
    import numpy as np
    from datetime import datetime, timedelta
    from cis.time_util import cis_standard_time_unit

    std_day = cis_standard_time_unit.num2date(0)

    ordered_vars = get_aeronet_file_variables(fname)

    def date2daynum(datestr):
        the_day = datetime(int(datestr[-4:]), int(datestr[3:5]), int(datestr[:2]))
        return float((the_day - std_day).days)

    def time2fractionalday(timestr):
        td = timedelta(hours=int(timestr[:2]), minutes=int(timestr[3:5]), seconds=int(timestr[6:8]))
        return td.total_seconds()/(24.0*60.0*60.0)

    try:
        rawd = np.genfromtxt(fname, skip_header=5, delimiter=',', names=ordered_vars,
                             converters={0: date2daynum, 1: time2fractionalday, 'Last_Processing_Date': date2daynum},
                             dtype=np.float64, missing_values='N/A', usemask=True)
    except (StopIteration, IndexError) as e:
        raise IOError(e)

    # The date and time column are already in days since cis standard time, and fractional days respectively, so we can
    # just add them together
    # Find the columns by number rather than name as some older versions of numpy mangle the special characters
    datetimes = rawd[rawd.dtype.names[0]] + rawd[rawd.dtype.names[1]]

    metadata = []
    with open(fname) as file:
        for i in range(0, 4):
            metadata.append(file.readline().replace("\n", "").split(","))

    station = metadata[2][1].split("=")[1]
    lon = float(metadata[2][1].split("=")[1])
    lat = float(metadata[2][2].split("=")[1])
    alt = float(metadata[2][3].split("=")[1])

    data_dict = {}
    data_dict["datetime"] = datetimes
    data_dict["longitude"] = lon
    data_dict["latitude"] = lat
    data_dict["altitude"] = alt
    data_dict['station'] = station

    return data_dict, metadata, rawd


def aeronet_to_cube(filenames, callback=None):
    from cis.time_util import cis_standard_time_unit as ct
    from iris.coords import AuxCoord, DimCoord
    from iris.cube import Cube
    import iris

    for filename in filenames:

        coords, header, data_array = load_aeronet(filename)

        for data in data_array:
            # The name is text before any brackets, the units is what's after it (minus the closing bracket)
            name_units = data.name.split('(')
            name = name_units[0]
            # For Aeronet we can assume that if there are no units then it is unitless (AOT, Angstrom exponent, etc)
            units = name_units[1][:-1] if len(name_units) > 1 else '1'

            aux_coords = []
            aux_coords.append((AuxCoord(coords['longitude'], standard_name="longitude"), None))
            aux_coords.append((AuxCoord(coords['latitude'], standard_name="latitude"), None))
            aux_coords.append((AuxCoord(coords['altitude'], standard_name="altitude"), None))
            aux_coords.append((AuxCoord(coords['station'], var_name='station'), None))
            time_coord = DimCoord(coords["datetime"], standard_name='time', units=ct)

            cube = Cube(data, var_name=name, long_name=name, units=units,
                        aux_coords_and_dims=aux_coords,
                        dim_coords_and_dims=[(time_coord, 0)])

            # implement standard iris callback capability. Although callbacks
            # are not used in this example, the standard mechanism for a custom
            # loader to implement a callback is shown:
            cube = iris.io.run_callback(callback, cube,
                                        [coords, header, data_array],
                                        filename)

            # yield the cube created (the loop will continue when the next()
            # element is requested)
            yield cube


# Create a format_picker specification
aeronet_spec = format_picker.FormatSpecification(
    'Aeronet',
    format_picker.FileExtension(),
    ".lev20",
    aeronet_to_cube,
    priority=6)
