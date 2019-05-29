import numpy as np
import warnings
import os
from tqdm import tqdm

from multi import pooled_return
from h5 import h5grab_data


def centroid_roi_map(results, map_type='chi_centroid'):
    """Returns the centroid or roi

    Parameters
    ==========

    results (nd.array)
        self.results or the output of self.analysis
    map_type (str)
        the value the user would like to return
        acceptable values are chi_centroid, ttheta_centroid, or full_roi

    Returns
    =======
    the user selected map in an nd.array
    """

    # Grab data
    row_col = pooled_return(results, 'row_column')
    new_row_col = []

    # Reorder data into an array with correct pixel location
    for array in row_col:
        new_row_col.append([array[0], array[1]])
    new_row_col = np.asarray(new_row_col)
    max_x = np.max(new_row_col[:, 1]) + 1
    max_y = np.max(new_row_col[:, 0]) + 1

    user_picker = pooled_return(results, map_type)
    mapper = [[0 for x in range(max_x)] for y in range(max_y)]

    for i, array in enumerate(row_col):
        row = array[0]
        col = array[1]
        mapper[row][col] = user_picker[i]

    return mapper


def twodsummed(results):
    """Returns the summed diffraction pattern for the analysis output

    Parameters
    ==========
    results (nd.array)
        the self.results or output of self.analysis

    Returns
    =======
    the summed diffraction patter from the analysis output
    """
    return np.sum(pooled_return(results, 'summed_dif'), axis=0)


def pixel_analysis_return(results, row, column, show_accep_vals=False):
    """Easy return of the results based on the input row and column value

    Parameters
    ==========

    results (nd.array)
        self.results or output of self.analysis
    row (int)
        the row the user would like to look at
    column (int)
        the column the user would like to look at

    Returns
    =======
    A dictionary with entries:

    'row_column',
    'summed_dif',
    'ttheta',
    'chi',
    'ttheta_corr',
    'chi_corr',
    'ttheta_cent',
    'chi_cent',
    'roi'

    """
    acceptable_values = ['row_column', 'summed_dif', 'ttheta',
                         'chi', 'ttheta_corr', 'ttheta_cent', 'chi_corr',
                         'chi_cent', 'roi']
    if False in results:
        warnings.warn('Not Enough RAM During Analysis - No Usable Results Output')

    if show_accep_vals is True:
        print(acceptable_values)
    rs = np.asarray(results)

    # Obtain the pixel results
    row_col = np.asarray(rs[:, 0])
    sumed = np.asarray(rs[:, 1])
    thetas = np.asarray(rs[:, 2])
    chis = np.asarray(rs[:, 3])
    ttheta_corr = np.asarray(rs[:, 4])
    ttheta_val = np.asarray(rs[:, 5])
    chi_corr = np.asarray(rs[:, 6])
    chi_val = np.asarray(rs[:, 7])
    roi = np.asarray(rs[:, 8])

    # Find the right pixel an store index
    for i, value in enumerate(row_col):
        if value == (row, column):
            idx = i
        else:
            pass

    # Store results
    master_array = [row_col[idx], sumed[idx], thetas[idx], chis[idx],
                    ttheta_corr[idx], ttheta_val[idx], chi_corr[idx],
                    chi_val[idx], roi[idx]]

    # Create the dictionary
    output_dic = {}
    for j, array in enumerate(master_array):
        output_dic[acceptable_values[j]] = array

    return output_dic


def make_video(image_folder, output_folder=False, outimg=None, fps=23, size=None,
               is_color=True, format="XVID"):
    """DEPRECIATED
    Create a video from a list of images.

    @param      outvid      output video
    @param      images      list of images to use in the video
    @param      fps         frame per second
    @param      size        size of each frame
    @param      is_color    color
    @param      format      see http://www.fourcc.org/codecs.php
    @return                 see http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html

    The function relies on http://opencv-python-tutroals.readthedocs.org/en/latest/.
    By default, the video will have the size of the first image.
    It will resize every image to this size before adding them to the video.
    """

    if output_folder == False:
        output_folder = '/home/will/Desktop/video.mp4'
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    images = sorted(images)

    from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize
    fourcc = VideoWriter_fourcc(*format)
    vid = None
    for image in images:
        image = image_folder + '/' + image
        if not os.path.exists(image):
            raise FileNotFoundError(image)
        img = imread(image)
        if vid is None:
            if size is None:
                size = img.shape[1], img.shape[0]
            vid = VideoWriter(output_folder, fourcc, float(fps), size, is_color)
        if size[0] != img.shape[1] and size[1] != img.shape[0]:
            img = resize(img, size)
        vid.write(img)
    vid.release()
    return vid


def maps_correct(user_map, new_bounds):
    """Takes the centroid_rou_map() function output and gives it new bounds

    Parameters
    ==========

    user_map (nd.array)
        the output of the centroid_roi_map function
    new_bounds (np.linspace)
        np.linspace(lowerbound, higherbound, dim of image)

    Returns
    =======
    nd.array of the user_map, but with new bounds rather than with the dimensions
    of the diffraction image
    """
    shape = np.shape(user_map)
    row = shape[0]
    column = shape[1]
    output = [[np.nan for x in range(column)] for y in range(row)]

    # Replace map value with new values
    for i in range(0, row - 1):
        for j in range(0, column - 1):
            try:

                output[i][j] = new_bounds[int(user_map[i][j])]

            except:
                pass
    return output


def saved_return(file, group, summed_dif_return=False):
    """Load saved data

    Parameters
    ==========

    file (str)
        a user defined hdf5 file
    group (str)
        the group the user would like to import
    summed_dif_return (bool)
        if True this will import all data. it is set to False because
        this import take up a lot of RAM

    Returns
    =======
    a nd.array thay can be set to the self.results value

    """
    acceptable_values = ['row_column', 'summed_dif', 'ttheta', 'chi',
                         'ttheta_corr', 'ttheta_centroid', 'chi_corr',
                         'chi_centroid', 'full_roi']
    pre_store = []
    for value in tqdm(acceptable_values):

        if value != 'summed_dif':
            data = h5grab_data(file, '{}/{}'.format(group, value))
            rc_appender = []
            if value == 'row_column':
                length_data = len(data)
                for rc_data in data:
                    rc_appender.append((rc_data[0], rc_data[1]))
                pre_store.append(rc_appender)

            else:
                pre_store.append(data)

        elif value == 'summed_dif' and summed_dif_return is True:
            data = h5grab_data(file, '{}/{}'.format(group, value))
            pre_store.append(data)

        elif value == 'summed_dif' and summed_dif_return is False:
            pre_store.append(np.zeros(length_data))

    results_store = []
    for i, iteration in enumerate(pre_store[0]):
        base_store = []
        for j, its in enumerate(pre_store):
            base_store.append(its[i])
        results_store.append(base_store)

    return np.asarray(results_store)
