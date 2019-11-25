import unittest
import os
import sys

sys.path.append(os.path.dirname(__file__))
sys.path.append('../..')

from sxdm import *


test_path = os.path.dirname(__file__)
main_path = '{}/'.format(test_path)
test_file_path = main_path+'test_data.h5'
scan_numbers = [178, 178]
dataset_name = 'test_178'

test_fs = SXDMFrameset(test_file_path, dataset_name, scan_numbers=scan_numbers)
test_fs.ims_array(center_around=-1)
create_imagearray(test_fs, center_around=-1)


def do_something(each_scan_diffraction_post_bk_sub, inputs):
    summed_diff = np.sum(each_scan_diffraction_post_bk_sub, axis=0)

    adding, subtracting, dividing, multiplying = inputs

    first = np.add(summed_diff, adding)
    second = np.subtract(first, subtracting)
    third = np.divide(second, dividing)
    fourth = np.multiply(third, multiplying)

    return fourth, third, second, first


class MultiTestCase(unittest.TestCase):
    
    def test_iterations(self):
        test_fs.median_blur_distance = 1
        test_fs.median_blur_height = 1
        test_fs.stdev_min = 1

        output1 = np.shape(iterations(test_fs, (4, 10), (5, 10)))

        output2 = np.shape(iterations(test_fs, 10, 10))

        self.assertEqual(output1, (30, 7))
        self.assertEqual(output2, (100, 7))
    
    def test_initalize_vectorize(self):
        output1 = np.shape(initialize_vectorize((5, 10), 10))
        output2 = np.shape(initialize_vectorize((5, 10), (5, 10)))
        output3 = np.shape(initialize_vectorize(10, 10))

        self.assertEqual(output1, (2, 50))
        self.assertEqual(output2, (2, 25))
        self.assertEqual(output3, (2, 100))

    
    def test_centroid_map_analysis(self):
        
        # Centroid Single Pixel Multi

        with h5py.File(test_fs.file, 'r', swmr=True) as hdf:
            results = centroid_pixel_analysis_multi(row=1, column=1, median_blur_distance=5, median_blur_height=10,
                                           image_array=test_fs.image_array, scan_numbers=test_fs.scan_numbers,
                                           background_dic=test_fs.background_dic, file=hdf, stdev_min=10)
            
        self.assertEqual(np.shape(results), (9, ))
            
        output = centroid_map_analysis(self=test_fs, rows=1, columns=2,
                                       med_blur_distance=5, center_around=-1)
        print(np.shape(output))
        print(np.shape(output[0]))
        print(output[0])
        shape_check = np.shape(output)
        rc_check = output[0][0]
        sum_dif_check = output[0][1]
        check5 = output[0][5]
        check7 = output[0][7]
        check8 = output[0][8]
        
        self.assertEqual(shape_check, (2, 9))
        self.assertEqual(rc_check, (0, 0))
        self.assertEqual(sum_dif_check, 0)
        self.assertEqual(check5, 397.09460443778215)
        self.assertEqual(check7, 279.2084836699383)
        self.assertEqual(check8, 53169.333333313465)
        
        returns = pooled_return(output, 'row_column')
        self.assertEqual(returns[0], (0, 0))

        output = centroid_analysis_multi(test_fs, 1, 2, med_blur_distance=5,
                                         med_blur_height=10, bkg_multiplier=1)

        shape_check = np.shape(output)
        rc_check = output[0][0]
        sum_dif_check = output[0][1]
        check5 = output[0][5]
        check7 = output[0][7]
        check8 = output[0][8]

        self.assertEqual(shape_check, (2, 9))
        self.assertEqual(rc_check, (0, 0))
        self.assertEqual(sum_dif_check, 0)
        self.assertEqual(check5, 397.09460443778215)
        self.assertEqual(check7, 279.2084836699383)
        self.assertEqual(check8, 53169.333333313465)
        
        

        
    
    def test_roi_analysis(self):
        
        # ROI Single Pixel Multi

        with h5py.File(test_fs.file, 'r', swmr=True) as hdf:
            results = roi_pixel_analysis_multi(row=1, column=1, median_blur_distance=5, median_blur_height=10,
                                           image_array=test_fs.image_array, scan_numbers=test_fs.scan_numbers,
                                           background_dic=test_fs.background_dic, file=hdf, diff_segments=False)
            
        self.assertEqual(np.shape(results), (8, ))
        self.assertEqual(results[0], (1, 1))
        
        # Analysis Single Thread
        output = roi_analysis(test_fs, 1, 2, med_blur_distance=5,
                              center_around=-1, diff_segmentation=False)
        
        shape_check = np.shape(output)
        rc_check = output[0][0]
        check1 = output[0][1]
        check4 = np.array_equal(output[0][4], [26584.666666656733, 26584.666666656733])

        self.assertEqual(shape_check, (2, ))
        self.assertEqual(rc_check, (0, 0))
        self.assertEqual(check1, [0, 1])
        self.assertTrue(check4)

        # Analysis Multi Thread
        output = roi_analysis_multi(test_fs, 1, 2, med_blur_distance=5, med_blur_height=10,
                                    bkg_multiplier=1, diff_segments=False)

        shape_check = np.shape(output)
        rc_check = output[0][0]
        check1 = output[0][1]
        check4 = np.array_equal(output[0][4], [26584.666666656733, 26584.666666656733])

        self.assertEqual(shape_check, (2, 8))
        self.assertEqual(rc_check, (0, 0))
        self.assertEqual(check1, [0, 1])
        self.assertTrue(check4)
    
    def test_general_analysis_multi(self):

        rows = 1
        columns = 2
        inputs = [1, 3, 5, 7]
        create_imagearray(test_fs, center_around=-1)
        
        with h5py.File(test_fs.file, 'r', swmr=True) as hdf:
            # General Pixel Analysis Testing
            results = general_pixel_analysis_multi(row=0, column=0,
                                                   image_array=test_fs.image_array,
                                                   scan_numbers=test_fs.scan_numbers,
                                                   background_dic=test_fs.background_dic,
                                                   file=hdf,
                                                   analysis_function=do_something,
                                                   analysis_input=inputs)

        # General Analysis Multi testing
        output = general_analysis_multi(test_fs, rows, columns, do_something, inputs)

        user_acceptable_values = ['fourth', 'third', 'second', 'first']

        # General Pooled Return Testing
        all_values = general_pooled_return(output, 'row_column', user_acceptable_values)

        self.assertEqual(all_values[0], (0, 0))
        self.assertEqual(np.shape(output), (2, 5))
        self.assertEqual(np.shape(results), (5, ))
    
    def test_sum_pixel_multi(self):
        pass
    
    def test_pooled_return(self):
        pass
    


if __name__ == '__main__':
    unittest.main()
