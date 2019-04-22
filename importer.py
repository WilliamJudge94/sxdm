import warnings
import os
from tqdm import tqdm

from mis import delimeter_func, tif_separation, zfill_scan, order_dir
from h5 import h5images_wra


def import_images(file, images_loc, fill_num = 4, delete = False, 
                  import_type = 'uint32', delimeter_function = delimeter_func):

    """Allows the user to import all .tif images into the .h5 file

    :param file:
    :param images_loc:
    :param fill_num:
    :param delete:
    :param import_type:
    :param delimeter_function:
    :return:
    """
    sorted_images_loc = sorted(os.listdir(images_loc))
    zfill_sorted_images_loc = zfill_scan(sorted_images_loc,fill_num)
    its = len(sorted_images_loc)
    for i in tqdm(range(0,its)):
        folder = sorted_images_loc[i]
        directory = images_loc+'/'+folder
        im_loc,im_name = order_dir(directory)
        im_name = [tif_separation(string,func = delimeter_function ) for string in im_name]
        h5images_wra(file,zfill_sorted_images_loc[i],im_loc,im_name,delete = delete,import_type = import_type)
