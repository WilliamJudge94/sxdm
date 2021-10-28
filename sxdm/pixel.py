import numpy as np
from multiprocessing.pool import ThreadPool
from multiprocessing import Process, Queue
import logging
import h5py
from tqdm import tqdm

from mis import ram_check, get_idx4roi#, median_blur
from h5 import h5get_image_destination, h5grab_data, open_h5, close_h5
from background import scan_background, scan_background_finder
from datetime import datetime

import config



def theta_maths(summed_dif, median_blur_distance, median_blur_height, stdev_min, q=False):
    """Determine the centroid of the theta axis
    Parameters
    ==========
    summed_dif (nd.array image)
        a 2D summed diffraction image
    median_blur_distance (int)
        the amount of values to take the median of
    median_blur_height (int)
        the value above the median to replace with the median value
    stdev_min (int)
        the standard deviation above the noise to consider the signal valid
    q (bool)
        used for an old multi processing function - unused now - might be put in at a later date
    Returns
    =======
    the edited (median blured) sum down the y axis
    the centroid of the data
    the cropped data to find the centroid
    the edited (median blured) sum down the y axis as a numpy array
    """
    median_blur = config.median_blur
    
    ttheta = np.sum(summed_dif, axis=0)
    ttheta = median_blur(ttheta, median_blur_distance, median_blur_height, with_low=True)
    ttheta2 = np.asarray(ttheta)
    ttheta_centroid_finder, ttheta_centroid = centroid_finder(ttheta2, stdev_min)
    if q == False:
        return ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2
    else:
        q.put([ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2])


def chi_maths(summed_dif, median_blur_distance, median_blur_height, stdev_min, q=False):
    """Determine the centroid of the chi axis
    Parameters
    ==========
    summed_dif (nd.array image)
        a 2D summed diffraction image
    median_blur_distance (int)
        the amount of values to take the median of
    median_blur_height (int)
        the value above the median to replace with the median value
    stdev_min (int)
        the standard deviation above the noise to consider the signal valid
    q (bool)
        used for an old multi processing function - unused now - might be put in at a later date
    Returns
    =======
    the edited (median blured) sum down the x axis
    the centroid of the data
    the cropped data to find the centroid
    the edited (median blured) sum down the x axis as a numpy array
    """
    median_blur = config.median_blur
    
    chi = np.sum(summed_dif, axis=1)
    chi = median_blur(chi, median_blur_distance, median_blur_height, with_low=True)
    chi2 = np.asarray(chi)
    chi_centroid_finder, chi_centroid = centroid_finder(chi2, stdev_min)
    if q == False:
        return chi, chi_centroid, chi_centroid_finder
    else:
        q.put([chi, chi_centroid, chi_centroid_finder])


def centroid_finder(oneDarray_start, stdev_min=35):
    """Determine the centroid function
    Parameters
    ==========
    oneDarray_start (numpy array)
        a one dimensions numpy array
    stdev_min (int)
        the standard deviation minimum the user would like to section the data off with
    Returns
    =======
    the corrected one dimensional array and the centroid of the array
    """
    oneDarray = oneDarray_start.copy()

    xvals = np.arange(0, len(oneDarray))
    if np.std(oneDarray) < stdev_min:
        oneDarray[oneDarray <= np.max(oneDarray)] = 0

    else:
        oneDarray[oneDarray <= np.mean(oneDarray)] = 0

    if np.sum(oneDarray) == 0:
        centroid = np.nan
    else:
        centroid = np.sum(xvals * oneDarray) / np.sum(oneDarray)

    return oneDarray, centroid


def grab_pix(array, row, column, int_convert=False):
    """Return a pixel at a given row and column value
    Parameters
    ==========
    array (nd.array)
        a 3 dimensional numpy array
    row (int)
        the row the user would like to grab
    column (int)
        the column the user would like to grab
    int_convert (bool)
        if the user would like to change np.nans to integers set this to True
    Returns
    =======
    All data associated with the set row and column for the 3 dimensional array
    """
    output = array[:, row, column]
    if int_convert == True:
        int_output = []
        for value in output:
            if np.isnan(value) == False:
                int_output.append(int(np.round(value, 0)))
            else:
                int_output.append(value)
        return int_output
    else:
        return np.asarray(output)


def sum_pixel(self, images_loc):
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
    pixel_store = []

    with h5py.File(self.file, 'r', swmr=True) as hdf:
        for image in images_loc:

            data = hdf.get(image)
            data = np.array(data)
            pixel_store.append(data)

    #for image in images_loc:
    #    pixel_store.append(h5grab_data(self.file, image))

    return pixel_store


