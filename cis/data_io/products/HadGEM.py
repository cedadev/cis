from cis.data_io.products import NetCDF_Gridded


class HadGEM_PP(NetCDF_Gridded):
    """
        HadGEM plugin for reading native pp files
    """

    def get_file_signature(self):
        return [r'.*\.pp']

    @staticmethod
    def load_multiple_files_callback(cube, field, filename):
        # This method sets the var_name (used for outputting the cube to NetCDF) to the cube name. This can be quite
        #  for some HadGEM variables but most commands allow the user to override this field on output.
        var_name = cube.name()
        cube.var_name = var_name

    @staticmethod
    def load_single_file_callback(cube, field, filename):
        # This method sets the var_name (used for outputting the cube to NetCDF) to the cube name. This can be quite
        #  for some HadGEM variables but most commands allow the user to override this field on output.
        var_name = cube.name()
        cube.var_name = var_name
