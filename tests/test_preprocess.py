import unittest
import os
import sys

sys.path.append(os.path.dirname(__file__))
sys.path.append('../..')

from sxdm import *

test_path = os.path.dirname(__file__)
main_path = '{}/'.format(test_path)
test_file_path = main_path+'test_data.h5'
test_scan_numbers = [178, 178]

class Dummy():
    pass

testing = Dummy()
testing.file = test_file_path
testing.dataset_name = 'test_178'

class PreprocessTestCase(unittest.TestCase):

    def test_initialize_scans(self):
        initialize_scans(testing,
                         scan_numbers=test_scan_numbers,
                         fill_num=4)
        self.assertEqual(testing.scan_numbers, ['0178', '0178'])

        self.assertEqual(testing.scan_theta, [56509.170099431816, 56509.170099431816])
        self.assertEqual(testing.det_smpl_theta, '02')

    def test_initialize_group(self):
        testing.scan_numbers = ['0178', '0178']
        testing.scan_theta = [56509.170099431816, 56509.170099431816]
        initialize_group(testing)
        self.assertTrue(h5path_exists(testing.file, testing.dataset_name + '/scan_numbers'))
        self.assertTrue(h5path_exists(testing.file, testing.dataset_name + '/scan_theta'))

    def test_shape_check(self):
        shape_check(testing)
        self.assertTrue(testing.shape_checker)

    def test_resolution_check(self):
        testing.scan_numbers = ['0178', '0178']
        resolution_check(testing)
        self.assertEqual(testing.res_x, 26.7974853515625)
        self.assertEqual(testing.res_y, 2110.107421875)
        self.assertEqual(testing.validation_x, True)
        self.assertEqual(testing.validation_y, True)

    def test_gaus_check(self):
        initialize_scans(testing,
                         scan_numbers=test_scan_numbers,
                         fill_num=4)

        x, y = gaus_check(testing, center_around=True, default=True)

        test_x = [56509.170099431816, 56509.170099431816]
        test_y = [452057.90625, 451941.90625]


        x_equal = all(np.equal(np.asarray(x), test_x))
        y_equal = all(np.equal(np.asarray(y), test_y))

        self.assertTrue(x_equal)
        self.assertTrue(y_equal)

if __name__ == '__main__':
    unittest.main()