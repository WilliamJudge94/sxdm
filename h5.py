import numpy as np
import imageio
import os
from tqdm import tqdm_notebook as tqdm
import matplotlib.pyplot as plt
import warnings

import h5py

def h5create_file(loc):
    hf = h5py.File('{}/data.h5'.format(loc), 'w')
    hf.close()

def h5read(file,data_loc):
    """Reads .h5 files

    :param file:
    :param data_loc:
    :return:
    """
    """
    Parameters
    ==========
    
    file: str 
    a string of the file you are working on
    
    data_loc: str
    
    """
    with h5py.File(file,'r') as hdf:
        g1 = hdf.get(data_loc)
        g1_data = list(g1)
    return g1_data

def h5list_group(file,group='base'):
    """Displays all group members for a user defined group

    :param file:
    :param group:
    :return:
    """
    with h5py.File(file,'r') as hdf:
        if group == 'base':
            base_items = list(hdf.items())
            base_items = np.array(base_items)
        else:
            base_items = hdf.get(group)
            base_items = list(base_items)
    return base_items

def h5grab_data(file,data_loc):
    """Returns the data stored in the user defined group

    :param file:
    :param data_loc:
    :return:
    """
    with h5py.File(file,'r') as hdf:
        data = hdf.get(data_loc)
        data = np.array(data)
    return data
    
def h5create_group(file,group):
    """Creates a group based on the Users group input

    :param file:
    :param group:
    :return:
    """
    with h5py.File(file,'a') as hdf:
        hdf.create_group(group)

def h5create_dataset(file,ds_path,ds_data):
    """Creates a dataset in the user defined group with data equal to the user defined data

    :param file:
    :param ds_path:
    :param ds_data:
    :return:
    """
    with h5py.File(file,'a') as hdf:
        #g1 = hdf.create_group(group)
        hdf.create_dataset(ds_path, data = ds_data)
    
def h5create_subgroup(file,group,subgroup):
    """Allows user to create a subgroup - Kinda useless

    :param file:
    :param group:
    :param subgroup:
    :return:
    """
    with h5py.File(file,'a') as hdf:
        hdf.create_group(group+'/'+subgroup)

def h5del_group(file,group):
    """Deletes the user defined group. DOES NOT REDUCE FILE SIZE

    :param file:
    :param group:
    :return:
    """
    with h5py.File(file,'a') as hdf:
        del hdf[group]

def h5del_data(file,group):
    """Sets all data equal to zero for a given dataset.

    :param file:
    :param group:
    :return:
    """
    with h5py.File(file,"a") as hdf:
        init_data = hdf[group]
        init_data[...] = 0

def h5images_wra(file,scan,im_loc,im_name,delete = False, import_type = 'uint32'):
    """Used to import/delete .tif images into the .h5 file

    :param file:
    :param scan:
    :param im_loc:
    :param im_name:
    :param delete:
    :param import_type:
    :return:
    """
    for idx,image in enumerate(im_loc):
        if delete == False:
            im = imageio.imread(image).astype(import_type)
        write_path = '/images/'+scan+'/'+im_name[idx]
        try:
            h5create_dataset(file,write_path,im)
        except:
            if delete == False:
                h5replace_data(file,write_path,im)   
            elif delete == True:
                h5del_data(file,write_path)
                
def h5replace_data(file,group,data):
    """Replaces all data in a dataset.

    Helps with space savings since deleting groups does not decrease the file size. Easier to replace data

    :param file:
    :param group:
    :param data:
    :return:
    """
    with h5py.File(file,"a") as hdf:
        init_data = hdf[group]
        init_data[...] = data
            
def h5group_list(file,group_name = 'base'):
    """Displays all group members for a user defined group

    :param file:
    :param group:
    :return:
    """
    with h5py.File(file,'r') as hdf:
        if group_name == 'base':
            return (list(hdf.items()))
        else:
            g1=hdf.get(group_name)
            return (list(g1.items()))


def h5path_exists(file, loc):
    """See if the group the user selected exsists

    :param file:
    :param loc:
    :return:
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

    :param file:
    :param loc:
    :param attribute_name:
    :param attribute_val:
    :return:
    """
    with h5py.File(file, 'a') as hdf:
        data = hdf.get(loc)
        data.attrs[attribute_name] = attribute_val

def h5read_attr(file, loc, attribute_name):
    """Read an attribute from a user selected group and attribute name

    :param file:
    :param loc:
    :param attribute_name:
    :return:
    """
    with h5py.File(file, 'a') as hdf:
        data = hdf.get(loc)
        return data.attrs[attribute_name]

def h5get_image_destination(self, pixel):
    """Determine where all the .tif images are for all the scan numbers

    :param self:
    :param pixel:
    :return:
    """
    scan_numbers = self.scan_numbers
    image_loc = 'images/'
    pixels_minus_nan = []
    for i, scan in enumerate(scan_numbers):
        if np.isnan(pixel[i]) == False:
            pixels_minus_nan.append(image_loc + scan + '/' + str(pixel[i]).zfill(6))

    return pixels_minus_nan
