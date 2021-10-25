import warnings
import os
from tqdm import tqdm
import numpy as np

from mis import delimiter_func, tif_separation, zfill_scan, order_dir
from h5 import h5images_wra, h5path_exists, h5create_file, h5create_dataset
from readingmda import readMDA


def import_images(file, images_loc, scans=False, fill_num=4,
                  import_type='uint32', delimiter_function=delimiter_func, force_reimport=False):

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
    import_type (str)
        a string value passed into imageio.imread().astype(import_type)
    delimiter_function (function)
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
        if os.path.isdir(directory):
            im_loc, im_name = order_dir(path=directory)
            im_name = [tif_separation(string=string,
                                    func=delimiter_function) for string in im_name]

            path2exsist = '/images/{}'.format(zfill_sorted_images_loc[i])

            # If the path already exists do not import the images again
            if h5path_exists(file, path2exsist) == True and force_reimport == False:
                print("Scan {} Already Imported. Will Not Continue. "
                    "Force Reimport With force_reimport = True".format(sorted_images_loc[i]))

            # If the path already exists but the User wants to force reimport then reimport
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
                            delete=False,
                            import_type=import_type)


def images_group_exsist(file, scan):
    """See if the images group exists.
    """
    exists = h5path_exists(file=file,
                           loc='images/{}'.format(scan))


def import_mda(mda_path, hdf5_save_directory, hdf5_save_filename,
               single_file=False, maxdims=2):
    """Allows the User to import all .mda image and line scan data into an hdf5 format

    Parameters
    ==========
    mda_path (str)
        the string path to the folder holding the .mda files

    hdf5_save_directory (str)
        the path location where you would like to save your data to
        EXAMPLE: '/home/Desktop'

    hdf5_save_filename (str)
        the file inside that path in which you would like to save data to (DO NOT INCLUDE ".h5")
        EXAMPLE: 'test'

    single_file (str)
        the location of the file to import

    maxdims (int)
        the maximum dimensions for the readMDA function to import from the .mda file


    Returns
    =======
    Nothing - Will Not Reimport Files
    """

    unsucessful_import_files = []
    reason_for_fail = []
    file_path = '{}/{}.h5'.format(hdf5_save_directory, hdf5_save_filename)

    if single_file == False:
        file_locs, filenames = order_dir(mda_path)

    elif single_file:
        split_files = single_file.split('/')

        file_locs = [single_file,]
        filenames = [split_files[-1],]

    # Create a file path if it does not exists.

    if os.path.exists(file_path):
        pass
    else:
        h5create_file(loc=hdf5_save_directory, name=hdf5_save_filename)

    # For each .mda file in the directory scan through the detectors and import the data
    for i, file in tqdm(enumerate(file_locs)):
        file_name = filenames[i]
        current_scan_number_import = delimiter_func(string=file_name)

        try:
            output = readMDA(file, verbose=0, maxdim=maxdims)
    
            # Determining if it is 2D or 1D
            if len(output) == 3:
                source_data = output[2]
                if maxdims >= 3:
                    xrf_data = output[3]
                flips = True
            elif len(output) == 2:
                source_data = output[1]
                if maxdims >= 3:
                    xrf_data = output[2]
                flips = False
            elif len(output) == 4:
                source_data = output[2]
                if maxdims >= 3:
                    xrf_data = output[3]
                flips = False

            else:
                warnings.warn("Input Scan Dimensions Are Not 1D or 2D. Error In Importing Scan - {}".format(
                    current_scan_number_import))
    
            for dats in source_data.d:
                detector_number = dats.number + 1
                current_det_num = str(detector_number).zfill(2)
                save_path = 'mda/{}/D{}'.format(current_scan_number_import, current_det_num)
    
                # If the save path exsists don't bother saving it again
                if h5path_exists(file=file_path, loc=save_path):
                    pass
    
                # All image data is flipped - unflip the 2D data
                else:
                    raw_data2save = dats.data
                    if flips:
                        data2save = np.flip(np.flip(raw_data2save), axis=1)
                    else:
                        data2save = raw_data2save
                    h5create_dataset(file=file_path, ds_path=save_path, ds_data=data2save)

            # XRF Importer Written By - Dr. Michael Stueckelberger
            if maxdims >= 3:
                # Save 3D data in h5 file
                for dats in xrf_data.d:
                    detector_number = dats.number + 1
                    current_det_num = str(detector_number).zfill(2)
                    save_path = 'xrf/{}/D{}'.format(current_scan_number_import, current_det_num)
                    raw_data2save = dats.data
                    if h5path_exists(file=file_path, loc=save_path):
                        pass
                    else:
                        if flips:
                            pass
                            #data2save = np.flip(np.flip(raw_data2save), axis=1)
                            #not yet clear how raw XRF data will be saved in that case ... skip for now
                        else:
                            data2save = raw_data2save
                        h5create_dataset(file=file_path, ds_path=save_path, ds_data=data2save)

                # Save position data in h5 file
                data2save = output[2].p[0].data
                save_path = f'pos/{current_scan_number_import}/inner_hor'
                if h5path_exists(file=file_path, loc=save_path):
                    pass
                else:
                    h5create_dataset(file=file_path, ds_path=save_path, ds_data=data2save)

                data2save = output[1].p[0].data
                save_path = f'pos/{current_scan_number_import}/outer_hor'
                if h5path_exists(file=file_path, loc=save_path):
                    pass
                else:
                    h5create_dataset(file=file_path, ds_path=save_path, ds_data=data2save)

        except Exception as ex:
            unsucessful_import_files.append(file)
            reason_for_fail.append(ex)
    
    
    for idxs, f in enumerate(unsucessful_import_files):
        warnings.warn(f'Unable to Import File -- {f} -- because -- {reason_for_fail[idxs]}')
