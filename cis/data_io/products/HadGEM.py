from cis.data_io.products import NetCDF_Gridded


class HadGEM(NetCDF_Gridded):
    """
        HadGEM plugin which implements a callback to pass to iris when reading multiple files to allow correct merging
    """

    def get_file_signature(self):
        return [r'[a-z]{6}[\._][pamd]{2}[0-9]{4,6}.*\.nc']

    @staticmethod
    def load_multiple_files_callback(cube, field, filename):
        from iris.util import squeeze
        # We need to remove the history field when reading multiple files so that the cubes can be properly merged
        cube.attributes.pop('history')
        # We also need to remove the length one time dimension so that the cube can be merged correctly (iris preserves
        #  the value as a scalar which then gets converted back into a full coordinate again on merge).
        return squeeze(cube)