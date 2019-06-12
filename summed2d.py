# make a way to sum all the difraction images inside of a user defined group - no centering, grab the full roi

import numpy as np
import h5py
from tqdm import tqdm


from pixel import grab_pix, sum_pixel
from h5 import h5get_image_destination
from background import scan_background_finder, scan_background
from mis import grab_fov_dimensions


def summed2d_all_data(self, bkg_multiplier=0):
    dims = grab_fov_dimensions(self)
    rows = dims[1] - 1
    columns = dims[2] - 1
    image_array = self.image_array

    bkg = scan_background(self=self, multiplier=bkg_multiplier)

    total = []
    for column in tqdm(range(0, columns)):
        for row in range(0, rows):

            pix = grab_pix(array=image_array, row=row, column=column, int_convert=True)
            destination = h5get_image_destination(self=self, pixel=pix)
            each_scan_diffraction = sum_pixel(self=self, images_loc=destination)

            if bkg_multiplier != 0:
                # Background Correction
                backgrounds = scan_background_finder(destination=destination, background_dic=self.background_dic)

                each_scan_diffraction_post = np.subtract(each_scan_diffraction, backgrounds)
            else:
                each_scan_diffraction_post = each_scan_diffraction

            summed_dif = np.sum(each_scan_diffraction_post, axis=0)

            total.append(summed_dif)
    total2 = np.sum(total, axis=0)
    return total2
