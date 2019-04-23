import warnings
import numpy as np
import os
from scipy.ndimage import shift
import psutil

from det_chan import return_det
from h5 import h5grab_data, h5set_attr, h5read_attr

def order_dir(path):
    """For a selected path return the ordered filenames

    :param path:
    :return:
    """
    images = sorted(os.listdir(path))
    im_loc = []
    im_name = []
    for i in images:
        im_loc.append(path+'/'+i)
        im_name.append(i)
    return im_loc,im_name

        
def zfill_scan(scan_list,fill_num):
    new_scan = []
    for scan in scan_list:
        new_scan.append(scan.zfill(fill_num))
    return new_scan

    
def create_file(file):
    if (os.path.isfile(file)):
        pass
    else:
        f = open(file,'w+')
        f.close()
            
def delimeter_func(string):
    return string.split('_')[-1][0:-4]

def tif_separation(string,func = delimeter_func):
    return func(string)

def figure_size_finder(images):
    im_shape = np.shape(images)
    im_len = len(im_shape)
    if im_len <= 2:
        return 1
    else:
        start_values = np.arange(1,10)
        starting_idx = np.where(np.arange(1,10)**2 >= len(images))[0][0]
        starting = start_values[starting_idx]
        return starting

def scan_num_convert(scan_numbers, fill_num = 4):
    if isinstance(scan_numbers[0],str):
        scan_numbers = [int(scan) for scan in scan_numbers]
    elif isinstance(scan_numbers[0],int):
        scan_numbers = [str(scan) for scan in scan_numbers]
        scan_numbers = zfill_scan(scan_numbers,fill_num = fill_num)
    return scan_numbers

def shape_check(self):
    hybrid_x = return_det(self.file, self.scan_numbers, group='hybrid_x')[0]
    hybrid_y = return_det(self.file, self.scan_numbers, group='hybrid_y')[0]

    shape_hybrid_x = np.shape(hybrid_x)
    shape_hybrid_y = np.shape(hybrid_y)

    len_x = len(shape_hybrid_x)
    len_y = len(shape_hybrid_y)

    if len_x != 3 and len_y != 3:
        warnings.warn('Scan Shapes Are Not The Same!')
    else:
        print('Scan Dimensions Are Equivalent')

def val_check(array, resolution):
    min_res = array[0] - resolution
    max_res = array[0] + resolution
    output = []
    for value in array:
        if min_res <= value <= max_res:
            output.append(True)
        else:
            output.append(False)

    return all(output)


def resolution_check(self, user_resolution_um = 0.0005):
    hybrid_x = return_det(self.file, self.scan_numbers, group='hybrid_x')[0]
    hybrid_y = return_det(self.file, self.scan_numbers, group='hybrid_y')[0]

    shape_hybrid_x = np.asarray([np.shape(scan) for scan in hybrid_x]) - [1, 1]
    shape_hybrid_y = np.asarray([np.shape(scan) for scan in hybrid_y]) - [1, 1]

    max_x = np.asarray([np.max(scan, axis=(0, 1)) for scan in hybrid_x])
    min_x = np.asarray([np.min(scan, axis=(0, 1)) for scan in hybrid_x])

    max_y = np.asarray([np.max(scan, axis=(0, 1)) for scan in hybrid_y])
    min_y = np.asarray([np.min(scan, axis=(0, 1)) for scan in hybrid_y])

    dif_x = max_x - min_x
    dif_y = max_y - min_y

    res_x = []
    res_y = []

    for i, value in enumerate(dif_x):
        len_hybrid_x = shape_hybrid_x[i][1]
        len_hybrid_y = shape_hybrid_y[i][0]
        current_x = dif_x[i]
        current_y = dif_y[i]
        res_x.append(current_x / len_hybrid_x)
        res_y.append(current_y / len_hybrid_y)

    dif_res_x = [res_x[0] - step for step in res_x]
    dif_res_y = [res_y[0] - step for step in res_y]


    validation_x = val_check(dif_res_x, user_resolution_um)
    validation_y = val_check(dif_res_y, user_resolution_um)

    if validation_x == True and validation_y == True:
        print('X and Y Resolutions are within ' +str(user_resolution_um *1000)+' nanometers from eachother')
    else:
        if validation_x != True and validation_y != True:
            warnings.warn('Resolution in X and Y Differ Between Scans')
        elif validation_x == True and validation_y != True:
            warnings.warn('Resolution in Y Differ Between Scans')
        elif validation_x != True and validation_y == True:
            warnings.warn('Resolution in X Differ Between Scans')


