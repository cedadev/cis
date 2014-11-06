class DataWriter(object):
    """
    High level class for writing data to a file
    """

    def write_data(self, data, output_file, _sample_points=None, _coords_to_be_written=False):
        """
        Write data to a file
        :param data: Data to write
        :param output_file: Output file name
        :param _sample_points: Sample points to use
        :param _coords_to_be_written: Write coords to file?
        :return:
        """
        data.save_data(output_file, _sample_points, _coords_to_be_written)
