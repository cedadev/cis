import logging

defaultdeletechars = """~!@#$%^&*=+~\|]}[{'; /?.>,<"""

AERONET_HEADER_LENGTH = {"AERONET-SDA/2" : 5, "AERONET/2" : 5, "MAN-SDA/2" : 5, "MAN/2" : 5,
                         "AERONET-SDA/3" : 7, "AERONET/3" : 7}
AERONET_MISSING_VALUE = {"AERONET-SDA/2" : 'N/A', "AERONET/2" :'N/A', "MAN-SDA/2" : -999.0, "MAN/2" : (-999.0, -10000),
                         "AERONET-SDA/3" : -999.0, "AERONET/3" : -999.0}

V2_HEADER = "Version 2 Direct Sun Algorithm"
V3_HEADER = "AERONET Version 3;"

AERONET_COORDINATE_RENAME = {
    "Date(dd:mm:yy)" : "date",
    "Date(dd-mm-yy)" : "date",
    "Date(dd:mm:yyyy)" : "date",
    "Date(dd-mm-yyyy)" : "date",
    "Date_(dd:mm:yy)" : "date",
    "Date_(dd-mm-yy)" : "date",
    "Date_(dd:mm:yyyy)" : "date",
    "Date_(dd-mm-yyyy)" : "date",
    "Time(hh:mm:ss)" : "time",
    "Time(hh-mm-ss)" : "time",
    "Time_(hh:mm:ss)" : "time",
    "Time_(hh-mm-ss)" : "time",
    "Latitude" : "latitude",
    "Longitude" : "longitude",
    "Site_Latitude(Degrees)" : "latitude",
    "Site_Longitude(Degrees)" : "longitude",
    "Site_Elevation(m)" : "altitude",
}

def get_slice_of_lines_from_file(filename, start, end):
    """Grab a subset of lines from a file, defined using slice-style start:end.

    This uses less memory than the equivalent linecache.getline()."""
    from itertools import islice
    with open(filename) as fileobj:
        return list(islice(fileobj, start, end))

def get_aeronet_version(filename):
    """
    Classifies the format of an Aeronet file based on it's header.
    :param filename: Full path to the file to read.
    :return str: AERONET or MAN, followed by an optional -SDA, and /# where # is the version number.
    """
    from cis.exceptions import FileFormatError

    first_line, second_line = get_slice_of_lines_from_file(filename, 0, 2)

    man = "Maritime Aerosol Network" in first_line
    sda = "SDA" in first_line

    if man:
        return "MAN-SDA/2" if sda else "MAN/2"

    if first_line.startswith(V3_HEADER):
        return "AERONET-SDA/3" if sda else "AERONET/3"

    if second_line.startswith(V2_HEADER):
        return "AERONET-SDA/2" if sda else "AERONET/2"

    raise FileFormatError(["Unable to determine Aeronet file version", filename],
                          "Unable to determine Aeronet file version " + filename)


def get_aeronet_file_variables(filename, version=None):
    """
    Return a list of valid Aeronet file variables with invalid characters removed. We need to remove invalid characters
    primarily for writing back out to CF-compliant NetCDF.
    :param filename: Full path to the file to read
    :return: A list of Aeronet variable names in the order they appear in the file
    """
    from collections import Counter

    if version is None:
        version = get_aeronet_version(filename)

    try:
        first_line, second_line = get_slice_of_lines_from_file(filename, AERONET_HEADER_LENGTH[version]-1,
                                                               AERONET_HEADER_LENGTH[version]+1)
    except ValueError:
        # Aeronet files can, for some reason, contain no data
        return []

    variables = first_line.replace("\n", "").split(",")

    # The SDA files don't list all of the columns
    if variables[-1] == "Exact_Wavelengths_for_Input_AOD(um)" or variables[-1] == "Exact_Wavelengths_for_Input_AOD(nm)":
        original_name = variables[-1]

        # Find the number of wavelengths from the first data line
        values = second_line.split(",")
        n_wavelengths = int(values[len(variables)-2])
        for i in range(n_wavelengths-1):
            variables.append(original_name)

    repeated_items = {var:-1 for var, num in Counter(variables).items() if num > 1}

    final_variables = []
    for var in variables:
        # Add a numerical counter to repeated variable names
        if var in repeated_items:
            repeated_items[var] += 1
            var += ".{}".format(repeated_items[var])

        # Remove nonstandard characters
        for char in defaultdeletechars:
            var = var.replace(char, "")

        var = var.strip()

        # Enforce standardised names for the coordinate fields
        try:
            final_variables.append(AERONET_COORDINATE_RENAME[var])
        except KeyError:
            final_variables.append(var)

    return final_variables


