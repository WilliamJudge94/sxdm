import warnings
import os
from tqdm import tqdm

from mis import delimeter_func, tif_separation, zfill_scan, order_dir
from h5 import h5images_wra, h5path_exists


def import_images(file, images_loc, scans=False, fill_num=4, delete=False,
                  import_type='uint32', delimeter_function=delimeter_func, force_reimport=False):

    """Allows the user to import all .tif images into the .h5 file

    Parameters
    ==========
    file (str)
        the user defined hdf5 file
    image_loc (str)
        the location of the images folder from the beamline
    scans (nd.array)
        the scans the user would like to import
    fill_num (int)
        the amount of numbers in the images folders names
    delete (bool)
        if True all the data from the selected scans will be set to zero
    import_type (str)
        a string value passed into imageio.imread().astype(import_type)
    delimeter_function (function)
        a function which determines the image number. redefine this if 26 - ID -C naming scheme changes
    force_reimport (bool)
        set to True if you would like to force reimport images

    Returns
    =======
    Nothing
    """

    # Get a list of files in directory

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
        
    zfill_sorted_images_loc = zfill_scan(scan_list=sorted_images_loc,
                                         fill_num=fill_num)

    its = len(sorted_images_loc)

    # For each of the sorted image folders import all the images
    for i in tqdm(range(0, its)):
        folder = sorted_images_loc[i]
        directory = images_loc+'/'+folder
        im_loc, im_name = order_dir(path=directory)
        im_name = [tif_separation(string=string,
                                  func=delimeter_function) for string in im_name]

        path2exsist = '/images/{}'.format(zfill_sorted_images_loc[i])

        # If the path already exists do not import the images again
        if h5path_exists(file, path2exsist) == True and force_reimport == False:
            print("Scan {} Already Imported. Will Not Continue. "
                  "Force Reimport With force_reimport = True".format(sorted_images_loc[i]))

        elif h5path_exists(file, path2exsist) == True and force_reimport == True:
            print("Deleting Scan {} And Reimporting".format(sorted_images_loc[i]))
            h5images_wra(file=file,
                         scan=zfill_sorted_images_loc[i],
                         im_loc=im_loc,
                         im_name=im_name,
                         delete=False,
                         import_type=import_type)

        elif h5path_exists(file, path2exsist) == False:
            h5images_wra(file=file,
                         scan=zfill_sorted_images_loc[i],
                         im_loc=im_loc,
                         im_name=im_name,
                         delete=delete,
                         import_type=import_type)


def images_group_exsist(file, scan):
    """See if the images group exists.
    """
    exists = h5path_exists(file=file,
                           loc='images/{}'.format(scan))
