import numpy as np
import h5py
from tqdm import tqdm


from pixel import grab_pix, sum_pixel, sum_pixel_v2
from h5 import h5get_image_destination, open_h5, close_h5
from background import scan_background_finder, scan_background
from mis import grab_fov_dimensions


def summed2d_all_data(self, bkg_multiplier=0):
    """Loads the summed diffraction patter without using a large amount of RAM

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframeset object
    bkg_multiplier (int)
        the multiplier for the background images

    Returns
    =======
    the 2D summed diffraction pattern
    """
    # Grab the fov dimensions
    dims = grab_fov_dimensions(self)

    # Determining the rows and columns
    rows = dims[1] - 1
    columns = dims[2] - 1
    image_array = self.image_array

    self.background_dic = scan_background(self=self, multiplier=bkg_multiplier)

    # open the hdf file

    for column in tqdm(range(0, columns), desc='Loading 2D'):
        for row in range(0, rows):

            # Getting scan locations
            pix = grab_pix(array=image_array, row=row, column=column, int_convert=True)
            destination = h5get_image_destination(self=self, pixel=pix)

            # Getting diffraction images
            each_scan_diffraction = sum_pixel(self=self, images_loc=destination)

            if bkg_multiplier != 0:
                # Background Correction
                backgrounds = scan_background_finder(destination=destination, background_dic=self.background_dic)

                each_scan_diffraction_post = np.subtract(each_scan_diffraction, backgrounds)
            else:
                # If bkg is set to zero no need for background correction
                each_scan_diffraction_post = each_scan_diffraction

            summed_dif = np.sum(each_scan_diffraction_post, axis=0)

            try:
                total2 = np.add(total2, summed_dif)
            except:
                total2 = summed_dif

    return total2


def summed2d_all_data_v2(self, bkg_multiplier=0):
    """Loads the summed diffraction patter without using a large amount of RAM

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframeset object
    bkg_multiplier (int)
        the multiplier for the background images

    Returns
    =======
    the 2D summed diffraction pattern
    """
    # Grab the fov dimensions
    #dims = grab_fov_dimensions(self)
    #user_input = input('What Scan Are You Doing? centroid/roi/all ?')

    user_input = 'all'

    if user_input == 'roi':
        rows_pre = self.roi_analysis_total_rows
        columns_pre = self.roi_analysis_total_columns
    elif user_input == 'centroid':
        rows_pre = self.centroid_analysis_total_rows
        columns_pre = self.centroid_analysis_total_columns
    elif user_input == 'all':
        dims = grab_fov_dimensions(self)
        rows_pre = dims[1] - 1
        columns_pre = dims[2] - 1

    # Determining the rows and columns
    if isinstance(rows_pre, int):
        start_row = 0
        end_row = rows_pre
    elif isinstance(rows_pre, tuple):
        start_row = rows_pre[0]
        end_row = rows_pre[1]

    if isinstance(columns_pre, int):
        start_column = 0
        end_column = columns_pre
    elif isinstance(columns_pre, tuple):
        start_column = columns_pre[0]
        end_column = columns_pre[1]


    image_array = self.image_array

    bkg = scan_background(self=self, multiplier=bkg_multiplier)

    # open the hdf file
    with h5py.File(self.file, 'r') as hdf:

        for row in tqdm(range(start_row, end_row), desc='Loading 2D'):
            for column in range(start_column, end_column):

                # Getting scan locations
                pix = grab_pix(array=image_array, row=row, column=column, int_convert=True)
                destination = h5get_image_destination(self=self, pixel=pix)

                # Getting diffraction images
                each_scan_diffraction = sum_pixel_v2(images_loc=destination, file=hdf)


                if bkg_multiplier != 0:
                    # Background Correction
                    backgrounds = scan_background_finder(destination=destination, background_dic=self.background_dic)
                    try:
                        each_scan_diffraction_post = np.subtract(each_scan_diffraction, backgrounds)
                    except Exception as ex:
                        print(ex)
                else:
                    # If bkg is set to zero no need for background correction
                    each_scan_diffraction_post = each_scan_diffraction

                summed_dif = np.sum(each_scan_diffraction_post, axis=0)

                try:
                    total2 = np.add(total2, summed_dif)
                except:
                    total2 = summed_dif

    return total2

