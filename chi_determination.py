#open up the chi sweep detector spectrum
#allow the user to change the vmin and vmax of the images

#Allow the user to click on two different images and make them show up larger on the right hand side

#Allow the user to select the middle of the ones on the side
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
from functools import partial

from h5 import h5grab_data

def return_chi_images_loc(file, detector_channel_loc = 'detector_channels/detector_scan/Main_Scan', zfill_num = 4):
    scan = h5grab_data(file, detector_channel_loc)
    scan_str = str(scan).zfill(zfill_num)
    im_loc = h5grab_data(file, 'images/{}'.format(scan_str))
    images_loc = ['images/{}/{}'.format(scan_str,
                                        loc) for loc in im_loc]
    return images_loc

def return_chi_images(file, images_loc):
    image_array = []
    for image in images_loc:
        image_array.append(h5grab_data(file,image))
    return image_array


def chi_figure_setup(self):
    im_loc = return_chi_images_loc(self.file)
    ims = return_chi_images(self.file, im_loc)
    tot_ims = int(np.ceil(np.sqrt(len(ims))))
    fig, axs = plt.subplots(tot_ims, tot_ims, figsize=(10, 10), facecolor='w',
                            edgecolor='k')
    fig.subplots_adjust(hspace=.55, wspace=.11)
    axs = axs.ravel()

    vmin_spot_ax = plt.axes([0.15, 0.92, 0.1, 0.05])
    vmin_spot_ax.set_title('vmin')
    vmin_spot_ax.set_xticks([])
    vmin_spot_ax.set_yticks([])
    vmax_spot_ax = plt.axes([0.3, 0.92, 0.1, 0.05])
    vmax_spot_ax.set_title('vmax')
    vmax_spot_ax.set_xticks([])
    vmax_spot_ax.set_yticks([])
    vmin_spot_tb, vmax_spot_tb = tb2_setup(vmin_spot_ax, vmax_spot_ax)

    return fig, axs, ims, vmin_spot_tb, vmax_spot_tb


def second_chi_figure_setup():
    fig, axs = plt.subplots(1, 2, figsize=(10, 10), facecolor='w',
                            edgecolor='k')
    fig.subplots_adjust(hspace=.55, wspace=.11)
    axs = axs.ravel()
    sides = ['left', 'right', 'top', 'bottom']
    for side in sides:
        axs[0].spines[side].set_color('red')
        axs[1].spines[side].set_color('green')

    small_idx_ax = plt.axes([0.15, 0.92, 0.1, 0.05])
    small_idx_ax.set_title('Index 1')
    small_idx_ax.set_xticks([])
    small_idx_ax.set_yticks([])
    large_idx_ax = plt.axes([0.3, 0.92, 0.1, 0.05])
    large_idx_ax.set_title('Index 2')
    large_idx_ax.set_xticks([])
    large_idx_ax.set_yticks([])
    small_idx_tb, large_idx_tb = tb2_setup(small_idx_ax, large_idx_ax)

    return fig, axs, small_idx_tb, large_idx_tb

def display_second_images(axs, ims, small_idx_tb, large_idx_tb, pos1, pos2):
    axs[0].cla()
    axs[1].cla()
    axs[0].imshow(ims[int(small_idx_tb.text)])
    axs[0].axvline(x = pos1)
    axs[1].imshow(ims[int(large_idx_tb.text)])
    axs[1].axvline(x = pos2)


def display_images(axs,ims,vmin,vmax):
    for i,ax in enumerate(axs):
        try:
            ax.cla()
            ax.imshow(ims[i], vmin = vmin, vmax = vmax)
            ax.set_xticks([])
            ax.set_yticks([])
        except:
            ax.set_xticks([])
            ax.set_yticks([])
        plt.draw()

def vs_change(event,axs, ims, vmin_spot_tb, vmax_spot_tb):
    display_images(axs, ims, int(vmin_spot_tb.text), int(vmax_spot_tb.text))

def chi_function(self):
    fig, axs, ims, vmin_spot_tb, vmax_spot_tb = chi_figure_setup(self)
    display_images(axs, ims, int(vmin_spot_tb.text), int(vmax_spot_tb.text))
    p_display_images = partial(vs_change,axs = axs, ims = ims, vmin_spot_tb = vmin_spot_tb, vmax_spot_tb = vmax_spot_tb)
    vmin_spot_tb.on_submit(p_display_images)
    vmax_spot_tb.on_submit(p_display_images)

def tb2_setup(vmin_spot_ax, vmax_spot_ax):
    vmin_spot_tb = TextBox(vmin_spot_ax, 'vmin', initial='0')
    vmax_spot_tb = TextBox(vmax_spot_ax, 'vmax', initial='2')
    plt.draw()
    return vmin_spot_tb, vmax_spot_tb

def tb3_setup(vmin_spot_ax, vmax_spot_ax):
    vmin_spot_tb = TextBox(vmin_spot_ax, 'idx_1', initial='0')
    vmax_spot_tb = TextBox(vmax_spot_ax, 'idx_2', initial='2')
    plt.draw()
    return vmin_spot_tb, vmax_spot_tb

def chi_setp2(self):
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