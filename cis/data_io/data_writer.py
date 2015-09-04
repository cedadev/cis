class DataWriter(object):
    """
    High level class for writing data to a file
    """

    def write_data(self, data, output_file):
        """
        Write data to a file.

        :param CommonData data: Data to write
        :param str output_file: Output file name
        """
        data.save_data(output_file)
