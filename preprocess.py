import numpy as np
import os
import warnings

from h5 import h5create_dataset, h5create_group, h5path_exists, h5grab_data,\
    h5read_attr, h5set_attr, h5replace_data, h5del_group
from mis import scan_num_convert, centering_det, grab_dxdy
from det_chan import return_det


def initialize_group(self):
    """ Initialized the group assigned by the user to the user defined file.

    From the scan numbers the program determines the scan_theta as well checking if identical
    settings have already been imported. If so the program reloads saved settings

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframeset

    Returns
    =======
    Nothing - sets /scan_numbers and /scan_theta
    """
    # When .mda files are missing this function cannot import /scan_theta
    try:
        if h5path_exists(self.file, self.dataset_name) == False:

            # Creating groups and initializing their datasets
            h5create_group(self.file, self.dataset_name)
            scan_numbers = scan_num_convert(self.scan_numbers)
            h5create_dataset(self.file, self.dataset_name+'/scan_numbers', scan_numbers)
            h5create_dataset(self.file, self.dataset_name+'/scan_theta', np.asarray(self.scan_theta))

        else:

            # Grabbing old data from stored datasets
            old_scan_nums = h5grab_data(self.file, self.dataset_name+'/scan_numbers')
            new_scan_nums = self.scan_numbers
            new_scan_nums = np.asarray(scan_num_convert(new_scan_nums))
            print('Saved Scans: ' + str(old_scan_nums))
            print('Current User Input: '+str(new_scan_nums))

            try:
                # See if an alignment data has already been set
                checker = self.dxdy_store
            except:
                try:
                    # Try to grab old alignment data
                    self.dxdy_store = grab_dxdy(self)
                except Exception as ex:
                    warnings.warn('{} - Alignment Data Not Found'.format(ex))

            # If the old scans equal the new scans tell the User
            if np.array_equal(old_scan_nums, new_scan_nums) == True:
                print('Importing Identical Scans. Reloading Saved Data...\n')

            # If they don't give them the option to delete the old group and start again
            else:
                user_val = input('New Scans Detected. Would You Like To Delete Current Group And Start Again? y/n ')

                if user_val == 'n':
                    print('Importing Saved Scans...')

                elif user_val == 'y':
                    print('Replacing - '+self.dataset_name+' - Group\n')
                    scan_numbers = scan_num_convert(self.scan_numbers)
                    try:
                        h5del_group(self.file, self.dataset_name + '/scan_numbers')
                    except:
                        pass
                    try:
                        h5del_group(self.file, self.dataset_name + '/scan_theta')
                    except:
                        pass
                    try:
                        h5create_dataset(self.file, self.dataset_name + '/scan_numbers', scan_numbers)
                    except:
                        pass
                    try:
                        h5create_dataset(self.file, self.dataset_name + '/scan_theta', np.asarray(self.scan_theta))
                    except:
                        pass

    except Exception as ex:
        print('preprocess.py/initialize_group', ex)
        warnings.warn('Cannot Initialize Group. Some .mda Files Might Be Missing...')


def initialize_zoneplate_data(self, reset=False):
    """Initialize values for the zoneplate used as well as detector pixel size.

    Asks the user what the parameters of the zone plate are and detector pixel size. If they have been already set
    then the program displays the current values when setting up SXDMFrameset object

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframset
    reset (bool)
        if True this allows the user to reset all values

    Returns
    =======
    Nothing - sets values inside /zone_plate/
    """
    if reset == False:
        if h5path_exists(self.file, 'zone_plate/D_um') == False:
            D_um_val = input('What Is The Diameter Of The Zone Plate Used In Microns? (Typically 150)')
            h5create_dataset(self.file, 'zone_plate/D_um', D_um_val)
        else:
            print('Diameter Of The Zone Plate Is Set To {} microns'.format(h5grab_data(self.file, 'zone_plate/D_um')))

        if h5path_exists(self.file, 'zone_plate/d_rN_nm') == False:
            d_rN_nm_val = input('What Is The Outer Most d Spacing Is '
                                'For The Zone Plate Used In Nanometers? (Typically 20)')
            h5create_dataset(self.file, 'zone_plate/d_rN_nm', d_rN_nm_val)
        else:
            print('Outermost Zone Plate d Spacing Is Set To {} nanometers'.format(h5grab_data(self.file,
                                                                                              'zone_plate/d_rN_nm')))

        if h5path_exists(self.file, 'zone_plate/detector_pixel_size') == False:
            detector_pixel_size_val = input('What Pixel Size Of The Detector In Microns? (Typically 15)')
            h5create_dataset(self.file, 'zone_plate/detector_pixel_size', detector_pixel_size_val)
        else:
            print('The Size Of Your Detector Pixels Is Set To {} microns'.format(h5grab_data(self.file,
                                                                                             'zone_plate/detector_pixel_size')))

    elif reset == True:
        D_um_val = input('What Is The Diameter Of The Zone Plate Used In Microns? (Typically 150)')
        h5replace_data(self.file, 'zone_plate/D_um', D_um_val)
        d_rN_nm_val = input('What Is The Outer Most d Spacing Is For The Zone Plate Used In Nanometers? (Typically 20)')
        h5replace_data(self.file, 'zone_plate/d_rN_nm', d_rN_nm_val)
        detector_pixel_size_val = input('What Pixel Size Of The Detector In Microns? (Typically 15)')
        h5replace_data(self.file, 'zone_plate/detector_pixel_size', detector_pixel_size_val)

