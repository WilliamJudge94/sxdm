import numpy as np
import h5py
import psutil
from functools import partial
import multiprocessing
from tqdm import tqdm

from background import scan_background_finder, scan_background
from mis import median_blur, get_idx4roi, ram_check
from pixel import theta_maths, chi_maths, centroid_finder, grab_pix
from multi import initialize_vectorize


def centroid_pixel_analysis_multi(row, column, median_blur_distance, median_blur_height,
                                  stdev_min, image_array, scan_numbers, background_dic, file):
    """The analysis done on a single pixel
    Parameters
    ==========
    rows: (int)
        the total number of rows you want to iterate through
    columns: (int)
        the total number of columns you want to iterate through
    med_blur_distance: (int)
        the amount of values to scan for median blur
    med_blur_height:  (int)
        the height cut off for the median blur
    stdev_min: (int)
        standard deviation above the mean of signal to ignore
    bkg_multiplier: (int)
        multiplier for the background signal to be subtracted
    Returns
    =======
    the analysis results as an nd.array
    """
    if column == 0 and row % 2 == 0:
        if ram_check() > 90:
            return False

    pix = grab_pix(array=image_array, row=row, column=column, int_convert=True)
    destination = h5get_image_destination_multi(scan_numbers=scan_numbers, pixel=pix)
    each_scan_diffraction = sum_pixel_multi(file=file, images_loc=destination)

    # Background Correction
    backgrounds = scan_background_finder(destination=destination, background_dic=background_dic)

    each_scan_diffraction_post = np.subtract(each_scan_diffraction, backgrounds)
    summed_dif = np.sum(each_scan_diffraction_post, axis=0)

    ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2 = theta_maths(summed_dif,
                                                                           median_blur_distance,
                                                                           median_blur_height,
                                                                           stdev_min)
    chi, chi_centroid, chi_centroid_finder = chi_maths(summed_dif,
                                                       median_blur_distance,
                                                       median_blur_height, stdev_min)

    full_roi = np.sum(ttheta2)

    # Setting this to zero to solve high RAM usage
    summed_dif = 0

    results = [(row, column), summed_dif, ttheta, chi, ttheta_centroid_finder,
               ttheta_centroid, chi_centroid_finder, chi_centroid, full_roi]

    return results


def h5get_image_destination_multi(scan_numbers, pixel):
    """Determine where all the .tif images are for all the scan numbers disregarding the nan values

    Parameters
    ==========
    self (SXDMFramset)
        the sxdmframset

    pixel (str array)
        the image number from each scan that corresponds to a certain pixel

    Returns
    =======
    All of the diffraction FULL image locations for each scan in a 3D array - excluding the np.nan's
    """
    image_loc = 'images/'
    pixels_minus_nan = []
    for i, scan in enumerate(scan_numbers):
        if np.isnan(pixel[i]) == False:
            pixels_minus_nan.append(image_loc + scan + '/' + str(pixel[i]).zfill(6))

    return pixels_minus_nan


def sum_pixel_multi(file, images_loc):
    """Sum a pixel
    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframset
    image_loc (list of str)
        the full image location in the hdf5 file
    Returns
    =======
    all images set in the image_loc variable
    """
    with h5py.File(file, 'r') as hdf:
        pixel_store = [hdf.get(image).value for image in images_loc]
    return pixel_store


