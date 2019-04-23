import warnings
import os
from tqdm import tqdm

from mis import delimeter_func, tif_separation, zfill_scan, order_dir
from h5 import h5images_wra, h5path_exists


def import_images(file, images_loc, scans = False, fill_num = 4, delete = False,
                  import_type = 'uint32', delimeter_function = delimeter_func, force_reimport = False):

    """Allows the user to import all .tif images into the .h5 file
    :param file:
    :param images_loc:
    :param fill_num:
    :param delete:
    :param import_type:
    :param delimeter_function:
    :return:
    """

    #Give the user the option to select which scans they want to import
    #If the scan already exsists as the user if they want to reimport this or skip
    #Ask if they want to skip all repeats


    sorted_images_loc = sorted(os.listdir(images_loc))
    if scans != False:
        pre_scans = [str(s) for s in scans]
        master_scan = []
        for scan in pre_scans:
            if scan in sorted_images_loc:
                master_scan.append(scan)
            else:
                print('{} Scan Not Found - Not Imported'.format(scan))
        sorted_images_loc = master_scan
        
    zfill_sorted_images_loc = zfill_scan(sorted_images_loc,fill_num)
    its = len(sorted_images_loc)
    for i in tqdm(range(0,its)):
        folder = sorted_images_loc[i]
        directory = images_loc+'/'+folder
        im_loc,im_name = order_dir(directory)
        im_name = [tif_separation(string, func = delimeter_function ) for string in im_name]

        path2exsist = '/images/{}'.format(zfill_sorted_images_loc[i])

        if h5path_exists(file, path2exsist) == True and force_reimport == False:
            print("Scan {} Already Imported. Will Not Continue. "
                  "Force Reimport With force_reimport = True".format(sorted_images_loc[i]))

        elif h5path_exists(file, path2exsist) == True and force_reimport == True:
            print("Deleting Scan {} And Reimporting".format(sorted_images_loc[i]))
            h5images_wra(file, zfill_sorted_images_loc[i], im_loc,
                         im_name, delete = False, import_type = import_type)

        elif h5path_exists(file, path2exsist) == False:
            h5images_wra(file, zfill_sorted_images_loc[i], im_loc,
                         im_name, delete=delete, import_type=import_type)


def images_group_exsist(file, scan):
    exists = h5path_exists(file, 'images/{}'.format(scan))
