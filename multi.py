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
                its.append((self,i, j,self.image_array, self.median_blur_distance, self.median_blur_height, self.stdev_min))
    elif isinstance(num_rows, tuple) and isinstance(num_columns, tuple):
        first_row = num_rows[0]
        last_row = num_rows[1]
        first_column = num_columns[0]
        last_column = num_columns[1]
        for i in range(first_row, last_row):
            for j in range(first_column, last_column):
                its.append((self,i, j,self.image_array, self.median_blur_distance, self.median_blur_height, self.stdev_min))
    return its


def initialize_vectorize(self, num_rows, num_columns):
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
        for i in range(0, num_rows):
            for j in range(0, num_columns):
                master_row.append(i)
                master_column.append(j)
    its = master_row, master_column

    return its

def analysis(self, rows, columns, default_cores = True,
             stdev_min = 35, med_blur_distance = 4, med_blur_height = 10, multiplier = 1):
    """Runs the pixel_analysis function defined in pixel.py through starmap multiprocessing

    Paramters
    =========

    :param self:
    :param rows:
    :param columns:
    :param default_cores:

    Return
    ======
    A multi-dimesional array consisting of:
    row_column - row and column values 'for the current index'
    summed_dif - summed diffraction ' '
    ttheta - a 1D 2theta array  ' '
    chi - a 1D chi array ' '
    ttheta_corr - a 1D 2theta array that has been median blurred ' '
    ttheta_centroid - a multi-dimensional array consisting of 2theta centroid values ' '
    chi_cor -  - a 1D chi array that has been median blurred ' '
    chi_centroid - a multi-dimensional array consisting of chi centroid values ' '
    full_roi - a corrected region of interest on the current selection
    """

    #Add background correction to analysis

    self.median_blur_distance = med_blur_distance
    self.median_blur_height = med_blur_height
    self.stdev_min = stdev_min
    background_dic_basic = scan_background(self, multiplier = multiplier)

    if default_cores == True:
        core_count = int(cpu_count()/2)
    else:
        core_count = default_cores
    image_array = centering_det(self, group='filenumber')
    self.image_array = np.asarray(image_array)
    its = iterations(self,rows, columns)
    pool = Pool(core_count)

    #Run multiprocessing on pixel iterations
    results = parallel_progbar(pixel_analysis, its, nprocs = default_cores, starmap = True)

    pool.close()
    pool.join()


    if False in results:
        warnings.warn('Not Enough RAM For Batch Processing. Program Auto Quit. Please Use Slower Functionality')
    self.results = results
    print('Results Saved As self.results')

def pooled_return(results, user_val ):
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

    acceptable_values = ['row_column', 'summed_dif', 'ttheta', 'chi', 'ttheta_corr', 'ttheta_centroid','chi_corr',
                         'chi_centroid', 'full_roi']
    if user_val in acceptable_values:
        acceptable_values = np.asarray(acceptable_values)
        finder = np.where(acceptable_values == user_val)[0][0]
        results = np.asarray(results)

        return np.asarray(results[:, finder])


    else:
        warnings.warn('Acceptable Values Are: ' + ', '.join(acceptable_values))

def better_multi(self, rows, columns, med_blur_distance = 4, med_blur_height = 10, stdev_min = 35, nprocs = 1):
    def worker(its, out_q):
        major_out = []
        for chunk in its:
            self, row, column, image_array, median_blur_distance, median_blur_height, stdev_min = chunk
            out = pixel_analysis(self, row, column, image_array, median_blur_distance, median_blur_height, stdev_min)
            major_out.append(out)
        out_q.put(major_out)

    self.median_blur_distance = med_blur_distance
    self.median_blur_height = med_blur_height
    self.stdev_min = stdev_min
    background_dic_basic = scan_background(self, multiplier = 0)
    image_array = centering_det(self, group='filenumber')
    self.image_array = np.asarray(image_array)
    its = iterations(self,rows, columns)
    chunksize = int(math.ceil(len(its) / float(nprocs)))

    out_q = Queue()
    procs = []

    for i in tqdm(range(nprocs), desc = "Procs"):
        chunk_its = its[chunksize * i:chunksize * (i + 1)]
        p = Process(
            target=worker, args=(chunk_its, out_q))
        procs.append(p)
        p.start()

    resultdict = []
    for i in tqdm(range(nprocs), desc = "Results"):
        resultdict.append(out_q.get())


    for pr in tqdm(procs, desc = "Join"):
        pr.join()

    master_results = []
    for re in resultdict:
        master_results.extend(re)

    return master_results

def best_analysis(self, rows, columns, med_blur_distance = 4, med_blur_height = 10, stdev_min = 35, multiplier = 1):
    """
    :param self:
    :param rows:
    :param columns:
    :param med_blur_distance:
    :param med_blur_height:
    :param stdev_min:
    :param multiplier:
    :return: A numpy matrix of every pixel asked. Each pixel contains row_column,
    (row, column), summed_dif, ttheta, chi, ttheta_centroid_finder, ttheta_centroid,
    chi_centroid_finder, chi_centroid, full_roi
    """
    self.median_blur_distance = med_blur_distance
    self.median_blur_height = med_blur_height
    self.stdev_min = stdev_min
    background_dic_basic = scan_background(self, multiplier=multiplier)

    image_array = centering_det(self, group='filenumber')
    self.image_array = np.asarray(image_array)
    row, column = initialize_vectorize(self,rows, columns)
    vectorize_pixel_analysis = np.vectorize(pixel_analysis_v2,
                                            excluded=['self','median_blur_distance', 'median_blur_height', 'stdev_min'])
    self.pbar_val = 0
    widgets = ['Progress: ', Percentage(), ' ', Bar(marker='-', left='[', right=']'),
               ' ', Timer(), '  ', ETA(), ' ', FileTransferSpeed()]  # see docs for other options
    self.pbar = ProgressBar(widgets=widgets, maxval=len(row)+1)
    self.pbar.start()

    results = vectorize_pixel_analysis(self,row,column,self.median_blur_distance, self.median_blur_height, self.stdev_min)
    readable_results = []
    for re in results:
        readable_results.append(np.asarray(re))
    readable_results = np.asarray(readable_results)

    return readable_results



