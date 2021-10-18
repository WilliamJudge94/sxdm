from multiprocessing import Pool, cpu_count, Queue, Process
import warnings
import numpy as np
from tqdm import tqdm
from datetime import datetime
import math

from pixel import *
from mis import centering_det
from miniutils import parallel_progbar
from tqdm import tqdm

from progressbar import *


def iterations(self, num_rows, num_columns):
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

    its = []
    if isinstance(num_rows, int) and isinstance(num_columns, int):
        for i in range(0, num_rows):
            for j in range(0, num_columns):
                its.append((self, i, j, self.image_array, self.median_blur_distance,
                            self.median_blur_height, self.stdev_min))
    elif isinstance(num_rows, tuple) and isinstance(num_columns, tuple):
        first_row = num_rows[0]
        last_row = num_rows[1]
        first_column = num_columns[0]
        last_column = num_columns[1]
        for i in range(first_row, last_row):
            for j in range(first_column, last_column):
                its.append((self, i, j, self.image_array, self.median_blur_distance,
                            self.median_blur_height, self.stdev_min))
    return its


def initialize_vectorize(num_rows, num_columns):
    """ Places the row and column number next to each other in an iterable array.
        Used for starmap multiprocessing pixels.

    Parameters
    ==========
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


def pooled_return(results, user_val):
    """Makes it easy to return values from the pooled results from the multi.analysis function

    Parameters
    ==========
    results (n dimensional array)
        the output from the analysis function

    user_val (str)
        a string that defines what the user wants to be returned

    Returns
    =======
    An n dimensional array consisting of the user selected data output from the multi.analysis function
    """

    acceptable_values = ['row_column', 'summed_dif',
                         'ttheta', 'chi', 'ttheta_corr',
                         'ttheta_centroid', 'chi_corr',
                         'chi_centroid', 'full_roi']
    if user_val in acceptable_values:
        acceptable_values = np.asarray(acceptable_values)
        finder = np.where(acceptable_values == user_val)[0][0]
        results = np.asarray(results, dtype=object)

        return np.asarray(results[:, finder])

    else:
        warnings.warn('Acceptable Values Are: ' + ', '.join(acceptable_values))


def centroid_map_analysis(self, rows, columns, med_blur_distance=4,
                  med_blur_height=10,
                  stdev_min=35, multiplier=1,
                  center_around=False):

    """Calculates spot diffraction and data needed to make 2theta/chi/roi maps

    Parameters
    ==========
    self: (SXDMFramset)
        the sxdmframset
    rows: (int)
        the total number of rows you want to iterate through
    columns: (int)
        the total number of columns you want to iterate through
    med_blur_distance: (int)
        the amount of values to scan for median blur
    med_blur_height:
        (int) the height cut off for the median blur
    stdev_min: (int)
        standard deviation above the mean of signal to ignore
    multiplier: (int)
        multiplier for the background signal to be subtracted
    center_around: (int)
        the index of the scan you would like to center around

    Returns
    =======
    A numpy matrix of every pixel asked. Each pixel contains

    row_column,(row, column), summed_dif, ttheta, chi,
    ttheta_centroid_finder, ttheta_centroid,
    chi_centroid_finder, chi_centroid, full_roi
    """
    self.median_blur_distance = med_blur_distance
    self.median_blur_height = med_blur_height
    self.stdev_min = stdev_min
    self.centroid_bkg_multiplier = multiplier

    # Create a background for the scans
    background_dic_basic = scan_background(self, multiplier=multiplier)

    # Grab all your images
    create_imagearray(self, center_around=center_around)

    # Initialize verctorization
    row, column = initialize_vectorize(rows, columns)
    vectorize_pixel_analysis = np.vectorize(centroid_pixel_analysis,
                                            excluded=['self', 'median_blur_distance',
                                                      'median_blur_height', 'stdev_min'])
    # Create progress bar
    self.pbar_val = 0
    widgets = ['Progress: ', Percentage(), ' ', Bar(marker='-', left='[', right=']'),
               ' ', Timer(), '  ', ETA(), ' ', FileTransferSpeed()]  # see docs for other options
    self.pbar = ProgressBar(widgets=widgets, maxval=len(row)+1)
    self.pbar.start()

    # Start the analysis
    results = vectorize_pixel_analysis(self, row, column,
                                       self.median_blur_distance,
                                       self.median_blur_height,
                                       self.stdev_min)
    readable_results = []

    # Make the results readable
    for re in results:
        readable_results.append(np.asarray(re))
    readable_results = np.asarray(readable_results)

    return readable_results


def roi_analysis(self, rows, columns, med_blur_distance=4,
                  med_blur_height=10,
                  stdev_min=35, multiplier=1,
                  center_around=False,
                 diff_segmentation=True):

    """Calculates region of interest for each scan as well as the region of interest maps for
    user defined sub region of interests

    Parameters
    ==========
    self: (SXDMFramset)
        the sxdmframset
    rows: (int)
        the total number of rows you want to iterate through
    columns: (int)
        the total number of columns you want to iterate through
    med_blur_distance: (int)
        the amount of values to scan for median blur
    med_blur_height:
        (int) the height cut off for the median blur
    stdev_min: (int)
        standard deviation above the mean of signal to ignore
    multiplier: (int)
        multiplier for the background signal to be subtracted
    center_around: (int)
        the index of the scan you would like to center around
    diff_segmentation: (bool)
        if set to True this will initiate the user sub region of interest analysis

    Returns
    =======
    A numpy matrix of every pixel asked. Each pixel contains

    [(row, column), idxs,
               raw_scan_data, corr_scan_data, scan_data_roi_vals,
               summed_data, corr_summed_data, summed_data_roi_vals]
    """
    self.median_blur_distance = med_blur_distance
    self.median_blur_height = med_blur_height
    self.stdev_min = stdev_min

    # Create a background for the scans
    background_dic_basic = scan_background(self, multiplier=multiplier)

    # Grab all your images
    create_imagearray(self, center_around=center_around)

    # Initialize verctorization
    row, column = initialize_vectorize(rows, columns)

    vectorize_roi_pixel_analysis = np.vectorize(roi_pixel_analysis,
                                            excluded=['self', 'median_blur_distance',
                                                      'median_blur_height', 'diff_segmentation'])
    # Create progress bar
    self.pbar_val = 0
    widgets = ['Progress: ', Percentage(), ' ', Bar(marker='-', left='[', right=']'),
               ' ', Timer(), '  ', ETA(), ' ', FileTransferSpeed()]  # see docs for other options
    self.pbar = ProgressBar(widgets=widgets, maxval=len(row)+1)
    self.pbar.start()

    results = vectorize_roi_pixel_analysis(self, row, column,
                                       self.median_blur_distance,
                                       self.median_blur_height,
                                       diff_segmentation)

    return results


def create_imagearray(self, center_around=False):
    """Creates the self.image_array variable needed for pixel_analysis

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframset
    center_around (bool)
        setting this to True allows the user to default to the first image index to center around

    Returns
    =======
    Nothing - sets the self.image_array value
    """
    try:
        image_array = centering_det(self, group='filenumber', center_around=center_around)
        self.image_array = np.asarray(image_array)
    except Exception as ex:
        print('Possibly No Alignment Data', 'multi.py/create_imagearray', ex)
