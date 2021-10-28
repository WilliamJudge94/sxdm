import numpy as np
import imageio
import os
from tqdm import tqdm_notebook as tqdm
import matplotlib.pyplot as plt
import warnings

import h5py


def h5create_file(loc, name):
    """Creates hdf5 file

    Parameters
    ==========
    loc: (str)
        the location of the hdf5 file
    name: (str)
        the name of the hdf5 file WITHOUT .h5 at the end

    Returns
    =======
    Nothing
    """

    with h5py.File('{}/{}.h5'.format(loc, name), "w") as f:
        pass


#def h5read(file, data_loc):
#    """Reads .h5 file data at a set location in the file
#    DEPRECIATED

#    Parameters
#    ==========
#    file: (str)
#        a string of the file you are working on
    
#    data_loc: (str)
#        read what has been set to a certain location in the hdf5 file

#    Returns
#    =======
#    The value set to the user defined path
#    """
#    with h5py.File(file, 'r') as hdf:
#        g1 = hdf.get(data_loc)
#        g1_data = list(g1)
#    return g1_data


def h5delete_file(file):
    """Deletes the file set by the user

    Parameters
    ==========
    file: (str)
        the full location of the hdf5 file the user would like to delete

    Returns
    =======
    Nothing
    """
    os.remove(file)


#def h5list_group(file, group='base'):
#    """Displays all group members for a user defined group

#    Parameters
#    ==========
#    file: (str)
#        the file the user wishes to find the group list for
#    group: (str)
#        the subgroup the user want to look at

#    Returns
#    =======
#    a list of groups within the specified hdf5 location
#    """
#    with h5py.File(file, 'r') as hdf:
#        if group == 'base':
#            base_items = list(hdf.items())
#            base_items = np.array(base_items)
#        else:
#            base_items = hdf.get(group)
#            base_items = list(base_items)
#    return base_items


def h5grab_data(file, data_loc):
    """Returns the data stored in the user defined group

    Parameters
    ==========
    file (str):
        the user defined hdf5 file
    data_loc (str):
        the group the user would like to pull data from

    Returns
    =======
    the data stored int the user defined location
    """
    with h5py.File(file, 'r') as hdf:
        data = hdf.get(data_loc)
        data = np.array(data)

    return data


def h5create_group(file, group):
    """Creates a group based on the Users group input

    Parameters
    ==========
    file (str):
        the user defined hdf5 file
    group (str):
        the group the user would like to create inside the file

    Returns
    =======
    Nothing
    """
    with h5py.File(file, 'a') as hdf:
        hdf.create_group(group)


def h5create_dataset(file, ds_path, ds_data):
    """Creates a dataset in the user defined group with data equal to the user defined data

    Parameters
    ==========
    file: (str)
        the user defined hdf5 file
    ds_path: (str)
        the group path to the dataset inside the hdf5 file
    ds_data: (nd.array)
        a numpy array the user would like to store

    Returns
    =======
    Nothing
    """
    with h5py.File(file, 'a') as hdf:
        hdf.create_dataset(ds_path, data=ds_data)


#def h5create_subgroup(file, group, subgroup):
#    """Allows user to create a subgroup - Kinda useless

#    Useless
#    """
#    with h5py.File(file, 'a') as hdf:
#        hdf.create_group(group+'/'+subgroup)


def h5del_group(file, group):
    """Deletes the user defined group. DOES NOT REDUCE FILE SIZE

    Parameters
    ==========
    file: (str)
        the user defined hdf5 file
    group: (str)
        the group inside the hdf5 file the user would like to delete

    Returns
    =======
    Nothing
    """
    with h5py.File(file, 'a') as hdf:
        del hdf[group]


def h5del_data(file, group):
    """Sets all data equal to zero for a given dataset.

    Parameters
    ==========
    file: (str)
        the hdf5 file path
    group: (str)
        the group location in the hdf5 the user wants to delete the data for

    Returns
    =======
    Nothing
    """
    with h5py.File(file, "a") as hdf:
        init_data = hdf[group]
        init_data[...] = 0


def h5images_wra(file, scan, im_loc, im_name, delete=False, import_type='uint32'):
    """Used to import/delete .tif images into the .h5 file

    Parameters
    ==========

    file (str)
        the user defined hdf5 file
    scan (nd.array)
        the scan numbers the user wants to import
    im_loc (str)
        the location of the image file
    delete (bool)
        set to True if the user would like to delete the data in the hdf5 file
    import_type (str)
        string passed into imageio.imread(image).astype(import_type)

    Returns
    =======
    Nothing
    """
    for idx, image in enumerate(im_loc):
        if delete == False:
            im = imageio.imread(image).astype(import_type)
        write_path = '/images/'+scan+'/'+im_name[idx]
        try:
            h5create_dataset(file=file,
                             ds_path=write_path,
                             ds_data=im)
        except:
            if delete == False:
                #print(im.dtype)
                h5replace_data(file=file,
                               group=write_path,
                               data=im)
            elif delete == True:
                h5del_data(file=file,
                           group=write_path)