def roi_pixel_analysis_multi(row, column, median_blur_distance,
                       median_blur_height, image_array, scan_numbers, background_dic, file, diff_segments=False):
    """The analysis done on a single pixel - this will get the new roi for each theta
    and be able to segment out diffraction areas and create the roi for them
    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframset
    rows: (int)
        the total number of rows you want to iterate through
    columns: (int)
        the total number of columns you want to iterate through
    med_blur_distance: (int)
        the amount of values to scan for median blur
    med_blur_height:  (int)
        the height cut off for the median blur
    diff_segments: (array)
        array used for segmenting the diffraction patterns
    Returns
    =======
    the analysis results as an nd.array
    [(row, column), idxs,
               raw_scan_data, corr_scan_data, scan_data_roi_vals,
               summed_data, corr_summed_data, summed_data_roi_vals]
    """
    if column == 0:
        if ram_check() > 90:
            return False


    pix = grab_pix(array=image_array, row=row, column=column, int_convert=True)
    destination = h5get_image_destination_multi(scan_numbers, pixel=pix)

    each_scan_diffraction = sum_pixel_multi(file, images_loc=destination)

    # Background Correction
    backgrounds = scan_background_finder(destination=destination, background_dic=background_dic)

    # All diffraction images for the current pixel
    each_scan_diffraction_post = np.subtract(each_scan_diffraction, backgrounds)

    # Obtain all master array scan_number index values that the diffraction scans correspond to
    idxs = get_idx4roi(pix=pix, destination=destination, scan_numbers=scan_numbers)

    raw_scan_data = []
    corr_scan_data = []
    scan_data_roi_vals = []

    # SCAN DATA
    # For each of the scan_diffraction_post
    for diffraction in each_scan_diffraction_post:

        # sum down an axis
        ttheta = np.sum(diffraction, axis=0)
        ttheta_copy = ttheta.copy()

        # store this to an array
        raw_scan_data.append(ttheta)

        # median blur it and store
        ttheta_copy = median_blur(input_array=ttheta_copy,
                    median_blur_distance=median_blur_distance,
                    cut_off_value_above_mean=median_blur_height,
                                  with_low=True)

        corr_scan_data.append(ttheta_copy)

        # sum to single value and store
        scan_roi_val = np.sum(ttheta_copy)
        scan_data_roi_vals.append(scan_roi_val)
    #print('first',datetime.now() - t1)

    # start roi bounding arrays
    summed_data = []
    corr_summed_data = []
    summed_data_roi_vals = []

    # create the summed diffraction pattern for the selected pixel location
    summed_dif = np.sum(each_scan_diffraction_post, axis=0)

    # only do this is the user wants it done

    if diff_segments != False:

        # for each bounding box
        for segment in diff_segments:
            # segment the summed diffraction pattern
            segmented_diffraction = summed_dif[int(segment[2]):int(segment[3]),
                                    int(segment[0]):int(segment[1])]

            # sum it down an axis and store
            ttheta = np.sum(segmented_diffraction, axis=0)
            ttheta_copy = ttheta.copy()
            summed_data.append(ttheta)

            # median blur it and store
            ttheta_copy = median_blur(input_array=ttheta_copy,
                        median_blur_distance=median_blur_distance,
                        cut_off_value_above_mean=median_blur_height)
            corr_summed_data.append(ttheta_copy)

            # sum to single value and store
            summed_data_roi_val = np.sum(ttheta_copy)
            summed_data_roi_vals.append(summed_data_roi_val)
        #print('second', datetime.now() - t2)

    results = [(row, column), idxs,
               raw_scan_data, corr_scan_data, scan_data_roi_vals,
               summed_data, corr_summed_data, summed_data_roi_vals]

    return results


def roi_pre_analysis(inputs, meds_d, meds_h, image_array, scan_numbers, background_dic, file, diff_segments):
    row, column = inputs
    results = roi_pixel_analysis_multi(row, column, meds_d, meds_h,
                                       image_array, scan_numbers, background_dic, file, diff_segments)
    return results


def roi_analysis_multi(self, rows, columns, med_blur_distance=9,
                           med_blur_height=100, bkg_multiplier=0, diff_segments=True):

    master_rows, master_columns = initialize_vectorize(num_rows=rows, num_columns=columns)

    inputs = zip(master_rows, master_columns)

    inputs = tqdm(inputs, total=len(master_rows),
              desc="Progress", unit='pixles')


    background_dic = scan_background(self, multiplier=bkg_multiplier)
    if diff_segments==True:
        diff_segments = self.diff_segment_squares


    p_roi_pre_analysis = partial(roi_pre_analysis, meds_d=med_blur_distance,
                                 meds_h=med_blur_height, image_array=self.image_array,
                                 background_dic=background_dic, file=self.file,
                                 diff_segments=diff_segments, scan_numbers=self.scan_numbers)


    with multiprocessing.Pool() as pool:
        results = pool.map(p_roi_pre_analysis, inputs)


    return results


def centroid_pre_analysis(inputs, meds_d, meds_h, st, image_array, scan_numbers, background_dic, file):
    row, column = inputs
    results = centroid_pixel_analysis_multi(row, column, meds_d, meds_h, st,
                                            image_array, scan_numbers, background_dic, file)
    return results


def centroid_analysis_multi(self, rows, columns, med_blur_distance=9,
                           med_blur_height=100, stdev=35, bkg_multiplier=0):

    master_rows, master_columns = initialize_vectorize(num_rows=rows, num_columns=columns)

    inputs = zip(master_rows, master_columns)

    inputs = tqdm(inputs, total=len(master_rows),
              desc="Progress", unit='pixles')


    background_dic = scan_background(self, multiplier=bkg_multiplier)


    p_centroid_pre_analysis = partial(centroid_pre_analysis, meds_d=med_blur_distance,
                                      meds_h=med_blur_height, image_array=self.image_array,
                                 background_dic=background_dic, file=self.file,
                                      st=stdev, scan_numbers=self.scan_numbers)

    with multiprocessing.Pool() as pool:
        # add chunksize
        results = pool.map(p_centroid_pre_analysis, inputs)

    return results


