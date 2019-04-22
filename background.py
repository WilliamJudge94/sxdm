import numpy as np

from h5 import h5grab_data
from mis import centering_det

def scan_background(self, amount2ave=3, multiplier=1):
    unshifted_array = centering_det(self, group='filenumber', center_around=-1)
    first = 0
    store = []

    # Get the first and last 3 (default = 3) images from map to make background images from
    for array in unshifted_array:
        last = np.shape(array)[0] - 1
        col_last = np.shape(array)[1] - 1
        user_last = col_last - amount2ave + 1
        store.append(np.concatenate([array[first][0:amount2ave], array[last][user_last:last]]))

    background_loc_store = []
    scans = self.scan_numbers

    # Format these images into a location we can pass onto h5grab_data
    for i, array in enumerate(store):
        background_sub = []
        for number in array:
            corrected_number = str(int(np.round(number, 0))).zfill(6)
            background_sub.append('images/{}/{}'.format(scans[i], corrected_number))
        background_loc_store.append(background_sub)

    background_store = []

    # Average each scans images together
    for scan in background_loc_store:
        middle_store = []
        for location in scan:
            data = h5grab_data(self.file, location)
            middle_store.append(data)
        background_store.append(np.mean(middle_store, axis=0))

        # Create a dictionary of these entries so it is easier to get info out
    background_dic = {}
    for j, scan in enumerate(scans):
        background_dic[scan] = background_store[i] * multiplier
    self.background_dic = background_dic
    return background_dic


def scan_background_finder(destination, background_dic):
    scans = [value.split('/')[1] for value in destination]
    background = []
    for scan in scans:
        background.append(background_dic[scan])
    return background
