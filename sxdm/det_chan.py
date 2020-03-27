import warnings
import numpy as np
from tqdm import tqdm

from h5 import h5group_list, h5create_dataset, h5grab_data, h5del_group

def space_check(fluor, roi, detector_scan, filenumber, sample_theta, hybrid_x, hybrid_y, mis, xrf):
    """Based on the input variables this checks to see if the user has put any spaces into their group names.

    Warns the user that they are using spaces

    Parameters
    ==========
    fluor: (dic)
        a dictionary entry with all the Fluorescence images names as well as their corresponding .mda detector channel
        value
    roi: (dic)
        a dictionary entry with all the Region of Interest images names as well as their corresponding .mda detector channel
        vale
    detector_scan: (int)
        the dectector channel that corresponds to the scanning of the detector - used to determine detector dimensions
    filenumber: (int)
        the dectector channel that corresponds to the image file numbers
    sample_theta: (int)
        the detector channel that corresponds to the sample theta
    hybrid_x: (int)
        the detector channel that corresponds to the hybrid_x
    hybrid_y: (int)
        the detector channel that corresponds to the hybrid_y
    mis: (dic)
        a miscellaneous dictionary with entries of detector channels that might be usefull. ex. 2Theta, Ring_Current
    xrf: (dic)
        an x-ray fluorescence dictionary with entries of the detector channels CORRESPOND TO THE DETECTOR CHANNELS
        UNDER THE 'xrf' HEADING THE THE HDF FILE!!!
    Return
    ======
    (bool) on whether or not there is a space in any of the dictionary entries given by the user
    """
    dic = False
    ints = False
    master_dic = [fluor, roi, detector_scan, mis, xrf]
    master_int = [filenumber, sample_theta, hybrid_x, hybrid_y]

    # See if there are any spaces in the dictionary names
    for dictionary in master_dic:
        master_keys = dictionary.keys()
        for key in master_keys:
            if ' ' in key:
                dic = True

    # Makes sure that the integers are actually integers
    for integers in master_int:
        if isinstance(integers, int):
            pass
        else:
            ints = True

    # Show the User where they are wrong
    if dic == True:
        warnings.warn('There Are Spaces In Your Dictionary Entries. Please Correct This')
    if ints == True:
        warnings.warn('filenumber And sample_theta Are In The Incorrect Format. Please Make Them Integers')

    if ints == False and dic == False:
        return True
    else:
        warnings.warn('Will Not Continue Till Issues Are Fixed')
        return False


def setup_det_chan(file,
                   fluor,
                   roi,
                   detector_scan,
                   filenumber,
                   sample_theta,
                   hybrid_x,
                   hybrid_y,
                   mis,
                   xrf):
    """Sets detector channel information and stores it in the .h5 file

    Parameters
    ==========
    file: (str)
        the hdf file path
    fluor: (dic)
        a dictionary entry with all the Fluorescence images names as well as their corresponding .mda detector channel
        vale
    roi: (dic)
        a dictionary entry with all the Region of Interest images names as well as their corresponding .mda detector channel
        vale
    detector_scan: (int)
        the dectector channel that corresponds to the scanning of the detector - used to determine detector dimensions
    filenumber: (int)
        the dectector channel that corresponds to the image file numbers
    sample_theta: (int)
        the detector channel that corresponds to the sample theta
    hybrid_x: (int)
        the detector channel that corresponds to the hybrid_x
    hybrid_y: (int)
        the detector channel that corresponds to the hybrid_y
    mis: (dic)
        a miscellaneous dictionary with entries of detector channels that might be usefull. ex. 2Theta, Ring_Current
    xrf: (dic)
        an x-ray fluorescence dictionary with entries of the detector channels CORRESPOND TO THE DETECTOR CHANNELS
        UNDER THE 'xrf' HEADING THE THE HDF FILE!!!

    Returns
    =======
    Nothing
    """

    # Check to see if spaces are in anything the user wrote
    cont = space_check(fluor=fluor,
                       roi=roi,
                       detector_scan=detector_scan,
                       filenumber=filenumber,
                       sample_theta=sample_theta,
                       hybrid_x=hybrid_x,
                       hybrid_y=hybrid_y,
                       mis=mis,
                       xrf=xrf)

    if cont == True:
        total = [fluor,
                 roi,
                 detector_scan,
                 [filenumber],
                 [sample_theta],
                 [hybrid_x],
                 [hybrid_y],
                 mis,
                 xrf]

        acceptable_types = ['fluor', 'roi', 'detector_scan',
                            'filenumber', 'sample_theta',
                            'hybrid_x', 'hybrid_y', 'mis', 'xrf']

        for i, dic in enumerate(total):
            det_type = acceptable_types[i]

            # Make sure that the input is in the acceptable values
            if det_type not in acceptable_types:
                warnings.warn('Not An Acceptable Detector_Type. '
                              'Please Choose From The Following Selection: '+', '.join(acceptable_types))

            # Set the detector_channel values in the .h5 file
            else:
                if det_type not in ['filenumber', 'sample_theta', 'hybrid_x', 'hybrid_y']:
                    for entry in dic:

                        # Create the Entry And Save Data
                        try:
                            h5create_dataset(file=file,
                                             ds_path='/detector_channels/'+det_type+'/'+entry,
                                             ds_data=dic[entry])
                        except:
                            warnings.warn(entry+' - '+det_type+' - Detector Channel Already Exists. Will Not Overwrite')
                else:
                    try:
                        h5create_dataset(file=file,
                                         ds_path='/detector_channels/'+det_type,
                                         ds_data=dic)

                    except:
                        warnings.warn(' - '+det_type+' - Detector Channel Already Exists. Will Not Overwrite')


