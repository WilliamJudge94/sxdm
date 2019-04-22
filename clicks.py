import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from functools import partial
import numpy as np

from h5 import h5create_dataset, h5set_attr, h5replace_data, h5del_group, h5path_exists
from mis import dic2array

def onclick_1(event, self):
    """Deal with click events for first figure. Only allows for 30 figures

    Parameters
    ==========
    event: (?)
        not 1100% sure. Needed to be the first param in a matplotlib event

    self: (SXDMFrameset)
        An SXDMFrameset which allows the function to store click values

    """
    button = ['left', 'middle', 'right']
    toolbar = plt.get_current_fig_manager().toolbar
    if toolbar.mode != '':
        print("You clicked on something, but toolbar is in mode {:s}.".format(toolbar.mode))
    else:
        self.clicks['loc'] = (int(event.xdata), int(event.ydata))
        total = 30
        try:
            for i in range(total):
                if event.inaxes == self.loc_axs[i]:
                    self.clicks['ax'] = i
        except:
            pass

def onclick_2(event, self):
    """Determine the pixel location the user has clicked on

    Parameters
    ==========

    event (?)
        Unsure. Needed to be the first variable in a matplotlib event click

    self (SXDMFrameset)
        An SXDMFrameset that allows the clicks to be saved
    """
    button = ['left', 'middle', 'right']
    toolbar = plt.get_current_fig_manager().toolbar
    if toolbar.mode != '':
        print("You clicked on something, but toolbar is in mode {:s}.".format(toolbar.mode))
    else:
        self.clicks['loc'] = (int(np.floor(event.xdata)), int(np.floor(event.ydata)))


def fig1_click(event, self, fig, images):
    """Deal with event clicks in the first figure and redraw plots

    Parameters
    ==========


    :param event:
    :param self:
    :param fig:
    :param images:
    :return:

    Returns
    =======
    Nothing
    """
    fig2, axs2 = plt.subplots(1, 1, figsize=(10, 10), facecolor='w', edgecolor='k')
    plt.imshow(images[self.clicks['ax']])
    plt.suptitle('Select A Spot To Center On')

    click2 = partial(onclick_2, self=self)

    fig2.canvas.mpl_connect('button_press_event', click2)

    plt.waitforbuttonpress(0)

    self.dxdy_store[self.clicks['ax']] = self.clicks['loc']

    circ = Circle((self.clicks['loc'][0], self.clicks['loc'][1]), 0.3, color='r')

    try:
        [p.remove() for p in reversed(self.loc_axs[self.clicks['ax']].patches)]
    except:
        pass

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

    Returns
    =======

    Nothing. It just stores /dxdy to the self.file as well
    as adding alingment_group and alignment_subgroup attributes


    """

    if h5path_exists(self.file, self.dataset_name + '/dxdy') == False:
        h5create_dataset(self.file, self.dataset_name + '/dxdy', dic2array(self.dxdy_store))
        h5set_attr(self.file, self.dataset_name + '/dxdy', 'alignment_group', self.alignment_group)
        h5set_attr(self.file, self.dataset_name + '/dxdy', 'alignment_subgroup', self.alignment_subgroup)
    else:

        try:
            h5replace_data(self.file, self.dataset_name + '/dxdy', dic2array(self.dxdy_store))
            h5set_attr(self.file, self.dataset_name + '/dxdy', 'alignment_group', self.alignment_group)
            h5set_attr(self.file, self.dataset_name + '/dxdy', 'alignment_subgroup', self.alignment_subgroup)
        except:
            print('Deleted Group')
            h5del_group(self.file, self.dataset_name + '/dxdy')
            h5create_dataset(self.file, self.dataset_name + '/dxdy', dic2array(self.dxdy_store))
            h5set_attr(self.file, self.dataset_name + '/dxdy', 'alignment_group', self.alignment_group)
            h5set_attr(self.file, self.dataset_name + '/dxdy', 'alignment_subgroup', self.alignment_subgroup)
            print('Deleted Group 2')
