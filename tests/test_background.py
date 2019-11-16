import unittest
import os
import sys
import pickle

sys.path.append(os.path.dirname(__file__))
sys.path.append('../..')

from sxdm import *

test_path = os.path.dirname(__file__)
main_path = '{}/'.format(test_path)
test_file_path = main_path+'test.h5'


class BackgroundTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test_data_file_path = main_path + 'test_data.h5'
        scan_numbers = [178, 178]
        dataset_name = '178'

        cls.test_fs = SXDMFrameset(test_data_file_path, dataset_name, scan_numbers=scan_numbers)

        cls.test_fs.dxdy_store = {0: (5, 0), 1: (5, 0)}
        create_imagearray(self=cls.test_fs, center_around=-1)

        image_array = cls.test_fs.image_array
        row = 1
        column = 5

        pix = grab_pix(array=image_array, row=row, column=column, int_convert=True)
        cls.destination = h5get_image_destination(self=cls.test_fs, pixel=pix)

        # Background Correction
        #backgrounds = scan_background_finder(destination=destination, background_dic=self.background_dic)

        cls.test_fs.bkg = scan_background(self=cls.test_fs, amount2ave=3, multiplier=1)

        with open('{}bkg.pickle'.format(main_path), 'rb') as f:
            cls.standard_dic, cls.scan_background_var, cls.change_dic1, cls.change_dic2, cls.change_dic3 = pickle.load(f)


    def test_scan_background(self):

        dic = scan_background(self=self.test_fs, amount2ave=3, multiplier=1)
        dic1 = scan_background(self=self.test_fs, amount2ave=2, multiplier=1)
        dic2 = scan_background(self=self.test_fs, amount2ave=3, multiplier=0)
        dic3 = scan_background(self=self.test_fs, amount2ave=5, multiplier=2)

        self.assertTrue(np.array_equal(dic2array(dic), dic2array(self.standard_dic)))

        self.assertTrue(np.array_equal(dic2array(dic1), dic2array(self.change_dic1)))
        self.assertTrue(np.array_equal(dic2array(dic2), dic2array(self.change_dic2)))
        self.assertTrue(np.array_equal(dic2array(dic3), dic2array(self.change_dic3)))



    def test_scan_background_finder(self):

        out = scan_background_finder(destination=self.destination, background_dic=self.test_fs.bkg)
        self.assertTrue(np.array_equal(out, self.scan_background_var))

if __name__ == '__main__':
    unittest.main()