def initialize_experimental_attrs(self):
    """Initialized the Kev and detector's theta position.

    Sets attributes of Kev and detector theta position to the current user defined group

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframeset

    Returns
    =======
    Nothing - sets Kev and detector_theta attributes
    """
    try:
        Kev = h5read_attr(file=self.file, loc=self.dataset_name, attribute_name='Kev')
        detector_theta_center = h5read_attr(file=self.file, loc=self.dataset_name, attribute_name='detector_theta')
        self.detector_theta_center = detector_theta_center
        print('The Detector Theta Value Is {} Degrees and the Kev is {} Kev\n'.format(detector_theta_center, Kev))
    except:
        detector_theta_center = input('What Is The Angle In Degrees Of The Detector For This Experiment? (Typically 16.7)\n')
        Kev = input('What Was The Kev For This Experiment? (Typically 9)\n')
        h5set_attr(file=self.file, loc=self.dataset_name, attribute_name='Kev', attribute_val=Kev)
        h5set_attr(file=self.file, loc=self.dataset_name, attribute_name='detector_theta', attribute_val=detector_theta_center)


def max_det_val(self, detector='fluor'):
    """Used to determine the max values for a given detector channel

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframeset
    detector (str)
        value to be passed into the return_det() function

    Returns
    =======
    the max values for all scans for a given detector channel input
    """
    if h5path_exists(self.file, 'detector_channels/'+detector) == True:
        data = return_det(self.file, self.scan_numbers, group=detector)
        max_array = [np.max(array) for array in data[0]]
        return max_array
    else:
        warnings.warng('Path Does Not Exist')


def init_dxdy(self):
    """Initializes a group that scan store dxdy data

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframeset

    Returns
    =======
    Nothing - creates a blank self.dxdy_store variable
    """
    dxdy = {}
    for i, scan in enumerate(self.scan_numbers):
        dxdy[i] = (0, 0)
    self.dxdy_store = dxdy


def gaus_check(self, center_around=False, default=False):
    """Determines the intensity change over all group scans

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframset

    Returns
    =======
    the x and y values for a plot that shows intensity vs scan angle.
    also auto displays the figure
    """

    # Grab roi data
    input_arrays = centering_det(self=self,
                                 group='roi',
                                 center_around=center_around,
                                 summed=False,
                                 default=default)
    nan_finder_pre = []
    dims = np.shape(input_arrays)


    # Get rid of np.nan
    for array in input_arrays:
        nan_finder_pre.append(np.argwhere(np.isnan(array)))

    nan_finder = []

    for array in nan_finder_pre:
        for arr in array:
            nan_finder.append(arr)

    uni_nan = np.unique(nan_finder, axis=0)

    mask = [[1 for x in range(dims[2])] for y in range(dims[1])]

    for array in uni_nan:
        row = array[0]
        column = array[1]
        mask[row][column] = np.nan

    gaus_arrays_pre = []
    for array in input_arrays:
        gaus_arrays_pre.append(np.add(array, mask))

    # get the correct theta value for each roi sum
    y = np.nansum(gaus_arrays_pre, axis=(1, 2))
    x = self.scan_theta

    gaus_array = []

    for i, theta in enumerate(x):
        gaus_array.append([theta, y[i]])

    # Sort the arrays from lowest to highest theta position
    gaus_array = np.asarray(sorted(gaus_array, key=lambda x: x[0]))
    x = gaus_array[:, 0]
    y = gaus_array[:, 1]
    return x, y


def initialize_saving(self):
    """Initialize the ability to save data

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframset

    Returns
    =======
    Nothing - creates the filename_savedata.h5 file to save data to
    """
    saved_filename = self.file[0:-3] + '_savedata.h5'
    self.save_filename = saved_filename
    if os.path.isfile(saved_filename) == False:
        f = open(saved_filename, "w+")
        f.close()
    try:
        h5create_group(saved_filename, self.dataset_name)
    except:
        pass


def initialize_scans(self, scan_numbers=False, fill_num=4):
    """Initialize all necessities for each scan

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframeset
    scan_numbers (nd.array of int)
        the list of scan numbers the user wants to create [178, 178, ...]
    fill_num (int)
        the zfill number for the scan number integers

    Returns
    =======
    Nothing - sets self.scan_numbers, self.det_smpl_theta, and self.scan_theta
    """
    # When .mda files are missing this script cannot pull scan information
    try:
        if scan_numbers != False:
            self.scan_numbers = scan_num_convert(scan_numbers, fill_num=fill_num)
        else:
            import_scans = h5grab_data(self.file, self.dataset_name + '/scan_numbers')
            import_scans = [int(scan) for scan in import_scans]
            self.scan_numbers = scan_num_convert(list(import_scans), fill_num=fill_num)
        self.det_smpl_theta = str(h5grab_data(self.file, 'detector_channels/sample_theta')[0]).zfill(2)

        scan_theta_grab = [h5grab_data(self.file, 'mda/' + scan + '/D' + self.det_smpl_theta)
                           for scan in self.scan_numbers]

        self.scan_theta = [np.mean(scan, axis=(0, 1)) for scan in scan_theta_grab]

    except Exception as ex:
        print('preprocess.py/initialize_scans', ex)
        warnings.warn('Cannot Initialize Scans. Some .mda Files Might Be Missing...')

