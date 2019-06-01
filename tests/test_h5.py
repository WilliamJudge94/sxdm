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
        h5create_dataset(file, 'group1/group2/test_data1', [0])

    def test_h5grab_data(self):
        file = test_file_path
        h5create_dataset(file, 'group1/group2/test_data2', [100])
        data = h5grab_data(file, 'group1/group2/test_data2')
        self.assertEqual(data, [100])

    def test_h5del_data(self):
        file = test_file_path
        h5create_dataset(file, 'group1/group2/test_data3', [100])
        h5del_data(file, 'group1/group2/test_data3')
        data = h5grab_data(file, 'group1/group2/test_data3')
        self.assertEqual(data, [0])

    def test_h5replace_data(self):
        file = test_file_path
        h5create_dataset(file, 'group1/group2/test_data4', [400, 345])
        h5replace_data(file, 'group1/group2/test_data4', [123, 999])
        data = h5grab_data(file, 'group1/group2/test_data4')
        equality = all(np.equal(data, [123, 999]))
        self.assertTrue(equality)

    def test_h5get_image_destination(self):
        file = main_path +'test_data.h5'
        scan_numbers = [178, 178]
        dataset_name = 'test_178'
        test_fs = SXDMFrameset(file, dataset_name, scan_numbers=scan_numbers)

        row = 1
        column = 9

        create_imagearray(test_fs, True)

        pix = grab_pix(array=test_fs.image_array, row=row, column=column, int_convert=True)
        destination = h5get_image_destination(self=test_fs, pixel=pix)
        print(destination)
        equality = destination == ['images/0178/165137', 'images/0178/165144']
        self.assertTrue(equality)


    @classmethod
    def tearDownClass(cls):
        file = test_file_path
        h5delete_file(file)


if __name__ == '__main__':
    unittest.main()