def sum_pixel_v2(images_loc, file):
    """Sum a pixel
    Parameters
    ==========
    image_loc (list of str)
        the full image location in the hdf5 file
    file: (hdf file)
        the opened hdf file
    Returns
    =======
    all images set in the image_loc variable
    """
    pixel_store = []

    for image in images_loc:

        data = file.get(image)
        data = np.asarray(data)
        pixel_store.append(data)


    return pixel_store


def centroid_pixel_analysis(self, row, column, median_blur_distance, median_blur_height, stdev_min):
    """The analysis done on a single pixel
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
    stdev_min: (int)
        standard deviation above the mean of signal to ignore
    bkg_multiplier: (int)
        multiplier for the background signal to be subtracted
    Returns
    =======
    the analysis results as an nd.array
    
    # For a given row and column
    [
    (row_index, column_index),
    summed diffraction pattern (set to zero to save RAM. User can change in source code in /pixel.py),
    two theta centroid value (float)
    chi centroid value (float)
    two theta cropped signal (nd.array)
    full two theta signal (nd.array)
    chi cropped signal (nd.array)
    full chi signal (nd.array)
    summed region of interest value (float)
    
    ]
    """

    image_array = self.image_array
    try:
        self.pbar_val = self.pbar_val + 1
        self.pbar.update(self.pbar_val)
    except:
        pass
    if column == 0:
        if ram_check() > 90:
            return False

    pix = grab_pix(array=image_array, row=row, column=column, int_convert=True)
    destination = h5get_image_destination(self=self, pixel=pix)
    each_scan_diffraction = sum_pixel(self=self, images_loc=destination)

    # Background Correction
    backgrounds = scan_background_finder(destination=destination, background_dic=self.background_dic)
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

def segment_diffraction_roi(diffraction):
    """Creates a roi value and the raw data analysis for the ROI maps

    Parameters
    ==========
    diffraction (image)
        the summed diffraction image

    Returns
    =======
    ttheta, ttheta_copy, np.sum(ttheta_copy), scan_roi_val
    """
    median_blur = config.median_blur
    
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


    return ttheta, ttheta_copy, np.sum(ttheta_copy), scan_roi_val


def roi_pixel_analysis(self, row, column, median_blur_distance,
                       median_blur_height, diff_segments=False):
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
    median_blur = config.median_blur
    
    image_array = self.image_array
    try:
        self.pbar_val = self.pbar_val + 1
        self.pbar.update(self.pbar_val)
    except:
        pass
    if column == 0:
        if ram_check() > 90:
            return False


    pix = grab_pix(array=image_array, row=row, column=column, int_convert=True)
    destination = h5get_image_destination(self=self, pixel=pix)

    each_scan_diffraction = sum_pixel(self=self, images_loc=destination)

    # Background Correction
    backgrounds = scan_background_finder(destination=destination, background_dic=self.background_dic)

    # All diffraction images for the current pixel
    each_scan_diffraction_post = np.subtract(each_scan_diffraction, backgrounds)

    # Obtain all master array scan_number index values that the diffraction scans correspond to
    idxs = get_idx4roi(pix=pix, destination=destination, scan_numbers=self.scan_numbers)

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

    # start roi bounding arrays
    summed_data = []
    corr_summed_data = []
    summed_data_roi_vals = []

    # create the summed diffraction pattern for the selected pixel location
    summed_dif = np.sum(each_scan_diffraction_post, axis=0)

    # only do this is the user wants it done
    t2 = datetime.now()
    if diff_segments != False:

        # for each bounding box
        for segment in self.diff_segment_squares:
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

def pixel_diffraction_grab(self, image_array, row, column):
    """Returns the diffraction image for a specific scan location (row, column)

    Parameters
    ==========

    self : (SXDMFrameset object)
        the sxdmframset object

    image_array : (nd.array)
        the array that holds all the diffraction image locations self.im_array()

    row : (int)
        the row the User would like to return data for

    column : (int)
        the column the User would like to return data for

    Returns
    ========
    Summed diffraction image for a single pixel
    """
    
    pix = grab_pix(array=image_array, row=row, column=column, int_convert=True)
    destination = h5get_image_destination(self=self, pixel=pix)
    each_scan_diffraction = sum_pixel(self=self, images_loc=destination)

    # Background Correction
    backgrounds = scan_background_finder(destination=destination, background_dic=self.background_dic)
    each_scan_diffraction_post = np.subtract(each_scan_diffraction, backgrounds)

    summed_dif = np.sum(each_scan_diffraction_post, axis=0)
    
    return summed_dif