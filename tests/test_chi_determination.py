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
test_fs.chi_angle_difference = 28.0
test_fs.chi_image_dimensions = (516, 516)
test_fs.chi_position_difference = 22
test_fs.r_mm = 0.6206397335642895
pix_size_um = float(h5grab_data(file=test_fs.file,
                                data_loc='zone_plate/detector_pixel_size'))
test_fs.pix_size_um = pix_size_um
kev = 9
D_um = 100
d_rN_nm = 20



class ChiDeterminationTestCase(unittest.TestCase):

    def test_chis(self):
        chis(test_fs)
        chi, focal_length_mm, NA_mrads, broadening_in_pix = test_fs.testing_chi_output
        self.assertEqual(chi, 80.88894092508293)
        self.assertEqual(focal_length_mm, 21.776968802074727)
        self.assertEqual(NA_mrads, 3.4440054849531965)
        self.assertEqual(broadening_in_pix, 0.1424991097716869)





if __name__ == '__main__':
    unittest.main()