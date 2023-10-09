import logging
import numpy as np
from cis.data_io.products.AProduct import AProduct
from cis.data_io.netcdf import read_many_files_individually
from cis.data_io.ungridded_data import UngriddedCoordinates, UngriddedData
import cis.utils as utils

def get_metadata_EC(var,optional_standard_name=None):
    """
    Retrieves all metadata

    :param var: the Variable to read metadata from
    :optional_standard_name: standard name if required, 
        for example in case where product contains standard_name not accepted as standard
    :return: A metadata object
    """
    from cis.data_io.ungridded_data import Metadata
    from cis.utils import set_standard_name_if_valid
    from cis.data_io.netcdf import find_missing_value

    missing_value = find_missing_value(var)
    standard_attributes = ['long_name', 'units','missing_value']

    attrs = {attr: getattr(var, attr, "") for attr in standard_attributes}

    shape = getattr(var, "shape", None)
    if shape is None:
        try:
            shape = (var._recLen[0],)
        except AttributeError:
            shape = ()
    metadata = Metadata(
        var._name,
        long_name=attrs['long_name'],
        units=attrs['units'],
        missing_value=missing_value,
        #missing_value=attrs['missing_value'],
        shape=shape,
        history='',#attrs['history'],
        misc={k: getattr(var, k) for k in var.ncattrs() if k not in standard_attributes})

    # Only set the standard name if it's CF compliant
    if optional_standard_name is None:
        set_standard_name_if_valid(metadata, var._name)
    else:
        set_standard_name_if_valid(metadata, optional_standard_name)
    #metadata.standard_name = var._name

    return metadata



