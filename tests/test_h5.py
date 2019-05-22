import unittest
import os
import sys

sys.path.append(os.path.dirname(__file__))
sys.path.append('../..')

from sxdm import *

test_path = os.path.dirname(__file__)
main_path = '{}/'.format(test_path)
test_file_path = main_path+'test.h5'


class H5TestCase(unittest.TestCase):
    def test_h5create_file(self):

        h5create_file(main_path, 'test')
        file_check = os.path.isfile('{}/test.h5'.format(test_path))
        self.assertTrue(file_check)

    def test_h5create_group(self):
        file = test_file_path
        h5create_group(file,'group1/group2')
        result1 = h5path_exists(file, '/group1/')
        result2 = h5path_exists(file, '/group1/group2')
        self.assertTrue(result1)
        self.assertTrue(result2)

    def test_h5group_list(self):
        file = test_file_path
        result1 = h5group_list(file)[0][0]
        result2 = h5group_list(file, 'group1')[0][0]
        self.assertEqual(result1, 'group1')
        self.assertEqual(result2, 'group2')

    def test_h5create_dataset(self):
        file = test_file_path
        h5create_dataset(file, 'group1/group2', [0])

    def test_h5create_dataset(self):
        file = test_file_path
        h5create_dataset(file, 'group1/group2/test_data', [0])




    @classmethod
    def tearDownClass(cls):
        file = test_file_path
        h5delete_file(file)


if __name__ == '__main__':
    unittest.main()
