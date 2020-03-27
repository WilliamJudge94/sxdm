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



class DetChanTestCase(unittest.TestCase):

    def test_disp_det_chan(self):
        disp_det_chan(test_fs.file)

        self.assertTrue(True)

    def test_setup_det_chan(self):
        detector_scan = {
            'Main_Scan': 178,
        }

        filenumber = 15

        fluor = {
            'Al': 24,
            'Co': 25,
            'Mn': 27,
            'Ni': 26,
        }

        hybrid_x = 67

        hybrid_y = 68

        xrf = {
            'Fe': 2,
            'Cu': 2,
            'Ni': 2,
            'Full': 2,
        }

        mis = {
            '2Theta': 2,
            'Relative_r_To_Detector': 2,
            'Storage_Ring_Current': 2,
        }

        roi = {
            'ROI_1': 2,
            'ROI_2': 2,
            'ROI_3': 2,
        }

        sample_theta = 2


        setup_det_chan(test_fs.file, fluor, roi, detector_scan, filenumber, sample_theta, hybrid_x, hybrid_y, mis, xrf)

        del_det_chan(test_fs.file)

        setup_det_chan(test_fs.file, fluor, roi, detector_scan, filenumber, sample_theta, hybrid_x, hybrid_y, mis, xrf)

        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()