def h5replace_data(file, group, data):
    """Replaces all data in a dataset.

    Helps with space savings since deleting groups does not decrease the file size. Easier to replace data

    Parameters
    ==========

    file (str)
        the user defined hdf5 file
    group (str)
        the user defined group in the hdf5 file
    data (nd.array)
        the data the user would like to sub in

    Returns
    =======
    Nothing
    """
    
    with h5py.File(file, "a") as hdf:
        init_data = hdf[group]
        init_data[...] = data
        
        try:
            dtype1 = init_data.dtype
            dtype2 = data.dtype
            if dtype1 != dtype2:
                warnings.warn('Different import dtypes from original. HDF5 does not allow this change.'
                              'Please recreate the entire dataset if you would like to change the import dtype.')
        except:
            pass





def h5group_list(file, group_name='base'):
    """Displays all group members for a user defined group

    Parameters
    ==========
    file (str)
        the path to the hdf5 file
    group_name (str)
        the path to the group the user wants the Keys for. Set to 'base' if you want the top most group

    Returns
    =======
    a list of all the subgroups inside the user defined group
    """
    # Parenthesis are needed - keep them
    with h5py.File(file, 'r') as hdf:
        if group_name == 'base':
            return (list(hdf.items()))
        else:
            g1=hdf.get(group_name)
            return (list(g1.items()))


def h5path_exists(file, loc):
    """See if the group the user selected exists

    Parameters
    ==========
    file (str)
        the path to the hdf5 file
    loc (str)
        the location to the group the user wishes to check the status of

    Returns
    =======
    a bool (True or False) on whether or not the group exists
    """
    with h5py.File(file, 'r') as hdf:
        try:
            value = hdf.get(loc)
            if value == None:
                return False
            else:
                return True
        except:
            return False


def h5set_attr(file, loc, attribute_name, attribute_val):
    """Set and attribute for a User selected group

    Parameters
    ==========
    file (str)
        the path to the hdf5 file
    loc (str)
        the group location in the hdf5 file
    attribute_name (str)
        the name the user wants to set the attribute value of
    attribute_val (str or int)
        the value of the attribute

    Returns
    =======
    Nothing
    """
    with h5py.File(file, 'a') as hdf:
        data = hdf.get(loc)
        data.attrs[attribute_name] = attribute_val


def h5read_attr(file, loc, attribute_name):
    """Read an attribute from a user selected group and attribute name

    Parameters
    ==========
    file (str)
        the path to the hdf5 file
    loc (str)
        the location to the group inside the hdf5 file
    attribute_name (str)
        the name of the attribute

    Returns
    =======
    Attribute value
    """
    with h5py.File(file, 'a') as hdf:
        data = hdf.get(loc)
        return data.attrs[attribute_name]


def h5get_image_destination(self, pixel):
    """Determine where all the .tif images are for all the scan numbers disregarding the nan values

    Parameters
    ==========
    self (SXDMFramset)
        the sxdmframset

    pixel (str array)
        the image number from each scan that corresponds to a certain pixel

    Returns
    =======
    All of the diffraction FULL image locations for each scan in a 3D array - excluding the np.nan's
    """
    scan_numbers = self.scan_numbers
    image_loc = 'images/'
    pixels_minus_nan = []
    for i, scan in enumerate(scan_numbers):
        if np.isnan(pixel[i]) == False:
            pixels_minus_nan.append(image_loc + scan + '/' + str(pixel[i]).zfill(6))

    return pixels_minus_nan

def h5get_image_destination_v2(self, pixel):
    """Determine where all the .tif images are for all the scan numbers disregarding the nan values

    Parameters
    ==========
    self (SXDMFramset)
        the sxdmframset

    pixel (str array)
        the image number from each scan that corresponds to a certain pixel

    Returns
    =======
    All of the diffraction FULL image locations for each scan in a 3D array - excluding the np.nan's
    """
    scan_numbers = self.scan_numbers
    image_loc = 'images/'
    pixels_minus_nan = []
    for i, scan in enumerate(scan_numbers):
        if np.isnan(pixel[i]) == False:
            #pixels_minus_nan.append(image_loc + scan + '/' + str(pixel[i]).zfill(6))
            pixels_minus_nan.append((scan, str(pixel[i]).zfill(6)))

    return pixels_minus_nan

def open_h5(file):
    """Opening an hdf5 file

    Parameters
    ===========
    file (str)
        the path to the hdf5 file

    Returns
    ========
    The opened hdf5 file
    """
    hdf = h5py.File(file, 'r')
    return hdf

def close_h5(hdf):
    """Closing and opened hdf5 file

    Parameters
    ===========
    file (str)
        the path to the hdf5 file

    Returns
    ========
    Closes an opened hdf5 file
    """
    hdf.close()