def del_det_chan(file):
    """Deletes the /detector_channels group
    Parameters
    ==========
    file (str):
        the .h5 file you would like to delete the detector_channel group from

    Returns
    =======
    Nothing
    """
    h5del_group(file=file,
                group='/detector_channels')


def disp_det_chan(file):
    """Allows the user to quicky see what all values are set to in the detector_channel group

    Parameters
    ==========
    file (str):
        the .h5 file you would like to delete the detector_channel group from

    Returns
    =======
    prints the current values of the detector_channel group. If no values are currently set it displays something the
    User can copy and paste into a cell to set the appropriate dectector values
    """
    try:
        det_chans = h5group_list(file=file,
                                 group_name='/detector_channels/')
        types = []
        dic_values = []
        for channel in det_chans:
            types.append(channel[0])

        # Try to grab the current detector_channel values to display to the User
        for chan_type in types:
            try:
                dic_values.append(h5group_list(file=file,
                                               group_name='/detector_channels/'+chan_type))
            except:
                dic_values.append(h5grab_data(file=file,
                                              data_loc='/detector_channels/'+chan_type))
        for i, vals in enumerate(dic_values):
            text = (types[i]+' = ')
            lens = len(vals)-1
            for j, sets in enumerate(vals):
                try:
                    dummy = h5grab_data(file=file,
                                        data_loc='/detector_channels/'+types[i]+'/'+sets[0])
                    if j == 0:
                        text = text + '{\n \t'
                    text = (text +

                    str("'"+sets[0])+"'"+':'+' ' +

                    str(h5grab_data(file=file,
                                    data_loc='/detector_channels/'+types[i]+'/'+sets[0]))+',\n \t')
                    if j == lens:
                        text = text + '}'
                except:
                    text = text + str(sets)
            print(text+'\n')

    # If you can't then display something that can help the User set the appropriate variables
    except:
        warnings.warn('No Detector Channels Set. Configure Them As You See Above')
        base = ("fluor = {\n\t'Fe':2,\n\t'Cu':2,\n\t'Ni':2,\n\t'Mn':2\n\t}"+'\n' +
                "roi = {\n\t'ROI_1':2,\n\t'ROI_2':2,\n\t'ROI_3':2,\n\t}"+'\n' +
                "detector_scan = {\n\t'Main_Scan':2,\n\t}"+'\n' +
                "filenumber = 2"+'\n' +
                "sample_theta = 2"+'\n' +
                "hybrid_x = 2" + '\n' +
                "hybrid_y = 2" + '\n' +
                "xrf = {\n\t'Fe':2,\n\t'Cu':2,\n\t'Ni':2,\n\t'Full':2\n\t}" + '\n' +
                "mis = {'2Theta':2,\n\t'Storage_Ring_Current':2,\n\t'Relative_r_To_Detector':2,}"+'\n'
               )
        print(base)


