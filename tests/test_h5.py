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
        destination2 = h5get_image_destination_v2(self=test_fs, pixel=pix)

        equality = destination == ['images/0178/165137', 'images/0178/165144']
        equality2 = destination2 == [('0178', '165137'), ('0178', '165144')]

        self.assertTrue(equality)
        self.assertTrue(equality2)

    def test_h5delete_file(self):
        h5create_file(main_path, 'test_deleting')
        h5delete_file('{}/test_deleting.h5'.format(test_path))

        file_check = os.path.isfile('{}/test_deleting.h5'.format(test_path))
        self.assertFalse(file_check)

    def test_h5del_group(self):
        h5create_file(main_path, 'test_deleting2')
        file = '{}/test_deleting2.h5'.format(test_path)


        h5create_group(file, 'testing_group')
        self.assertTrue(h5path_exists(file, 'testing_group'))

        h5del_group(file, 'testing_group')
        self.assertFalse(h5path_exists(file, 'testing_group'))

        h5delete_file(file)


    def test_h5set_attr(self):
        h5create_file(main_path, 'test_deleting3')
        file = '{}/test_deleting3.h5'.format(test_path)

        h5create_group(file, 'testing_group')
        h5set_attr(file, 'testing_group', 'attr_test', 'sup')

        self.assertEqual(h5read_attr(file, 'testing_group', 'attr_test'), 'sup')

        h5delete_file(file)

    def test_h5images_wra(self):
        h5create_file(main_path, 'test_deleting4')
        file = '{}/test_deleting4.h5'.format(test_path)
        images_path = '{}/test_images'.format(test_path)
        scan = '65'

        import_images(file, images_path, import_type='uint64')

        output1 = h5grab_data(file, 'images/0065/041930')

        self.assertEqual(np.shape(output1), (516, 516))

        import_images(file, images_path, force_reimport=True, import_type='float32')
        output2 = h5grab_data(file, 'images/0065/041930')

        t_or_f = np.array_equal(output1, output2)

        self.assertTrue(output1.dtype == 'uint64')

        h5delete_file(file)


    def test_import_mda(self):

        save_dir = '{}/'.format(test_path)
        save_name = 'test_deleting5'
        mda_path = '{}/test_mda'.format(test_path)
        file = '{}/test_deleting5.h5'.format(test_path)

        import_mda(mda_path, save_dir, save_name)

        first_path = h5path_exists(file, 'mda')
        second_path = h5path_exists(file, 'mda/0291')
        third_path = h5path_exists(file, 'mda/0291/D01')

        self.assertTrue(first_path)
        self.assertTrue(second_path)
        self.assertTrue(third_path)

        h5delete_file(file)

    @classmethod
    def tearDownClass(cls):
        file = test_file_path
        h5delete_file(file)


if __name__ == '__main__':
    unittest.main()
