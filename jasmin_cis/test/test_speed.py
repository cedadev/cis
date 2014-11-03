from unittest import TestCase
from jasmin_cis.test.test_files.data import *
from jasmin_cis.cis import col_cmd
from jasmin_cis.parse import parse_args


class TestSpeed(TestCase):

    def test_speed(self):
        return
        variable = 'loadbc'
        filename = '/home/vagrant/trac429/aerocom.HadGEM3-A-GLOMAP.A2.CTRL.annual.loadbc.2006.nc'
        sample = '/home/vagrant/trac429/aerocom.CAM4-Oslo-Vcmip5.A2.CTRL.annual.loadbc.9999.nc'
        out = 'testout.nc'
        arguments = ['col', variable+':'+filename,
                     sample+':colocator=nn', '-o', out]
        main_arguments = parse_args(arguments)
        col_cmd(main_arguments)
