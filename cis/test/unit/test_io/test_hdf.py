# Based on examples here: http://erikzaadi.com/2012/07/03/mocking-python-imports/
"""
    Tests for checking correct behaviour when Python HDF is not installed. ImportError should be raised when HDF is used
    not when CIS is first started.
"""
from nose.tools import raises
from mock import MagicMock, patch


class HDFNotInstalledTests(object):

    def setup(self):
        """
        We have to patch the sys.modules dictionary to use our mocked versions of the pyhdf library to test it not
        being installed. This creates the appropriate mocks and imports them into the namespace.
        """

        self.pyhdf_mock = MagicMock()
        self.pyhdf_mock.SD = None
        self.pyhdf_mock.HDF = None
        modules = {
            'pyhdf': self.pyhdf_mock,
            'pyhdf.SD': self.pyhdf_mock.SD,
            'pyhdf.HDF': self.pyhdf_mock.HDF
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

        from cis.data_io import hdf, hdf_vd, hdf_sd
        self.hdf_vd = hdf_vd
        self.hdf_sd = hdf_sd
        self.hdf = hdf

    def teardown(self):
        """
        Remove the patches
        """
        self.module_patcher.stop()

    @raises(ImportError)
    def test_no_pyhdf_raises_not_installed_in_VD_variables(self):
        _ = self.hdf_vd.get_hdf_VD_file_variables('some_file')

    @raises(ImportError)
    def test_no_pyhdf_raises_not_installed_in_VD_read(self):
        _ = self.hdf_vd.read('some_file', 'some_variable')

    @raises(ImportError)
    def test_no_pyhdf_raises_not_installed_in_SD_variables(self):
        _ = self.hdf_sd.get_hdf_SD_file_variables('some_file')

    @raises(ImportError)
    def test_no_pyhdf_raises_not_installed_in_SD_read(self):
        _ = self.hdf_sd.read('some_file', 'some_variable')

    @raises(ImportError)
    def test_no_pyhdf_raises_not_installed_in_HDF_get_metadata(self):
        _ = self.hdf.get_hdf4_file_metadata('some_file')
