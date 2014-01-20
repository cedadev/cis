
import os

TEST_FILE_PATH='/group_workspaces/jasmin/cedaproc/cis_test'
HERE = os.path.dirname(__file__)

def link_test_data():
    for test_file in os.listdir(TEST_FILE_PATH):
        src = os.path.join(TEST_FILE_PATH, test_file)
        dest = os.path.join(HERE, test_file)
        if not os.path.exists(dest):
            print 'Linking test file %s to %s' % (src, dest)
            os.symlink(src, dest)
