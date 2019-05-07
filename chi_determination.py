#open up the chi sweep detector spectrum
#allow the user to change the vmin and vmax of the images

#Allow the user to click on two different images and make them show up larger on the right hand side

#Allow the user to select the middle of the ones on the side
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
from functools import partial
import warnings

from h5 import h5grab_data
from viewer import sum_error

class Chi_FiguresClass():
    pass


def return_chi_images_loc(file,
                          chi_figures,
                          detector_channel_loc = 'detector_channels/detector_scan/Main_Scan',
                          zfill_num = 4,
                          ):
    try:
        scan = h5grab_data(file, detector_channel_loc)
        scan_str = str(scan).zfill(zfill_num)
        im_loc = h5grab_data(file, 'images/{}'.format(scan_str))
        images_loc = ['images/{}/{}'.format(scan_str,
                                            loc) for loc in im_loc]
        chi_figures.images_location = images_loc
    except:
        warnings.warn('You Have Failed To Load In The Correct Detector Channel. '
                      'Correct The detector_channel_loc or Import Correct Data')
        chi_figures.images_location = None

def return_chi_images(file, chi_figures):
    images_loc = chi_figures.images_location
    image_array = []
    if images_loc != None:
        for image in images_loc:
            image_array.append(h5grab_data(file,image))
    elif images_loc == None:
        image_array = [sum_error(),sum_error()]
    chi_figures.images = image_array

def first_chi_figure_setup(self):
    chi_figures = Chi_FiguresClass()
    return_chi_images_loc(self.file, chi_figures)
    return_chi_images(self.file, chi_figures)
    ims = chi_figures.images
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
    vmin_spot_tb, vmax_spot_tb = minmax_tb_setup(vmin_spot_ax, vmax_spot_ax)

    chi_figures.first_fig = fig
    chi_figures.first_axs = axs
    chi_figures.vmin_spot_tb = vmin_spot_tb
    chi_figures.vmax_spot_tb = vmax_spot_tb
    return chi_figures

def display_first_images(chi_figures):
    axs = chi_figures.first_axs
    ims = chi_figures.images
    vmin = int(chi_figures.vmin_spot_tb.text)
    vmax = int(chi_figures.vmax_spot_tb.text)
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

def second_chi_figure_setup(chi_figures):
    fig, axs = plt.subplots(1, 2, figsize=(10, 10), facecolor='w',
                            edgecolor='k')
    fig.subplots_adjust(hspace=.55, wspace=.11)
    axs = axs.ravel()
    sides = ['left', 'right', 'top', 'bottom']
    for side in sides:
        axs[0].spines[side].set_color('red')
        axs[1].spines[side].set_color('green')

    small_idx_ax = plt.axes([0.15, 0.90, 0.1, 0.05])
    small_idx_ax.set_title('Index 1')
    small_idx_ax.set_xticks([])
    small_idx_ax.set_yticks([])
    large_idx_ax = plt.axes([0.3, 0.90, 0.1, 0.05])
    large_idx_ax.set_title('Index 2')
    large_idx_ax.set_xticks([])
    large_idx_ax.set_yticks([])
    small_idx_tb, large_idx_tb = idx_tb_setup(small_idx_ax, large_idx_ax)

    pos1_ax = plt.axes([0.65, 0.90, 0.1, 0.05])
    pos1_ax.set_title('Position 1')
    pos1_ax.set_xticks([])
    pos1_ax.set_yticks([])
    pos2_ax = plt.axes([0.8, 0.90, 0.1, 0.05])
    pos2_ax.set_title('Position 2')
    pos2_ax.set_xticks([])
    pos2_ax.set_yticks([])
    pos1_tb, pos2_tb = pos_tb_setup(pos1_ax, pos2_ax)

    chi_figures.second_fig = fig
    chi_figures.second_axs = axs
    chi_figures.small_idx_tb = small_idx_tb
    chi_figures.large_idx_tb = large_idx_tb
    chi_figures.pos1_tb = pos1_tb
    chi_figures.pos2_tb = pos2_tb

def display_second_images(chi_figures):
    axs = chi_figures.second_axs
    ims = chi_figures.images
    small_idx_tb = chi_figures.small_idx_tb
    large_idx_tb = chi_figures.large_idx_tb
    pos1 = int(chi_figures.pos1_tb.text)
    pos2 = int(chi_figures.pos2_tb.text)
    vmin = int(chi_figures.vmin_spot_tb.text)
    vmax = int(chi_figures.vmax_spot_tb.text)
    axs[0].cla()
    axs[1].cla()
    axs[0].imshow(ims[int(small_idx_tb.text)], vmin = vmin, vmax = vmax)
    axs[0].axvline(x = pos1)
    axs[1].imshow(ims[int(large_idx_tb.text)], vmin = vmin, vmax = vmax)
    axs[1].axvline(x = pos2)
    chi_figures.pos1 = pos1
    chi_figures.pos2 = pos2

def vs_change(event,chi_figures):
    axs = chi_figures.first_axs
    ims = chi_figures.images
    vmin_spot_tb = chi_figures.vmin_spot_tb
    vmax_spot_tb = chi_figures.vmax_spot_tb
    display_images(axs, ims, int(vmin_spot_tb.text), int(vmax_spot_tb.text))

def second_change(event, chi_figures):
    display_second_images(chi_figures)

def chi_function(self):
    chi_figures = first_chi_figure_setup(self)
    display_first_images(chi_figures)
    second_chi_figure_setup(chi_figures)
    display_second_images(chi_figures)

    p_display_images = partial(vs_change,chi_figures = chi_figures)
    p_display_second_images = partial(second_change, chi_figures = chi_figures)

    chi_figures.vmin_spot_tb.on_submit(p_display_images)
    chi_figures.vmax_spot_tb.on_submit(p_display_images)
    chi_figures.small_idx_tb.on_submit(p_display_second_images)
    chi_figures.large_idx_tb.on_submit(p_display_second_images)
    chi_figures.pos1_tb.on_submit(p_display_second_images)
    chi_figures.pos2_tb.on_submit(p_display_second_images)

def minmax_tb_setup(vmin_spot_ax, vmax_spot_ax):
    vmin_spot_tb = TextBox(vmin_spot_ax, 'vmin', initial='0')
    vmax_spot_tb = TextBox(vmax_spot_ax, 'vmax', initial='2')
    plt.draw()
    return vmin_spot_tb, vmax_spot_tb

def idx_tb_setup(vmin_spot_ax, vmax_spot_ax):
    vmin_spot_tb = TextBox(vmin_spot_ax, 'idx_1', initial='0')
    vmax_spot_tb = TextBox(vmax_spot_ax, 'idx_2', initial='1')
    plt.draw()
    return vmin_spot_tb, vmax_spot_tb

def pos_tb_setup(pos1_ax, pos2_ax):
    pos1_ax_tb = TextBox(pos1_ax, 'pos_1', initial='0')
    pos2_ax_tb = TextBox(pos2_ax, 'pos_2', initial='0')
    plt.draw()
    return pos1_ax_tb, pos2_ax_tb







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