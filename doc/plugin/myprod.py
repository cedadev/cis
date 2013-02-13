from jasmin_cis.data_io.products.AProduct import AProduct
from jasmin_cis.data_io.Coord import Coord, CoordList
from jasmin_cis.data_io.ungridded_data import UngriddedData
from jasmin_cis.data_io.ungridded_data import Metadata

import logging

class MyProd(AProduct):

    def get_file_signature(self):
        return [r'.*something*.hdf']

    def create_coords(self, filenames):

        logging.info("gathering coordinates")
        for filename in filenames:
            data1 = []
            data2 = []
            data3 = []

        logging.info("gathering coordinates metadata")
        metadata1 = Metadata()
        metadata2 = Metadata()
        metadata3 = Metadata()

        coord1 = Coord(data1,metadata1,'X') # this coordinate will be used as the 'X' axis when plotting
        coord2 = Coord(data2,metadata2,'Y') # this coordinate will be used as the 'Y' axis when plotting
        coord3 = Coord(data3,metadata3)

        return CoordList([coord1,coord2,coord3])

    def create_ungridded_data(self, filenames, variable):

        logging.info("gathering data for variable " + variable)
        for filename in filenames:
            data = []

        logging.info("gatherings metadata for variable ", + variable)
        metadata = Metadata()

        coords = self.create_coords(filenames)
        return UngriddedData(data,metadata,coords)

