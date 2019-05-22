import matplotlib.pyplot as plt
import warnings

from h5 import h5path_exists, h5read_attr, h5grab_data
from mis import array2dic, figure_size_finder
from clicks import *
from det_chan import return_det
from preprocess import init_dxdy

def alignment_function(self):
    """Allows the user to align the scans based on Fluorescence or Region Of Interest.

    Sets alignment variables and stores them in designated .h5 file. Easier to reload alignment data
    or redo alignment data

    Parameters
    ----------
    self: (SXDMFrameset)

    Returns
    -------
    Nothing
    """
    # Check to see if /dxdy group exsists if not make it and set attributes
    if h5path_exists(self.file, self.dataset_name + '/dxdy') == True:
        warnings.warn('Previous Data Found')
        redo_alignment = input('Previous Data Found. Redo Alignment? y/n ')

        # Determining if User wants to reload or redo alignment
        if redo_alignment == 'y':
            start_alignment = 'y'
            self.alignment_group = h5read_attr(self.file, self.dataset_name + '/dxdy', 'alignment_group')
            self.alignment_subgroup = h5read_attr(self.file, self.dataset_name + '/dxdy', 'alignment_subgroup')
        else:
            start_alignment = 'n'
            redo_alignment = 'n'

    else:
        start_alignment = 'y'
        redo_alignment = 'n'

    if start_alignment == 'y':
        if start_alignment == 'y' and redo_alignment == 'n':
            init_dxdy(self)
        else:
            print('Previous Alignment Done On -  ' + self.alignment_group + ' - ' + self.alignment_subgroup)
            # Grabbing old alignment and setting alignment circles
            retrieve_old_data = array2dic(h5grab_data(self.file, self.dataset_name + '/dxdy'))
            warnings.warn('Refreshing Old Aligment Data')
        self.clicks = {}
        self.correction_store = {}
        plt.close('all')
        cont = True
        # Ask which images the user wants to align to
        while cont == True:
            user_val = input('Would You Like To Align On fluor Or roi? ')
            if user_val == 'fluor' or user_val == 'roi':
                cont = False
            else:
                warnings.warn('Please Type In An Acceptable Values: ')
        det_return = return_det(self.file, self.scan_numbers, group=user_val)
        images = det_return[0]
        self.alignment_subgroup = det_return[1]
        self.alignment_group = user_val
        starting = figure_size_finder(images)

        plt.close('all')
        #Setting up initial figure for alignment
        fig, axs = plt.subplots(starting, starting,
                                figsize=(10, 10),
                                facecolor='w',
                                edgecolor='k')
        try:
            self.loc_axs = axs.ravel()
        except:
            warnings.warn('Ravel Function Not Called. Possible 1D Image Trying To Load')
            self.loc_axs = [axs]
        axs_store = []

        saving = partial(save_alignment, self=self)
        initiate = partial(onclick_1, self=self)
        click1 = partial(fig1_click, self=self, fig=fig, images=images)

        # Display circles for alignment
        for i, image in enumerate(images):
            self.loc_axs[i].imshow(image)
            axs_store.append(self.loc_axs[i].get_position())
        if redo_alignment == 'y':
            for num, old_ax in enumerate(retrieve_old_data):
                old_clicks = retrieve_old_data[old_ax]
                circ = Circle((old_clicks[0], old_clicks[1]), 0.3, color='r')
                self.loc_axs[old_ax].add_patch(circ)

        plt.suptitle('Please Click On Any Of The Images Below')
        plt.show()

        # Based on the Users clicks display different information
        fig.canvas.mpl_connect('button_press_event', initiate)
        fig.canvas.mpl_connect('button_press_event', click1)
        fig.canvas.mpl_connect('button_press_event', saving)

    elif redo_alignment == 'n':
        print('Staying With Current Alignment Parameters')
