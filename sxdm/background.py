import numpy as np
import h5py

from h5 import h5grab_data
from mis import centering_det


def scan_background(self, amount2ave=3, multiplier=1):
    """Create background images for each scan.

    Takes the first "amount2ave" and last "amount2ave" images of each scan and average them together to each scan.
    Create a dictionary of these background images.

    Parameters
    ==========
    self: (SXDMFrameset)
    amount2ave: (int)
        amount of images from the beginning and enf of each scan to average together
    multiplier: (int/float)
        multiplier for each background scan

    Returns
    =======
    A dictionary of background images with entries for each scan number
    """
    # Grab data
    unshifted_array = centering_det(self=self,
                                    group='filenumber',
                                    center_around=-1,
                                    summed=False)

    first = 0
    store = []

    # Get the first and last 3 (default = 3) images from map to make background images from
    for array in unshifted_array:
        last = np.shape(array)[0] - 1
        col_last = np.shape(array)[1] - 1
        user_last = col_last - amount2ave + 1
        store.append(np.concatenate([array[first][0:amount2ave], array[last][user_last:last]]))

    # Create blank arrays to store data in
    background_loc_store = []
    scans = self.scan_numbers

    # Format these images into a location we can pass onto h5grab_data
    for i, array in enumerate(store):
        background_sub = []
        for number in array:
            try:
                corrected_number = str(int(np.round(number, 0))).zfill(6)
                background_sub.append('images/{}/{}'.format(scans[i], corrected_number))
            except:
                pass
            try:
                background_loc_store.append(background_sub)
            except:
                pass

    background_store = []

    # Average each scans images together
    with h5py.File(self.file, 'r') as hdf:

        for scan in background_loc_store:
            middle_store = []

            for location in scan:
                data = hdf.get(location)
                data = np.array(data)

                middle_store.append(data)

            background_store.append(np.mean(middle_store, axis=0))

    # Create a dictionary of these entries so it is easier to get info out
    background_dic = {}
    for j, scan in enumerate(scans):
        background_dic[scan] = background_store[j] * multiplier
    self.background_dic = background_dic

    return background_dic


def scan_background_finder(destination, background_dic):
    """The destination is the scan numbers associated with a given pixel location. This will take all scans in a pixel
    location and return a numpy array of their appropriate background images.

    Parameters
    ==========
    destination: (numpy array)
        the output of h5get_image_destination(self, pixel)
        list of scan numbers which the user wants to get the background images for

    background_dic: (dic)
        the dictionary otuput from the scan_background() function

    Returns
    =======
    A numpy array of background images corresponding to the scans in the destination input
    """

    # Take the destination and convert it into something readable for the dictionary entry
    scans = [value.split('/')[1] for value in destination]

    background = []
    for scan in scans:
        background.append(background_dic[scan])
        #scan4background.append(scan)

    return background