def return_det(file, scan_numbers, group='fluor', default=False, dim_correction=True):
    """Returns all information for a given detector channel for an array of scan numbers

    Parameters
    ==========
    file: (str)
        the .h5 file location
    scan_numbers: (np.array)
        an array of scan numbers the user wants to get a specific detector channel information for
    group: (str)
        a string corresponding to a group value that the user wants to return
    default: (bool)
        If True this will default to the first acceptable detector_channel in the hdf5 file
    dim_correction: (bool)
        If False this will not add rows and columns to the returned array to make them all the same shape

    Returns
    =======
    The specified detector channel for all specified scan numbers, the .mda detector value
    """

    # Get the acceptable values
    acceptable_values = h5grab_data(file=file,
                                    data_loc='detector_channels')
    if group in acceptable_values:
        path = 'detector_channels/' + group
        acceptable_values = h5grab_data(file=file,
                                        data_loc=path)
        end = False
        fluor_array = []

        # Keep asking the User for an acceptable value if it doesnt exsist
        while end == False:
            if group not in ['filenumber', 'sample_theta', 'hybrid_x', 'hybrid_y']:
                if default == False:
                    user_val = str(input('Which - ' + group + ' - Would You Like To Center To/Return: ' + str(acceptable_values)))
                elif default == True:
                    user_val = acceptable_values[0]
            else:
                user_val = str(acceptable_values[0])
                acceptable_values = [str(user_val)]

            # Grab the right data
            if user_val in acceptable_values:
                if group not in ['filenumber', 'sample_theta', 'hybrid_x', 'hybrid_y']:
                    det = str(h5grab_data(file=file,
                                          data_loc=path + '/' + user_val))
                else:
                    det = user_val
                det = 'D' + det.zfill(2)

                shapes = []

                for i, scan in enumerate(scan_numbers):
                    
                    if group != 'xrf':
                        fluors = h5grab_data(file=file,
                                         data_loc='mda/' + scan + '/' + det)
                    elif group == 'xrf':
                        fluors = h5grab_data(file=file, data_loc='xrf/' + scan + '/' + det)
                        
                    
                    if group == 'filenumber':
                        shapes.append(np.shape(fluors))
                        
                    fluor_array.append(fluors)
                        
                end = True


                # Correcting for terrible matlab code filenumber logging
                if group == 'filenumber':
                    fluor_array = []
                    fluor_array = true_filenumbers(file=file, scan_numbers=scan_numbers, shapes=shapes)

                # Correct the dimensions of each scan to make sure they are all the same
                if dim_correction == True:
                    m_row, m_column = max_dims(fluor_array)
                    n_fluor_array = det_dim_fix(fluor_array, m_row, m_column)

                else:
                    n_fluor_array = fluor_array

                return n_fluor_array, user_val
            else:
                warnings.warn('Please Type In An Acceptable Value')
    else:
        warnings.warn('Please Type In An Acceptable Value')


def true_filenumbers(file, scan_numbers,  shapes):
    """Since the .mda files do not store the correct file_names/image_names inside of it. This creates an appropriate file number
    for each pixel in a scan

    Parameters
    ==========

    file (str)
        the location of the .h5 file
    scan_numbers (nd.array)
        array of all the scan numbers the User wishes to create image numbers for
    shapes (nd.array)
        the shapes of all the scans

    Returns:
    =======
    an nd.array with the .tif image numbers/locations for each voxel of the scan
    """
    final_locations = []

    # for each scan number
    for i, scan in tqdm(enumerate(scan_numbers), desc='File # Shifting', unit='scans', total=len(scan_numbers)):

        # Determine the shape of the main files
        shape = shapes[i]

        # get the im numbers
        im_list = h5group_list(file, '/images/{}'.format(scan))

        # get the np array
        im_list_np = np.array(im_list)

        # get the im numbers
        im_nums_pre = im_list_np[:, 0]

        im_nums = [float(i) for i in im_nums_pre]

        # length check
        if len(im_nums) != shape[0] * shape[1]:
            warnings.warn('Image Numbers Wrong - Fix Code/Imports - Scan {}'.format(scan))

        # flip
        ims_flip1 = np.flip(im_nums)

        # reshape
        ims_reshape = ims_flip1.reshape((shape[0], shape[1]))

        # flip again
        locations = np.flip(ims_reshape, axis=1)

        final_locations.append(locations)

    return final_locations


def max_dims(array):
    """Get the max dimensions for an array of 2D images

    Parameters
    ==========
    array (np.ndarray)
        a 3 dimensional array

    Returns
    =======
    the max rows and the max columns round for the 3 dimensionsal array
    """
    m_row = []
    m_column = []
    for im in array:
        shape = np.shape(im)
        m_row.append(shape[0])
        m_column.append(shape[1])
    max_row = max(m_row)
    max_column = max(m_column)

    return max_row, max_column


def add_column(im, max_column):
    """Add a numpy.nan column to an image array based on how many columns in the max amount of columns

    Parameters
    ==========
    im (a 2D array)
        the image array to add columns to
    max_column (int)
        the final amount of columns the user want to make the im array

    Returns
    =======
    a new im array with the User selected max_column
    """
    shape = np.shape(im)
    its = max_column - shape[1]

    a = np.empty((shape[0], its,))
    a[:] = np.nan

    return np.hstack((im, a))


def add_row(im, max_row):
    """Add a numpy.nan rows to an image array based on how many rows in the max amount of rows

    Parameters
    ==========
    im (a 2D array)
        the image array to add columns to
    max_row (int)
        the final amount of rows the user want to make the im array

    Returns
    =======
    a new im array with the User selected max_row
    """
    shape = np.shape(im)
    its = max_row - shape[0]

    a = np.empty((its, shape[1],))
    a[:] = np.nan

    return np.vstack((im, a))


def det_dim_fix(array, max_row, max_column):
    """Add columns and rows to image matrix to make everything the same dimensions

    Parameters
    ==========
    array (np.ndarray)
        a 3D array of images
    max_row (int)
        the max amount of rows the User would like to make all the images
    max_column (int)
        the max amount of columns the User would like to make all the images

    Returns
    =======
    the 3D image array with dimensions (#images, max_row, max_column)
    """
    master = []
    for im in array:
        first = add_column(im, max_column)
        second = add_row(first, max_row)
        master.append(second)
    return master
