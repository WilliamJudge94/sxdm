import warnings
import numpy as np
from tqdm import tqdm

from h5 import h5group_list, h5create_dataset, h5grab_data, h5del_group, h5list_group

def space_check(fluor, roi, detector_scan, filenumber, sample_theta, hybrid_x, hybrid_y, mis):
    """Based on the input variables this checks to see if the user has put any spaces into their group names.

    Warns the user that they are using spaces

    Parameters
    ----------
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
    sample_theta; (int)
        the detector channel that corresponds to the sample theta
    hybrid_x: (int)
        the detector channel that corresponds to the hybrid_x
    hybrid_y: (int)
        the detector channel that corresponds to the hybrid_y
    mis: (dic)
        a miscellaneous dictionary with entries of detector channels that might be usefull. ex. 2Theta, Ring_Current

    Return
    ------
    (bool) on whether or not there is a space in any of the dictionary entries given by the user
    """
    dic = False
    ints = False
    master_dic = [fluor, roi, detector_scan, mis]
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
    #Show the User where they are wrong
    if dic == True:
        warnings.warn('There Are Spaces In Your Dictionary Entries. Please Correct This')
    if ints == True:
        warnings.warn('filenumber And sample_theta Are In The Incorrect Format. Please Make Them Integers')

    if ints == False and dic == False:
        return True
    else:
        warnings.warn('Will Not Continue Till Issues Are Fixed')
        return False



def setup_det_chan(file,fluor,roi,detector_scan,filenumber,sample_theta,hybrid_x, hybrid_y,mis):
    """Sets detector channel information and stores it in the .h5 file

    Parameters
    ----------
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
    sample_theta; (int)
        the detector channel that corresponds to the sample theta
    hybrid_x: (int)
        the detector channel that corresponds to the hybrid_x
    hybrid_y: (int)
        the detector channel that corresponds to the hybrid_y
    mis: (dic)
        a miscellaneous dictionary with entries of detector channels that might be usefull. ex. 2Theta, Ring_Current

    Returns
    -------
    Nothing
    """
    cont = space_check(fluor,roi,detector_scan,filenumber,sample_theta,hybrid_x,hybrid_y,mis)

    if cont == True:
        total = [fluor,roi,detector_scan,[filenumber],[sample_theta],[hybrid_x],[hybrid_y],mis]
        acceptable_types = ['fluor','roi','detector_scan','filenumber','sample_theta','hybrid_x','hybrid_y','mis']

        for i,dic in enumerate(total):
            det_type = acceptable_types[i]

            # Make sure that the input is in the acceptable values
            if det_type not in acceptable_types:
                warnings.warn('Not An Acceptable Detector_Type. Please Choose From The Following Selection: '+', '.join(acceptable_types))

            # Set the detector_channel values in the .h5 file
            else:
                if det_type not in ['filenumber','sample_theta','hybrid_x','hybrid_y']:
                    for entry in dic:
                        #Create the Entry And Save Data
                        try:
                            h5create_dataset(file,'/detector_channels/'+det_type+'/'+entry,dic[entry])
                        except:
                            warnings.warn(entry+' - '+det_type+' - Detector Channel Already Exists. Will Not Overwrite')
                else:
                    try:
                        h5create_dataset(file,'/detector_channels/'+det_type,dic)

                    except:
                        warnings.warn(' - '+det_type+' - Detector Channel Already Exists. Will Not Overwrite')

def del_det_chan(file):
    """Deletes the /detector_channels group
    Parameters
    ----------
    file (str):
        the .h5 file you would like to delete the detector_channel group from

    Returns
    -------
    Nothing
    """
    h5del_group(file,'/detector_channels')

def disp_det_chan(file):
    """Allows the user to quicky see what all values are set to in the detector_channel group

    Parameters
    ----------
    file (str):
        the .h5 file you would like to delete the detector_channel group from

    Returns
    -------
    prints the current values of the detector_channel group. If no values are currently set it displays something the
    User can copy and paste into a cell to set the appropriate dectector values
    """
    try:
        det_chans = h5group_list(file,'/detector_channels/')

        types = []
        dic_values = []
        for channel in det_chans:
            types.append(channel[0])

        # Try to grab the current detector_channel values to display to the User
        for chan_type in types:
            try:
                dic_values.append(h5group_list(file,'/detector_channels/'+chan_type))
            except:
                dic_values.append(h5grab_data(file,'/detector_channels/'+chan_type))

        for i,vals in enumerate(dic_values):
            text = (types[i]+' = ')
            lens = len(vals)-1
            for j,sets in enumerate(vals):
                try:
                    dummy = h5grab_data(file,'/detector_channels/'+types[i]+'/'+sets[0])
                    if j == 0:
                        text = text + '{\n \t'
                    text = (text+
                    str("'"+sets[0])+"'"+':'+' '+
                    str(h5grab_data(file,'/detector_channels/'+types[i]+'/'+sets[0]))+',\n \t')
                    if j == lens:
                        text = text + '}'
                except:
                    text = text + str(sets)
            print(text+'\n')
    # If you can't then display something that can help the User set the appropriate variables
    except:
        warnings.warn('No Detector Channels Set. Configure Them As You See Above')
        base = ("fluor = {\n\t'Fe':33,\n\t'Cu':3,\n\t'Ni':4,\n\t'Mn':30\n\t}"+'\n'+
                "roi = {\n\t'ROI_1':5,\n\t'ROI_2':6,\n\t'ROI_3':7,\n\t}"+'\n'+
                "detector_scan = {\n\t'Main_Scan':65,\n\t}"+'\n'+
                "filenumber = 10"+'\n'+
                "sample_theta = 56"+'\n'+
                "hybrid_x = 67" + '\n' +
                "hybrid_y = 68" + '\n' +
                "mis = {'2Theta':55,\n\t'Storage_Ring_Current':70,\n\t'Relative_r_To_Detector':54,}"+'\n'
               )
        print(base)


def return_det(file, scan_numbers, group='fluor'):
    """Returns all information for a given detector channel for an array of scan numbers

    Parameters
    ----------
    file: (str)
        the .h5 file location
    scan_numbers: (np.array)
        an array of scan numbers the user wants to get a specific detector channel information for
    group: (str)
        a string corresponding to a group value that the user wants to return

    Returns
    -------
    The specified detector channel for all specified scan numbers, the .mda detector value
    """

    # Get the acceptable values
    acceptable_values = h5grab_data(file, 'detector_channels')
    if group in acceptable_values:
        path = 'detector_channels/' + group
        acceptable_values = h5grab_data(file, path)
        end = False
        fluor_array = []

        # Keep asking the User for an acceptable value if it doesnt exsist
        while end == False:
            if group not in ['filenumber', 'sample_theta', 'hybrid_x', 'hybrid_y']:
                user_val = str(input('Which - ' + group + ' - Would You Like To Center To: ' + str(acceptable_values)))

            else:
                user_val = str(acceptable_values[0])
                acceptable_values = [str(user_val)]

            if user_val in acceptable_values:
                if group not in ['filenumber', 'sample_theta', 'hybrid_x', 'hybrid_y']:
                    det = str(h5grab_data(file, path + '/' + user_val))
                else:
                    det = user_val
                det = 'D' + det.zfill(2)
                for i, scan in enumerate(scan_numbers):
                    fluors = h5grab_data(file, 'mda/' + scan + '/' + det)
                    fluor_array.append(fluors)
                end = True
                return fluor_array, user_val
            else:
                warnings.warn('Please Type In An Acceptable Value')
    else:
        warnings.warn('Please Type In An Acceptable Value')
