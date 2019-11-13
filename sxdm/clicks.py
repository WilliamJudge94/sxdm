import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from functools import partial
import numpy as np
import time

from h5 import h5create_dataset, h5set_attr, h5replace_data, h5del_group, h5path_exists
from mis import dic2array


def onclick_1(event, self):
    """Deal with click events for first figure. Only allows for 30 figures

    Once you click on figure one open up a second figure with the figure you just clicked on, but larger

    Parameters
    ==========
    event: (matplotlib event)
        not 1100% sure. Needed to be the first param in a matplotlib event

    self: (SXDMFrameset)
        An SXDMFrameset which allows the function to store click values

    Returns
    =======
    Nothing

    """

    button = ['left', 'middle', 'right']
    toolbar = plt.get_current_fig_manager().toolbar
    if toolbar.mode != '':
        print("You clicked on something, but toolbar is in mode {:s}.".format(toolbar.mode))

    # Keep making up to 30 figures in a single plot
    else:
        try:
            old_loc = self.clicks['loc']
        except:
            pass
        self.clicks['loc'] = (int(event.xdata), int(event.ydata))
        total = 30

        # Making plots and getting axis locations
        try:
            for i in range(total):
                if event.inaxes == self.loc_axs[i]:
                    if i <= self.max_images:
                        self.clicks['ax'] = i
                    elif i > self.max_images:
                        self.clicks['ax'] = self.max_images
                        self.clicks['loc'] = old_loc
        except:
            pass


def onclick_2(event, self):
    """Determine the pixel location the user has clicked on.

    From the second figure that popped up, once you click on it, determine the location of that click

    Parameters
    ==========
    event (matplotlib event)
        Unsure. Needed to be the first variable in a matplotlib event click

    self (SXDMFrameset)
        An SXDMFrameset that allows the clicks to be saved
    """

    # Storing the click data
    toolbar = plt.get_current_fig_manager().toolbar
    if toolbar.mode != '':
        print("You clicked on something, but toolbar is in mode {:s}.".format(toolbar.mode))
    else:
        self.clicks['loc'] = (int(np.floor(event.xdata)), int(np.floor(event.ydata)))


def fig1_click(event, self, fig, images):
    """Deal with event clicks in the first figure and redraw plots

    Parameters
    ==========
    event (matplotlib event)
        matplotlib event
    self (SXDMFrameset)
        the sxdmframeset
    fig (matplotlib figure)
        the figure to be clicked on
    images (nd.array)
        the images to display

    Returns
    =======
    Nothing - deals with the clicks on the first image
    """

    # Set up new figure
    fig2, axs2 = plt.subplots(1, 1, figsize=(10, 10), facecolor='w', edgecolor='k')
    try:
        plt.imshow(images[self.clicks['ax']])
        plt.suptitle('Select A Spot To Center On')
    except:
        plt.close()

    click2 = partial(onclick_2, self=self)

    fig2.canvas.mpl_connect('button_press_event', click2)

    plt.waitforbuttonpress(0)

    # Grabbing dxdy store movements and place their circle locations
    self.dxdy_store[self.clicks['ax']] = self.clicks['loc']

    circ = Circle((self.clicks['loc'][0], self.clicks['loc'][1]), 0.3, color='r')

    # Try to remove circles if they exist
    try:
        [p.remove() for p in reversed(self.loc_axs[self.clicks['ax']].patches)]
    except:
        pass

    # Plot images
    self.loc_axs[self.clicks['ax']].add_patch(circ)
    plt.close(fig2)
    fig_count = len(self.scan_numbers)
    spot_count = len(self.dxdy_store)
    if spot_count >= fig_count:
        fig.suptitle('Once Complete You May Close This Window')
    fig.canvas.draw()


def save_alignment(event, self):
    """Allow the alignment click information to be saved to self.file

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframeset object

    Returns
    =======
    Nothing. It just stores /dxdy to the self.file as well
    as adding alingment_group and alignment_subgroup attributes
    """

    # Try saving the data
    if h5path_exists(file=self.file,
                     loc=self.dataset_name + '/dxdy') == False:
        h5create_dataset(file=self.file,
                         ds_path=self.dataset_name + '/dxdy',
                         ds_data=dic2array(self.dxdy_store))
        h5set_attr(file=self.file,
                   loc=self.dataset_name + '/dxdy',
                   attribute_name='alignment_group',
                   attribute_val=self.alignment_group)

        h5set_attr(file=self.file,
                   loc=self.dataset_name + '/dxdy',
                   attribute_name='alignment_subgroup',
                   attribute_val=self.alignment_subgroup)
    else:

        # Try replacing the data
        try:
            h5replace_data(file=self.file,
                           group=self.dataset_name + '/dxdy',
                           data=dic2array(self.dxdy_store))

            h5set_attr(file=self.file,
                       loc=self.dataset_name + '/dxdy',
                       attribute_name='alignment_group',
                       attribute_val=self.alignment_group)

            h5set_attr(file=self.file,
                       loc=self.dataset_name + '/dxdy',
                       attribute_name='alignment_subgroup',
                       attribute_val=self.alignment_subgroup)

        # Delete group and create a new dataset
        except Exception as ex:
            print('clicks.py/save_alignment', ex)
            print('Deleted Group')
            h5del_group(file=self.file,
                        group=self.dataset_name + '/dxdy')

            h5create_dataset(file=self.file,
                             ds_path=self.dataset_name + '/dxdy',
                             ds_data=dic2array(self.dxdy_store))

            h5set_attr(file=self.file,
                       loc=self.dataset_name + '/dxdy',
                       attribute_name='alignment_group',
                       attribute_val=self.alignment_group)

            h5set_attr(file=self.file,
                       loc=self.dataset_name + '/dxdy',
                       attribute_name='alignment_subgroup',
                       attribute_val=self.alignment_subgroup)
            print('Deleted Group 2')


def check_mouse_ax(event, self):
    """Grabs the mouse axes position

    Parameters
    ==========
    event (matplotlib event)
        the matpotlib event
    self (SXDMFrameset)
        the sxdmframeset

    Returns
    =======
    Nothing - just checks which axis the mouse is in
    """

    if event.inaxes == self.fluor_ax:
        self.viewer_currentax = self.fluor_ax
    elif event.inaxes == self.roi_ax:
        self.viewer_currentax = self.roi_ax


def fig_leave(event, self):
    """If the user leaves an axis set the self.viewer_currentax to None
    Parameters
    ==========
    event (matplotlib event)
        the matplotlib event
    self (SXDMFrameset)
        the sxdmframeset

    Returns
    =======
    Nothing
    """
    self.viewer_currentax = None
