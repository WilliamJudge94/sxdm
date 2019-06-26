import numpy as np
import h5py
import psutil
from functools import partial
import multiprocessing
from tqdm import tqdm

from background import scan_background_finder, scan_background
from mis import median_blur, get_idx4roi


def pixel_analysis_v3(row, column, median_blur_distance, median_blur_height, stdev_min, image_array, scan_numbers, background_dic, file):
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
    """

    try:
        self.pbar_val = self.pbar_val + 1
        self.pbar.update(self.pbar_val)
    except:
        pass
    if column == 0:
        if ram_check() > 90:
            return False

    pix = grab_pix_v2(array=image_array, row=row, column=column, int_convert=True)
    destination = h5get_image_destination_v2(scan_numbers=scan_numbers, pixel=pix)
    each_scan_diffraction = sum_pixel_v2(file=file, images_loc=destination)

    # Background Correction
    backgrounds = scan_background_finder(destination=destination, background_dic=background_dic)
    each_scan_diffraction_post = np.subtract(each_scan_diffraction, backgrounds)

    summed_dif = np.sum(each_scan_diffraction_post, axis=0)

    ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2 = theta_maths_v2(summed_dif,
                                                                           median_blur_distance,
                                                                           median_blur_height,
                                                                           stdev_min)
    chi, chi_centroid, chi_centroid_finder = chi_maths_v2(summed_dif,
                                                       median_blur_distance,
                                                       median_blur_height, stdev_min)

    full_roi = np.sum(ttheta2)

    # Setting this to zero to solve high RAM usage
    summed_dif = 0

    results = [(row, column), summed_dif, ttheta, chi, ttheta_centroid_finder,
               ttheta_centroid, chi_centroid_finder, chi_centroid, full_roi]

    return results


def h5get_image_destination_v2(scan_numbers, pixel):
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


def sum_pixel_v2(file, images_loc):
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
    for image in images_loc:
        pixel_store.append(h5grab_data_v2(file, image))
    return pixel_store


def grab_pix_v2(array, row, column, int_convert=False):
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


def h5grab_data_v2(file, data_loc):
        """Returns the data stored in the user defined group

        Parameters
        ==========
        file (str):
            the user defined hdf5 file
        data_loc (str):
            the group the user would like to pull data from

        Returns
        =======
        the data stored int the user defined location
        """
        with h5py.File(file, 'r') as hdf:
            data = hdf.get(data_loc)
            data = np.array(data)
        return data


def theta_maths_v2(summed_dif, median_blur_distance, median_blur_height, stdev_min, q=False):
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

    ttheta = np.sum(summed_dif, axis=0)
    ttheta = median_blur(ttheta, median_blur_distance, median_blur_height, with_low=True)
    ttheta2 = np.asarray(ttheta)
    ttheta_centroid_finder, ttheta_centroid = centroid_finder_v2(ttheta2, stdev_min)
    if q == False:
        return ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2
    else:
        q.put([ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2])


def chi_maths_v2(summed_dif, median_blur_distance, median_blur_height, stdev_min, q=False):
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
    chi = np.sum(summed_dif, axis=1)
    chi = median_blur(chi, median_blur_distance, median_blur_height, with_low=True)
    chi2 = np.asarray(chi)
    chi_centroid_finder, chi_centroid = centroid_finder_v2(chi2, stdev_min)
    if q == False:
        return chi, chi_centroid, chi_centroid_finder
    else:
        q.put([chi, chi_centroid, chi_centroid_finder])


def centroid_finder_v2(oneDarray_start, stdev_min=35):
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


def ram_check():
    """Check how much RAM is being used.
    If it's over 90% then the analysis function stop loading information

    Returns
    =======
    the percent of RAM usage
    """
    mems = psutil.virtual_memory()
    return round(mems[2], 1)


def roi_pixel_analysis_v2(row, column, median_blur_distance,
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

    try:
        self.pbar_val = self.pbar_val + 1
        self.pbar.update(self.pbar_val)
    except:
        pass
    if column == 0:
        if ram_check() > 90:
            return False


    pix = grab_pix_v2(array=image_array, row=row, column=column, int_convert=True)
    destination = h5get_image_destination_v2(scan_numbers, pixel=pix)

    each_scan_diffraction = sum_pixel_v2(file, images_loc=destination)

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


def initialize_multi(num_rows, num_columns):
    """ Places the row and column number next to each other in an iterable array.
        Used for starmap multiprocessing pixels.

    Parameters
    ==========
    self: (SXDMFrameset)
    num_rows: (int)
        Total number of rows the user wants to calculate
    num_columns: (int)
        Total number of columns the user wants to calculate

    Returns
    =======
    An iterable array of pixel locations to be passed into the multiprocessing pixel analysis
    """

    master_row = []
    master_column = []
    if isinstance(num_rows, int) and isinstance(num_columns, int):
        start_row = 0
        end_row = num_rows
        start_column = 0
        end_column = num_columns

    elif isinstance(num_rows, int) and isinstance(num_columns, tuple):
        start_row = 0
        end_row = num_rows
        start_column = num_columns[0]
        end_column = num_columns[1]

    elif isinstance(num_rows, tuple) and isinstance(num_columns, int):
        start_row = num_rows[0]
        end_row = num_rows[1]
        start_column = 0
        end_column = num_columns

    elif isinstance(num_rows, tuple) and isinstance(num_columns, tuple):
        start_row = num_rows[0]
        end_row = num_rows[1]
        start_column = num_columns[0]
        end_column = num_columns[1]

    for i in range(start_row, end_row):
        for j in range(start_column, end_column):
            master_row.append(i)
            master_column.append(j)

    return master_row, master_column


def roi_pre_analysis(inputs, meds_d, meds_h, image_array, scan_numbers, background_dic, file, diff_segments):
    row, column = inputs
    results = roi_pixel_analysis_v2(row, column, meds_d, meds_h, image_array, scan_numbers, background_dic, file, diff_segments)
    return results


def roi_analysis_v2(self, rows, columns, med_blur_distance=9,
                           med_blur_height=100, bkg_multiplier=0, diff_segments=True):

    master_rows, master_columns = initialize_multi(num_rows=rows, num_columns=columns)

    inputs = zip(master_rows, master_columns)

    inputs = tqdm(inputs, total=len(master_rows),
              desc="Progress", unit='pixles')


    background_dic = scan_background(self, multiplier=bkg_multiplier)
    if diff_segments==True:
        diff_segments = self.diff_segment_squares


    p_roi_pre_analysis = partial(roi_pre_analysis, meds_d=med_blur_distance, meds_h=med_blur_height, image_array=self.image_array,
                                 background_dic=background_dic, file=self.file, diff_segments=diff_segments, scan_numbers=self.scan_numbers)

    pool = multiprocessing.Pool()

    results = pool.map(p_roi_pre_analysis, inputs)

    pool.close()

    return results


def centroid_pre_analysis(inputs, meds_d, meds_h, st, image_array, scan_numbers, background_dic, file):
    row, column = inputs
    results = pixel_analysis_v3(row, column, meds_d, meds_h, st, image_array, scan_numbers, background_dic, file)
    return results


def centroid_analysis_v2(self, rows, columns, med_blur_distance=9,
                           med_blur_height=100, stdev=35, bkg_multiplier=0):

    master_rows, master_columns = initialize_multi(num_rows=rows, num_columns=columns)

    inputs = zip(master_rows, master_columns)

    inputs = tqdm(inputs, total=len(master_rows),
              desc="Progress", unit='pixles')


    background_dic = scan_background(self, multiplier=bkg_multiplier)


    p_centroid_pre_analysis = partial(centroid_pre_analysis, meds_d=med_blur_distance, meds_h=med_blur_height, image_array=self.image_array,
                                 background_dic=background_dic, file=self.file, st=stdev, scan_numbers=self.scan_numbers)

    pool = multiprocessing.Pool()

    results = pool.map(p_centroid_pre_analysis, inputs)

    pool.close()

    return results


