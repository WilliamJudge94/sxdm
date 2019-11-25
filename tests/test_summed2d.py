import unittest
import os
import sys

sys.path.append(os.path.dirname(__file__))
sys.path.append('../..')

from sxdm import *

test_path = os.path.dirname(__file__)
main_path = '{}/'.format(test_path)

test_data_file_path = main_path + 'test_data.h5'
pixel_analysis_checker_path = main_path + 'test_data.npy'

test_file_path = main_path+'test.h5'
variable_path = main_path + 'test_pixel_vars.pickle'
scan_numbers = [178, 178]
dataset_name = '178'
test_fs = SXDMFrameset(test_data_file_path, dataset_name, scan_numbers=scan_numbers)
create_imagearray(test_fs, center_around=-1)


class Summed2dTestCase(unittest.TestCase):
    
    def test_summed2d_all_data(self):
        output1 = summed2d_all_data(test_fs, bkg_multiplier=0)
        self.assertEqual(np.shape(output1), (516, 516))

        output2 = summed2d_all_data_v2(test_fs, bkg_multiplier=0)
        self.assertEqual(np.shape(output2), (516, 516))


if __name__ == '__main__':
    unittest.main()

