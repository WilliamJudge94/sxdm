import unittest
import os
import sys

sys.path.append(os.path.dirname(__file__))
sys.path.append('../..')

from sxdm import *

test_path = os.path.dirname(__file__)
main_path = '{}/'.format(test_path)
test_file_path = main_path+'test.h5'
test_data_file_path = main_path + 'test_data.h5'
pixel_analysis_checker_path = main_path + 'test_data.npy'


scan_numbers = [178, 178]
dataset_name = '178'
test_fs = SXDMFrameset(test_data_file_path,dataset_name, scan_numbers = scan_numbers)


class PixelTestCase(unittest.TestCase):

    def test_centroid_pixel_analysis(self):
        background_dic_basic = scan_background(test_fs, amount2ave=2, multiplier=1)
        create_imagearray(test_fs, center_around=-1)
        output = centroid_pixel_analysis(test_fs, 1, 1, 1, 1, 2)

        check_output = np.load(pixel_analysis_checker_path, allow_pickle=True)

        out_checker = []
        for i in range(0, 8):
            out_checker.append(np.array_equal(output[i], check_output[i]))

        self.assertTrue(all(out_checker))


if __name__ == '__main__':
    unittest.main()