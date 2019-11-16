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
testing.dataset_name = '178'


scan_numbers = [178, 178]
dataset_name = 'test_178'

test_fs = SXDMFrameset(test_file_path, dataset_name, scan_numbers = scan_numbers)



class MainTestCase(unittest.TestCase):

    def test_chis(self):
        output = test_fs.image_data_dimensions()

        self.assertEqual(output, (516, 516))

    def test_frame_shape(self):

        output = test_fs.frame_shape()
        print(output)

        self.assertEqual(output, (2, 2, 11))

    def test_gaus_checker(self):
        pass
        #test_fs.gaus_checker(center_around=1, default=True)
        #x, y = test_fs.mda_roi_gaus_check
        #x_true = np.array_equal(x, [56509.170099431816, 56509.170099431816])
        #y_true = np.array_equal(y, [452057.90625, 451941.90625])
        #self.assertTrue(x_true)
        #self.assertTrue(y_true)


if __name__ == '__main__':
    unittest.main()