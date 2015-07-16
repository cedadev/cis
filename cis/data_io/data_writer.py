class DataWriter(object):
    """
    High level class for writing data to a file
    """

    def write_data(self, data, output_file):
        """
        Write data to a file
        :param data: Data to write
        :param output_file: Output file name
        :return:
        """
        data.save_data(output_file)
