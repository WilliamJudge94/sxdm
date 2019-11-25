import numpy as np
import h5py
import psutil
from functools import partial
import multiprocessing
from tqdm import tqdm
import time
import warnings


from background import scan_background_finder, scan_background
from mis import get_idx4roi, ram_check#, median_blur
from pixel import theta_maths, chi_maths, centroid_finder, grab_pix
from multi import initialize_vectorize
from multi_update import h5get_image_destination_multi, sum_pixel_multi
from h5 import open_h5, close_h5

import config


def general_pixel_analysis_multi(row, column, image_array, scan_numbers, background_dic, file, analysis_function, analysis_input):
    """The analysis done on a single pixel

    Parameters
    ==========
    row: (int)
        the row the User wants to do analysis on
    column: (int)
        the column the User wants to do analysis on
    image_array: (nd.array)
        the image location array - can be created with create_imagearray(self)
    scan_numbers: (nd.array)
        the list of scan numbers used
    background_dic: (dic)
        the background scan dictionary entry - can be made with scan_backgrounnd(self)
    file: (str)
        the hdf5 file location
    analysis_function: (func)
        a function to be passed into the analysis. the program will find the summed diffraction pattern for each pixel,
        for each scan number of the dataset, background subtract, and pass the summed diffraction into the first
        analysis_function argument.
    analysis_input: (user defined)
        an static input array, value, etc passed into the second argument in the analysis_function.

    Returns
    =======
    the analysis results as an nd.array

    """
    if column == 0 and row % 2 == 0:
        if ram_check() > 90:
            return False

    # This grabs the pixel diffraction information
    pix = grab_pix(array=image_array, row=row, column=column, int_convert=True)

    # This grabs the locations of all of those images it just grabbed
    destination = h5get_image_destination_multi(scan_numbers=scan_numbers, pixel=pix)

    # This will sum together all of those diffraction images
    each_scan_diffraction = sum_pixel_multi(file=file, images_loc=destination)


    # This finds the background
    backgrounds = scan_background_finder(destination=destination, background_dic=background_dic)

    # This subtracts the background
    each_scan_diffraction_post = np.subtract(each_scan_diffraction, backgrounds)

    # This sums together all the background corrected images for that single pixel
    #summed_dif = np.sum(each_scan_diffraction_post, axis=0)


    analysis_output = analysis_function(each_scan_diffraction_post, analysis_input)

    results = [(row, column)]

    for array in analysis_output:
        results.append(array)

    return results

def general_pre_multi(inputs, image_array, scan_numbers, background_dic, file, analysis_function, analysis_input):
    """Allows Python to run the roi analysis in a pool.map function

    Parameters
    ==========
    inputs: (nd.array)
        the iterable inputs of rows and columns
    image_array: (nd.array)
        the total locations of all the images - created by create_imagearray(self)
    scan_numbers: (nd.array)
        the list of all the scan numbers
    background_dic: (dic)
        the dictionary of all the background images - created by scan_background(self)
    file: (str)
        the full hdf5 file location
    analysis_function: (func)
        a function to be passed into the analysis. the program will find the summed diffraction pattern for each pixel,
        for each scan number of the dataset, background subtract, and pass the summed diffraction into the first
        analysis_function argument.
    analysis_input: (user defined)
        an static input array, value, etc passed into the second argument in the analysis_function.

    Returns
    =======
    the results from the general_pixel_analysis_multi() function

    """

    with h5py.File(file, 'r', swmr=True) as hdf:
        row, column = inputs
        results = general_pixel_analysis_multi(row, column, image_array, scan_numbers,
                                               background_dic, hdf,
                                               analysis_function, analysis_input)
    return results


def general_analysis_multi(self, rows, columns, analysis_function, analysis_input, bkg_multiplier=0):
    """Runs the centroid analysis in a pool.map function

    Parameters
    ==========
    self: (SXDMFrameset)
        the sxdmframeset object
    rows: (int or tup)
        the total amount of rows the User wants to analyze or a tuple of the rows
    columns: (int or tup)
        the total amount of columns the User wants to analyze or a tuple of the columns
    med_blur_distance: (int)
        the median blur distance - must be odd
    med_blur_height: (int)
        the median blur height
    stdev: (int)
        the standard deviation used to segment data
    bkg_multiplier: (int)
        the multiplier to the background images
    analysis_function: (func)
        a function to be passed into the analysis. the program will find the summed diffraction pattern for each pixel,
        for each scan number of the dataset, background subtract, and pass the summed diffraction into the first
        analysis_function argument.
    analysis_input: (user defined)
        an static input array, value, etc passed into the second argument in the analysis_function.

    Returns
    =======
    a pooled results from the centroid_pixel_analysis_multi() function

    """

    # Creating the background images
    background_dic = scan_background(self, multiplier=bkg_multiplier)
    time.sleep(2)

    # Creating the iterable to pool.map
    master_rows, master_columns = initialize_vectorize(num_rows=rows, num_columns=columns)

    inputs = zip(master_rows, master_columns)

    inputs = tqdm(inputs, total=len(master_rows),
              desc="Progress", unit='pixles')


    # Creating a partial function
    p_general_pre_analysis = partial(general_pre_multi, image_array=self.image_array,
                                      background_dic=background_dic,
                                      file=self.file,
                                      scan_numbers=self.scan_numbers,
                                      analysis_function=analysis_function,
                                      analysis_input=analysis_input)

    if isinstance(columns, tuple):
        chunky = columns[1] - columns[0]
    else:
        chunky = columns
    # Start multiprocessing
    with multiprocessing.Pool() as pool:
        # add chunksize
        results = pool.map(p_general_pre_analysis, inputs, chunksize=chunky)

    if False in results:
        warnings.warn('RAM Usage Too High. ROI Analysis Stopped')

    return results

def general_pooled_return(results, user_val, user_acceptable_values):
    """Makes it easy to return values from the pooled results from the multi.analysis function

    Parameters
    ==========
    results (n dimensional array)
        the output from the analysis function

    user_val (str)
        a string that defines what the user wants to be returned. Type 'help' for all acceptable values

    user_acceptable_values (list)
        an array of all the analysis_function outputs in the order the user has set them as.

    Returns
    =======
    An n dimensional array consisting of the user selected data output from the multi.analysis function

    """

    acceptable_values = user_acceptable_values
    acceptable_values.insert(0, 'row_column')

    if user_val in acceptable_values:
        acceptable_values = np.asarray(acceptable_values)
        finder = np.where(acceptable_values == user_val)[0][0]
        results = np.asarray(results)

        return np.asarray(results[:, finder])

    else:
        warnings.warn('Acceptable Values Are: ' + ', '.join(acceptable_values))