def load_multiple_aeronet(filenames, variables=None):
    from cis.utils import add_element_to_list_in_dict, concatenate

    adata = {}

    for filename in filenames:
        logging.debug("reading file: " + filename)

        # reading in all variables into a dictionary:
        # a_dict, key: variable name, value: list of masked arrays
        a_dict = load_aeronet(filename, variables)
        for var in list(a_dict.keys()):
            add_element_to_list_in_dict(adata, var, a_dict[var])

    for var in list(adata.keys()):
        adata[var] = concatenate(adata[var])

    return adata


def load_aeronet(filename, variables=None):
    """
    loads aeronet lev 2.0 csv file.

        Originally from http://code.google.com/p/metamet/
        License: GNU GPL v3

    :param filename: data file name
    :param variables: A list of variables to return
    :return: A dictionary of variables names and numpy arrays containing the data for that variable
    """
    import numpy as np
    from numpy import ma
    from datetime import datetime, timedelta
    from cis.time_util import cis_standard_time_unit
    from cis.exceptions import InvalidVariableError

    std_day = cis_standard_time_unit.num2date(0)

    version = get_aeronet_version(filename)
    ordered_vars = get_aeronet_file_variables(filename, version)
    if len(ordered_vars) == 0:
        return {}

    def date2daynum(datestr):
        the_day = datetime(int(datestr[-4:]), int(datestr[3:5]), int(datestr[:2]))
        return float((the_day - std_day).days)

    def time2fractionalday(timestr):
        td = timedelta(hours=int(timestr[:2]), minutes=int(timestr[3:5]), seconds=int(timestr[6:8]))
        return td.total_seconds()/(24.0*60.0*60.0)

    try:
        rawd = np.genfromtxt(filename, skip_header=AERONET_HEADER_LENGTH[version], delimiter=',', names=ordered_vars,
                             converters={0: date2daynum, 1: time2fractionalday, 'Last_Processing_Date': date2daynum},
                             dtype=np.float64, missing_values=AERONET_MISSING_VALUE[version], usemask=True,
                             invalid_raise=False)
        # Turn off exceptions for invalid lines as they're not uncommon in Aeronet files
    except (StopIteration, IndexError) as e:
        raise IOError(e)

    lend = len(rawd)
    # The date and time column are already in days since cis standard time, and fractional days respectively, so we can
    # just add them together
    # Find the columns by number rather than name as some older versions of numpy mangle the special characters
    datetimes = rawd[rawd.dtype.names[0]] + rawd[rawd.dtype.names[1]]

    # Geolocation information is stored in different places for different file versions
    if man:
        # MAN data lists the lat/lon in each line
        lon = rawd["Longitude"]
        lat = rawd["Latitude"]
        alt = 0.

    elif version == 2:
        # Specified in header
        metadata = get_file_metadata(filename)
        lon = np.zeros(lend) + float(metadata.misc[2][1].split("=")[1])
        lat = np.zeros(lend) + float(metadata.misc[2][2].split("=")[1])
        alt = np.zeros(lend) + float(metadata.misc[2][3].split("=")[1])

    elif version == 3:
        # Geolocation now in each line
        lon = np.unique(rawd[rawd.dtype.names[ordered_vars.index("Site_Longitude(Degrees)")]])
        lat = np.unique(rawd[rawd.dtype.names[ordered_vars.index("Site_Latitude(Degrees)")]])
        alt = np.unique(rawd[rawd.dtype.names[ordered_vars.index("Site_Elevation(m)")]])

    data_dict = {}
    if variables is not None:
        for key in variables:
            try:
                # Again, we can't trust the numpy names so we have to use our pre-read names to index the right column
                data_dict[key] = rawd[rawd.dtype.names[ordered_vars.index(key)]]
            except ValueError:
                raise InvalidVariableError(key + " does not exist in " + filename)

    data_dict["datetime"] = ma.array(datetimes)
    data_dict["longitude"] = ma.array(lon)
    data_dict["latitude"] = ma.array(lat)
    data_dict["altitude"] = ma.array(alt)

    return data_dict


def get_file_metadata(filename, variable='', shape=None):
    file = open(filename)
    from cis.data_io.ungridded_data import Metadata

    if variable is None:
        variable = ''
    version = get_aeronet_version(filename)
    metadata = Metadata(name=variable, long_name=variable, shape=shape)
    lines = []
    for i in range(0, AERONET_HEADER_LENGTH[version]-1):
        lines.append(file.readline().replace("\n", "").split(","))
    metadata.misc = lines
    return metadata