################################################################
class EarthCARE_MSI_ATL(AProduct):
    """
    A class for creating data object model for supported EarthCARE data products.

    Currently most data in MSI_RGR_1C, MSI_XXX_2A, ATL_NOM_1B and ATL_XXX_2A products can be visualised.

    In cases where data has dimensions such that it needs to be visualised
        by indexing the values one by one, the user may append a special string
        and the required index into the data, 
        to the required field. A default index of 0 is used if this is not specified.
        For eg, band index 3(band number 4) for pixel_values field in MSI_RGR_1C, 
            can be specified using pixel_vales_BANDNUM_3.
    """

    # storage structure: (dimname, recognised string, expected dimension position)
    # ATL_TC__2A,ATL_AER_2A have class as 3rd dim
    # MSI_AOT_2A has aerosol_components
    m_listOfKnownDims=[('class','_CLASSNUM_',2),('aerosol_components','_AEROSOL_COMPONENTSNUM_',2),
                       ('band','_BANDNUM_',0), ('VNS_band','_BANDNUM_',0),
                       ('background','_BACKGROUNDNUM_',1)]

    def get_file_signature(self):
        product_names = ['ATL_CTH_2A','ATL_EBD_2A','ATL_FM__2A',
                         'ATL_ICE_2A','ATL_TC__2A','ATL_AER_2A','ATL_ALD_2A',
                        'MSI_AOT_2A','MSI_COP_2A','MSI_CM__2A',
                        'MSI_RGR_1C',
                        'ATL_NOM_1B'
                        ]
        regex_list = [r'.*' + product + r'.*.h5' for product in product_names]
        return regex_list

    def get_file_format(self, filename):
        return "h5/NetCDF/EarthCARE_MSI_ATL"

    def _create_coord_list(self, filenames, variable=None):
        """
        Function to create coords with matching dimensions to variable passed in by user.
        """
        #from cis.data_io.netcdf import read_many_files_individually
        from cis.data_io.Coord import Coord, CoordList
        from cis.exceptions import InvalidVariableError
        from cis.data_io.netcdf import get_data
        from cis.data_io.ungridded_data import Metadata

        coords = CoordList()

        b_altitude_found=False
        height_var_name=None
        time_var_name="ScienceData/time"
        try:
            longitude_var_name="ScienceData/longitude"
            latitude_var_name="ScienceData/latitude"
            # variables = ["ScienceData/longitude","ScienceData/latitude","ScienceData/time"]
            variables = [longitude_var_name,latitude_var_name,time_var_name]
            data = read_many_files_individually(filenames, variables)
        except InvalidVariableError:
            # try ATL_NOM_1B
            # height_raw is not required dimension for visualising in ATL_NOM_1B for now.
            longitude_var_name="ScienceData/ellipsoid_longitude"
            latitude_var_name="ScienceData/ellipsoid_latitude"
            #height_var_name="ScienceData/sample_altitude"
            #variables = [longitude_var_name,latitude_var_name,time_var_name,height_var_name]
            variables = [longitude_var_name,latitude_var_name,time_var_name]
            try:
                data = read_many_files_individually(filenames, variables)
                #b_altitude_found = True
                #sampleAltitudeData[height_var_name] = data[height_var_name]
            except InvalidVariableError:
                if variable is not None:
                    logging.info("Error reading variables for {}".format( str(variable) ) )
                else:
                    logging.info("Error reading variables for creating coords.")
                return coords
            except:
                logging.info("Error reading variables for creating coords.")
                return coords
        except:
            logging.info("Error reading variables for creating coords.")
            return coords

        if variable is not None:
            reqdVarData = read_many_files_individually(filenames, [variable])
            logging.info("Listing coordinates for variable: {}".format( str(variable) ) )
            aVarMetadata = get_metadata_EC(reqdVarData[variable][0])
            #logging.info(str(aVarMetadata.shape))
            requiredShape = aVarMetadata.shape
        else:
            logging.info("Create coords with no variable given.")

        foundKnownDim=False

        if variable is not None:
            #check the dimensions of variable to be plotted
            #logging.info(str(reqdVarData[variable][0].dimensions))
            #logging.info("var dim name(s)")
            dimnames = tuple([str(dimname) for dimname in reqdVarData[variable][0].dimensions])
            #logging.info(var._recdimname)
            #logging.info(str(dimnames))

            #ignore class dimension, if in required variable
            #if ( 3 == len(dimnames) ):
            # aKnownDim[2] is expected dim pos, aKnownDim[0] is dimname 
            for aKnownDim in self.m_listOfKnownDims:
                if ( ( len(dimnames) > aKnownDim[2] ) 
                       and ( reqdVarData[variable][0].dimensions[aKnownDim[2]] == aKnownDim[0]  ) ):
                    #logging.info(reqdVarData[variable][0].dimensions[aKnownDim[2]] +" is indexed at"+ 
                    #            str(aKnownDim[2]) + "dim, ignore that to create coords")
                    logging.info("{} is indexed at {} dim, ignore that to create coords".
                                 format(reqdVarData[variable][0].dimensions[aKnownDim[2]],
                                        str(aKnownDim[2])))
                    foundKnownDim=True
                    requiredShapeList=list(requiredShape)
                    del requiredShapeList[aKnownDim[2]]
                    requiredShape=tuple(requiredShapeList)
                    logging.info(str(requiredShape))


        longitude_data = data[longitude_var_name][0][:]
        if( (variable is not None) and (len(longitude_data.shape) > len(requiredShape) ) ):
            logging.info("longitude data has more dims than that of required data, not adding to coords")
        else:
            #expand dimensions if variable is more than 1D
            if( (variable is not None) and (len(longitude_data.shape) < len(requiredShape) ) ):
                logging.info("Expand longitude")
                longitude_data_expanded = utils.expand_1d_to_2d_array(longitude_data, requiredShape[1], axis=1)
            else:
                longitude_data_expanded = longitude_data
            longitude_data_expanded_metadata = get_metadata_EC(data[longitude_var_name][0],"longitude")
            longitude_data_expanded_metadata.shape = longitude_data_expanded.shape
            coords.append(Coord(longitude_data_expanded, 
                                longitude_data_expanded_metadata,"X"))

        latitude_data = data[latitude_var_name][0][:]
        if( (variable is not None) and (len(latitude_data.shape) > len(requiredShape) ) ):
            logging.info("latitude data has more dims than that of required data, not adding to coords")
        else:
            #expand dimensions if variable is more than 1D
            if( (variable is not None) and (len(latitude_data.shape) < len(requiredShape) ) ):
                logging.info("Expand latitude")
                latitude_data_expanded = utils.expand_1d_to_2d_array(latitude_data, requiredShape[1], axis=1)
            else:
                latitude_data_expanded = latitude_data
            latitude_data_expanded_metadata = get_metadata_EC(data[latitude_var_name][0],"latitude")
            latitude_data_expanded_metadata.shape = latitude_data_expanded.shape
            coords.append(Coord(latitude_data_expanded,
                                latitude_data_expanded_metadata,"Y"))

        time_data_masked = data[time_var_name][0][:]
        time_data_expanded=None
        b_is_time_data_of_reqd_dim = False
        if( (variable is not None) and (len(time_data_masked.shape) < len(requiredShape) ) ):
            logging.info("Expand time")
            time_data_expanded = utils.expand_1d_to_2d_array(time_data_masked, requiredShape[1], axis=1)
            b_is_time_data_of_reqd_dim = True
        elif ( (variable is not None) and (time_data_masked.shape == requiredShape) ):
            time_data_expanded = time_data_masked
            b_is_time_data_of_reqd_dim = True
        elif (variable is not None):
            logging.info("time data shape not matching required data shape")
        #coords.append(self._fix_time(Coord(time_data_expanded, get_metadata_EC(data[variables[2]][0]), "T")))
        if ( True == b_is_time_data_of_reqd_dim ):
            time_data_expanded_metadata = get_metadata_EC(data[time_var_name][0])
            time_data_expanded_metadata.shape = time_data_expanded.shape
            coords.append(self._fix_time(Coord(time_data_expanded, time_data_expanded_metadata, "T")))

        sampleAltitudeData=None
        if( False == b_altitude_found ):
            height_var_name="ScienceData/height"
            #b_altitude_found=False
            try:
                sampleAltitudeData = read_many_files_individually(filenames, [height_var_name])
                b_altitude_found = True
            except InvalidVariableError:
                height_var_name="ScienceData/sample_altitude" # for ATL_NOM_1B
                try:
                    sampleAltitudeData = read_many_files_individually(filenames, [height_var_name])
                    b_altitude_found = True
                except InvalidVariableError:
                    logging.info("unknown exception when reading height")
                    pass
                except:
                    logging.info("unknown exception when reading height")
                    pass
                pass
            except:
                logging.info("unknown exception when reading height")
                pass

        if ( True == b_altitude_found ) :
            #sampleAltitude_metadata = get_metadata_EC(sampleAltitudeData[height_var_name][0])
            sampleAltitude_metadata = get_metadata_EC(sampleAltitudeData[height_var_name][0],"height")
            if( (variable is not None) and (sampleAltitude_metadata.shape==requiredShape) ):
                height_metadata = Metadata("altitude",long_name=sampleAltitude_metadata.long_name,
                        units=sampleAltitude_metadata.units,
                        missing_value=sampleAltitude_metadata.missing_value,
                        shape=sampleAltitude_metadata.shape,
                        history=''
                        )
                coords.append(Coord(sampleAltitudeData[height_var_name][0][:], height_metadata ,"Z"))
                variables.append(height_var_name)
                logging.info("Added height coord from variable {}".format(height_var_name))
            elif (variable is not None):
                logging.info("{} found, but not same as required dims, so not adding height coord.".format(height_var_name))
        else:
            logging.info("no height data found")
            # For ATL_2A, if  required data is 2D i.e. one more than original longitude data dim, which is usually along_track only,
            # , then add a range coord in the required data dims ?
            # eg: ScienceData/aerosol_layer_mean_backscatter_355nm in ATL_ALD_2A
            # if not a known dim from the predefined list
            if ( (variable is not None) and (len(longitude_data.shape) == len(requiredShape)-1 ) and ( False == foundKnownDim )):
                custom_data=np.arange(0,requiredShape[1])
                custom_data_expanded=utils.expand_1d_to_2d_array(custom_data, requiredShape[0], axis=0)
                zs_metadata = Metadata("altitude",long_name="index_z",
                units=None,
                missing_value=None,
                #missing_value=attrs['missing_value'],
                shape=custom_data_expanded.shape,
                history=''
                )
                coords.append(Coord(custom_data_expanded, zs_metadata , "Z"))
                logString="Created custom height dimension with dimensions {} using {}".format(str(custom_data_expanded.shape), dimnames[1])
                logging.warning(logString)

        if not coords:
            # check current shape or dimensions, if required data is 1d, then just plot as 1d data, 
            # example MSI_RGR_1C - solar_spectral_irradiance - across_track
            # if 1D and across_track then plot as required
            if ( (variable is not None) and (len(requiredShape) == 1 ) ):
                logging.info("no matching coords found ")
                custom_data=np.arange(0,requiredShape[0])
                xs_metadata = Metadata("index_x",long_name="index_x",
                units=None,
                missing_value=None,
                #missing_value=attrs['missing_value'],
                shape=custom_data.shape,
                history=''
                )
                coords.append(Coord(custom_data,xs_metadata , "X"))

        logging.info("Coords:")
        for coord in coords:
            logging.info("{}-{}".format(coord.standard_name,coord.data.shape))

        return coords

    def create_coords(self, filenames, variable=None):
        """
        Reads the coordinates from one or more files.
        Coordinates data may be extended to match dimensions of input variable.
        Only data with dimensions that can be adjusted to match dimensions of input variable are added to the coordinates set.

        :param list filenames: List of filenames to read coordinates from
        :param str variable: Variable to visualise.
        return: :class:`.CommonData` object
        """
        return UngriddedCoordinates(self._create_coord_list(filenames,variable))

    def _fix_time(self, coord):
        import datetime as dt
        coord.convert_TAI_time_to_std_time(dt.datetime(2000, 1, 1, 0, 0, 0))
        return coord

    def create_data_object(self, filenames, variable):
        """
        Create and return an :class:`.CommonData` object for a given variable from one or more files.    

        :param list filenames: List of filenames of files to read
        :param str variable: Variable to read from the files, variable with more than 3 dimensions is not supported.
        :return: An :class:`.CommonData` object representing the specified variable

        :raise FileIOError: Unable to read a file
        :raise InvalidVariableError: Variable not present in file
        """
        from cis.data_io.netcdf import get_data
        from cis.data_io.ungridded_data import Metadata
        from cis.data_io.Coord import Coord, CoordList
        from cis.utils import create_masked_array_for_missing_data
        from cis.exceptions import InvalidVariableError


        thisDimNum=-1
        thisDimIndexPos=-1
        # if variable string has pre recognised dimname string in list self.m_listOfKnownDims[1]
        for AKNOWNDIM in self.m_listOfKnownDims:
            # AKNOWNDIM[1] is string dimname in user variable
            if AKNOWNDIM[1] in variable:
                thisDimNum=int(variable[-1:])#assume last number is the known dim
                #remove dimnum and string dim from the end
                nLastFew=len(AKNOWNDIM[1])+1
                variablePassed = variable
                variable=variable[:-nLastFew]
                thisDimIndexPos=AKNOWNDIM[2]
                break

        coords = self._create_coord_list(filenames,variable)
        try:
            var = read_many_files_individually(filenames, [variable])
        except InvalidVariableError:
            logging.info("InvalidVariableError when reading variable: {}".format(variable))
            return
        except:
            logging.info("unknown when reading variable: {}".format(variable))
            return

        logging.debug("get_metadata for -{}, shape {} ".format(var[variable][0].long_name,var[variable][0].shape))
        #logging.debug(var[variable][0])
        metadata = get_metadata_EC(var[variable][0])
        #if data is more than 3d, we dont support it
        dimnames = tuple([str(dimname) for dimname in var[variable][0].dimensions])
        if len(dimnames) > 3:
            logging.info("Unsupported number of dimensions")
            raise NotImplementedError("more than 3D in EarthCARE data.")
        else:
            #if 3d data and third dimname is one of predefined vars, user should input dimname_?         
            # add exceptions for such data, by reading dims and taking them off            
            # if any dimname matches known extra dims
            for AKNOWNDIM in self.m_listOfKnownDims:
                # AKNOWNDIM[1] is string dimname in user variable
                if AKNOWNDIM[0] in dimnames:
                    #we recognise this dim
                    if(-1 == thisDimNum):
                        logging.warning("The {} can be specified appending {} to the variable name, using index 0 for now.".format(AKNOWNDIM[0],AKNOWNDIM[1]))
                        thisDimNum=0
                    #slice according to dimensions of the data
                    #this_data_masked = var[variable][0][:]
                    if ( 3 == len(dimnames) ):
                        if 0 == AKNOWNDIM[2]:
                            this_data_masked = var[variable][0][thisDimNum,...]
                        elif 1 == AKNOWNDIM[2]:
                            this_data_masked = var[variable][0][:,thisDimNum,:]
                        elif 2 == AKNOWNDIM[2]:
                            this_data_masked = var[variable][0][...,thisDimNum]
                    elif ( 2 == len(dimnames) ):
                        if 0 == AKNOWNDIM[2]:
                            this_data_masked = var[variable][0][thisDimNum,...]
                        elif 1 == AKNOWNDIM[2]:
                            this_data_masked = var[variable][0][:,thisDimNum]
                    else:
                        #should never be here
                        pass
                    this_data_masked_name= metadata.long_name + AKNOWNDIM[1] +str(thisDimNum)
                    this_data_metadata = Metadata(this_data_masked_name,long_name=this_data_masked_name,
                        units=metadata.units,
                        missing_value=metadata.missing_value,
                        #missing_value=attrs['missing_value'],
                        shape=this_data_masked.shape,
                        history=''
                        )
                    return UngriddedData(this_data_masked, this_data_metadata, coords)
            else:
                if 3 == len(dimnames):
                    logging.info("unrecongnised dimension in EarthCARE 3d data.")
                    raise NotImplementedError("unrecongnised dimension in EarthCARE 3d data.")
                else:
                    this_data_masked = var[variable][0][:]
                    return UngriddedData(this_data_masked, metadata, coords)
                