def image_numbers(self):
    filenumbers = return_det(self.file, self.scan_numbers, group='filenumber')[0]
    int_filenumbers = {}
    for i, scan in enumerate(filenumbers):
        int_filenumbers[self.scan_numbers[i]] = np.asarray(scan).astype(int)

    return int_filenumbers

def dic2array(dic):
    output_array = []
    for val in dic:
        output_array.append(dic[val])
    return output_array


def array2dic(array):
    new_dic = {}
    for i,dot in enumerate(array):
        new_dic[i] = (dot[0],dot[1])
    return new_dic


def array_shift(self, arrays2shift, centering_idx):
    complete_array = array2dic(h5grab_data(self.file, self.dataset_name + '/dxdy'))
    center = complete_array[centering_idx]
    center_x = center[0]
    center_y = center[1]
    translation_array = {}
    for array in complete_array:
        translation_array[array] = (center_x - complete_array[array][0], center_y - complete_array[array][1])
    shifted_arrays = []
    for i, array in enumerate(translation_array):
        trans = translation_array[array]
        movement_x = trans[0]
        movement_y = trans[1]
        shifted_arrays.append(shift(arrays2shift[i], (movement_y, movement_x), cval=np.nan))

    return shifted_arrays


def centering_det(self, group = 'fluor', center_around = False, summed = False):
    if center_around == False:
        center_around = set_centering(self)
    else:
        pass
    array = return_det(self.file, self.scan_numbers, group=group)[0]

    if center_around != -1:
        ims = array_shift(self, array, center_around)
    else:
        ims = array
    if summed == False:
        return ims
    elif summed == True:
        return np.sum(ims, axis = 0)


def set_centering(self):
    try:
        center_around = h5read_attr(self.file, self.dataset_name + '/dxdy', 'centering')
        user_ask = input('A Centering Index of - ' + str(center_around) + ' - Has Been Found.' +
                         ' Would You Like To Use This Index To Center? y/n ')
        if user_ask == 'n':
            center_around = input('Which Scan Do You Want To Center Around? - Input Index - ')
            h5set_attr(self.file, self.dataset_name + '/dxdy', 'centering', center_around)

        elif user_ask == 'y':
            pass
        return int(center_around)

    except:
        center_around = input('Which Scan Do You Want To Center Around? - Input Index - ')
        h5set_attr(self.file, self.dataset_name + '/dxdy', 'centering', center_around)

    return int(center_around)

def ram_check():
    mems=psutil.virtual_memory()
    return round(mems[2],1)


def median_blur(input_array, median_blur_distance,
                cut_off_value_above_mean):
    iteration_number = np.shape(input_array)[
        0]  # Finds out the length of the array you want to median blur. This equals the number of iterations you will perform
    median_array = []  # Create a blank array for the final output
    for j in range(0, iteration_number):
        median_array = []
        if j - median_blur_distance < 0:  # Corrects bounds if the program is out of bounds
            its_blur = range(0, j + median_blur_distance + 1)
        if j + median_blur_distance > iteration_number:
            its_blur = range(j - median_blur_distance, iteration_number)
        if j - median_blur_distance >= 0 and j + median_blur_distance <= iteration_number:
            its_blur = range(j - median_blur_distance, j + median_blur_distance + 1)

        for i in its_blur:  # Takes the indicies for one iteration and gets the values of these locations from the users array
            try:
                median_array.append(input_array[i])
            except:
                pass
        if input_array[j] > np.median(
                median_array) + cut_off_value_above_mean:  # Replace a high value with the median value
            input_array[j] = np.median(median_array)
        else:
            pass

    return input_array

def grab_dxdy(self):
    data = h5grab_data(self.file, self.dataset_name + '/dxdy')
    store = {}
    for i, d in enumerate(data):
        store[i] = (d[0], d[1])
    return store
