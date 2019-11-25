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


class PixelTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up all variable checks
        # All 33 variables to check

        # Set up analysis function variables
        cls.median_blur_distance = 9
        cls.median_blur_height = 10
        cls.stdev_min = 35


        # Used for single pixel
        cls.row = 1
        cls.column = 5

        # Used for analysis
        cls.rows = 2
        cls.columns = 5

        # Create the background dictionary and image_array
        cls.background_dic_basic = scan_background(test_fs, amount2ave=3, multiplier=1)
        create_imagearray(test_fs, center_around=-1)

        # Grab the image_loc value
        pix = grab_pix(array=test_fs.image_array, row=cls.row, column=cls.column, int_convert=True)
        destination = h5get_image_destination(self=test_fs, pixel=pix)
        cls.images_loc = destination


        loading = load_variable_pickle(variable_path)

        cls.diffraction_pattern = loading[0]
        cls.oneDarray = loading[1]


        cls.centroid_pixel_analysis_check = loading[2]
        cls.theta_maths_check = loading[3]
        cls.chi_maths_check = loading[4]
        cls.centroid_finder_check = loading[5]
        cls.grab_pix_check = loading[6]
        cls.destination = loading[7]

        cls.sum_pixel_check = loading[8]
        cls.diff_segment_squares = loading[9]
        test_fs.diff_segment_squares = cls.diff_segment_squares

        cls.roi_pixel_analysis_check = loading[10]


        pass

    def test_centroid_pixel_analysis(self):
        # Check 9 outputs

        pass
        new = centroid_pixel_analysis(self=test_fs, row=self.row, column=self.column,
                                      median_blur_distance=self.median_blur_distance,
                                      median_blur_height=self.median_blur_height,
                                      stdev_min=self.stdev_min)

        out_checker = []
        for i in range(0, len(new)):
            out_checker.append(np.array_equal(new[i], self.centroid_pixel_analysis_check[i]))

        self.assertTrue(all(out_checker))

    def test_theta_maths(self):
        # Check 4 outputs
        new = theta_maths(summed_dif=self.diffraction_pattern, median_blur_distance=self.median_blur_distance,
                          median_blur_height=self.median_blur_height,
                          stdev_min=self.stdev_min, q=False)


        out_checker = []
        for i in range(0, len(new)):
            out_checker.append(np.array_equal(new[i], self.theta_maths_check[i]))

        self.assertTrue(all(out_checker))

    def test_chi_maths(self):
        # Check 4 outputs
        new = chi_maths(summed_dif=self.diffraction_pattern, median_blur_distance=self.median_blur_distance,
                        median_blur_height=self.median_blur_height, stdev_min=self.stdev_min, q=False)


        out_checker = []
        for i in range(0, len(new)):
            out_checker.append(np.array_equal(new[i], self.chi_maths_check[i]))

        self.assertTrue(all(out_checker))

    def test_centroid_finder(self):
        # Check 2 outputs
        new = centroid_finder(oneDarray_start=self.oneDarray, stdev_min=self.stdev_min)

        out_checker = []
        for i in range(0, len(new)):
            out_checker.append(np.array_equal(new[i], self.centroid_finder_check[i]))

        self.assertTrue(all(out_checker))


    def test_grab_pix(self):
        # Check 1 output
        new = grab_pix(array=test_fs.image_array, row=self.row, column=self.column, int_convert=False)

        out_checker = []
        for i in range(0, len(new)):
            out_checker.append(np.array_equal(new[i], self.grab_pix_check[i]))

        self.assertTrue(all(out_checker))

    def test_sum_pixel(self):
        # Check 1 output
        new = sum_pixel(self=test_fs, images_loc=self.destination)

        out_checker = []
        for i in range(0, len(new)):
            out_checker.append(np.array_equal(new[i], self.sum_pixel_check[i]))

        self.assertTrue(all(out_checker))



    def test_roi_pixel_analysis(self):
        # Check 8 outputs
        new = roi_pixel_analysis(self=test_fs, row=self.row, column=self.column,
                                 median_blur_distance=self.median_blur_distance,
                                median_blur_height=self.median_blur_height, diff_segments=True)


        out_checker = []

        for i in range(0, len(new)):
            if len(new[i]) > 1:
                for j in range(0, len(new[i])):
                    out_checker.append(np.array_equal(new[i][j], self.roi_pixel_analysis_check[i][j]))

            else:
                out_checker.append(np.array_equal(new[i], self.roi_pixel_analysis_check[i]))

        self.assertTrue(all(out_checker))
        
    def test_sum_pixel_v2(self):
        image_array = test_fs.image_array
        row = 1
        column = 1
        pix = grab_pix(array=image_array, row=row, column=column, int_convert=True)
        destination = h5get_image_destination(self=test_fs, pixel=pix)

        with h5py.File(test_fs.file, 'r', swmr=True) as hdf:
            each_scan_diffraction = sum_pixel_v2(images_loc=destination, file=hdf)
        
        self.assertEqual(np.shape(each_scan_diffraction), (2, 516, 516))
        
    def test_pixel_diffraction_grab(self):
        summed_dif = pixel_diffraction_grab(test_fs, test_fs.image_array, row=1, column=1)
        self.assertEqual(np.shape(summed_dif), (516, 516))

if __name__ == '__main__':
    unittest.main()