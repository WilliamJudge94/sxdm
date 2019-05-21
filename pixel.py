import numpy as np
from multiprocessing.pool import ThreadPool
from multiprocessing import Process, Queue
import logging

from mis import ram_check, median_blur
from h5 import h5get_image_destination, h5grab_data
from background import scan_background, scan_background_finder
from datetime import datetime



def theta_maths(summed_dif, median_blur_distance, median_blur_height, stdev_min,q = False):
    ttheta = np.sum(summed_dif, axis=0)
    ttheta = median_blur(ttheta, median_blur_distance, median_blur_height)
    ttheta2 = np.asarray(ttheta)
    ttheta_centroid_finder, ttheta_centroid = centroid_finder(ttheta2, stdev_min)
    if q == False:
        return ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2
    else:
        q.put([ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2])

def chi_maths(summed_dif, median_blur_distance, median_blur_height, stdev_min,q = False):
        chi = np.sum(summed_dif, axis=1)
        chi = median_blur(chi, median_blur_distance, median_blur_height)
        chi2 = np.asarray(chi)
        chi_centroid_finder, chi_centroid = centroid_finder(chi2, stdev_min)
        if q == False:
            return chi, chi_centroid, chi_centroid_finder
        else:
            q.put([chi, chi_centroid, chi_centroid_finder])

def centroid_finder(oneDarray_start, stdev_min = 35):
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

def grab_pix(array,row,column, int_convert = False):
    output = array[:, row, column]
    if int_convert == True:
        int_output = []
        for value in output:
            if np.isnan(value) == False:
                int_output.append(int(np.round(value,0)))
            else:
                int_output.append(value)
        return int_output
    else:
        return np.asarray(output)

def sum_pixel(self, images_loc):
    pixel_store = []
    for image in images_loc:
        pixel_store.append(h5grab_data(self.file, image))
    return pixel_store

def pixel_analysis(self, row, column, image_array, median_blur_distance, median_blur_height, stdev_min):
    if column == 0:
        if ram_check() > 90:
            return False
    pix = grab_pix(array = image_array, row = row, column = column, int_convert = True)
    destination = h5get_image_destination(self = self, pixel = pix)
    each_scan_diffraction = sum_pixel(self = self, images_loc = destination)


    #Background Correction
    backgrounds = scan_background_finder(destination = destination, background_dic = self.background_dic)
    each_scan_diffraction_post = np.subtract(each_scan_diffraction, backgrounds)

    summed_dif = np.sum(each_scan_diffraction_post, axis = 0)


    #pooled: Work In Progress
    #q_theta = Queue()
    #q_chi = Queue()

    #ttheta_pool_results = Process(target = theta_maths, args = (summed_dif, median_blur_distance, median_blur_height,stdev_min,q_theta))
    #chi_pool_results = Process(target = chi_maths, args = (summed_dif, median_blur_distance, median_blur_height,stdev_min,q_chi))

    #ttheta_pool_results.start()
    #chi_pool_results.start()

    #ttheta_pool_results.join()
    #chi_pool_results.join()

    #ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2 = q_theta.get()
    #chi, chi_centroid, chi_centroid_finder = q_chi.get()

    #seperate analysis (SLOW)

    ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2 = theta_maths(summed_dif, median_blur_distance, median_blur_height, stdev_min)
    chi, chi_centroid, chi_centroid_finder = chi_maths(summed_dif, median_blur_distance, median_blur_height, stdev_min)

    full_roi = np.sum(ttheta2)


    return (row, column), summed_dif, ttheta, chi, ttheta_centroid_finder, ttheta_centroid, chi_centroid_finder, chi_centroid, full_roi



def pixel_analysis_v2(self, row, column, median_blur_distance, median_blur_height, stdev_min):
    image_array = self.image_array
    try:
        self.pbar_val = self.pbar_val + 1
        self.pbar.update(self.pbar_val)
    except:
        pass
    if column == 0:
        if ram_check() > 90:
            return False
    t = datetime.now()
    pix = grab_pix(array = image_array, row = row, column = column, int_convert = True)
    destination = h5get_image_destination(self = self, pixel = pix)
    each_scan_diffraction = sum_pixel(self = self, images_loc = destination)

    #Background Correction
    backgrounds = scan_background_finder(destination = destination, background_dic = self.background_dic)
    each_scan_diffraction_post = np.subtract(each_scan_diffraction, backgrounds)

    summed_dif = np.sum(each_scan_diffraction_post, axis = 0)


    ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2 = theta_maths(summed_dif, median_blur_distance, median_blur_height, stdev_min)
    chi, chi_centroid, chi_centroid_finder = chi_maths(summed_dif, median_blur_distance, median_blur_height, stdev_min)

    full_roi = np.sum(ttheta2)


    results = [(row, column), summed_dif, ttheta, chi, ttheta_centroid_finder, ttheta_centroid, chi_centroid_finder, chi_centroid, full_roi]

    return results
