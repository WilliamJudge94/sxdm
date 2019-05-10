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
import math

from h5 import h5grab_data, h5path_exists, h5read_attr
from det_chan import return_det
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
        mda_loc = h5grab_data(file, 'mda/{}'.format(scan_str))
        im_check = h5path_exists(file,'images/{}'.format(scan_str))
        mda_check = h5path_exists(file, 'mda/{}'.format(scan_str))
        images_loc = ['images/{}/{}'.format(scan_str,
                                            loc) for loc in im_loc]
        chi_figures.images_location = images_loc
        if chi_figures.user_rocking == 'spl':
            theta = return_det(file, [scan_str], group='sample_theta')
            chi_figures.scan_theta = theta[0]
        elif chi_figures.user_rocking == 'det':
            #chi_figures.scan_theta = chi_figures.user_det_theta
            det_find = 'D'+str(h5grab_data(file,'detector_channels/mis/2Theta')).zfill(2)
            theta = h5grab_data(file, '/mda/{}/{}'.format(scan_str, det_find))
            sh = np.shape(theta)
            theta = np.reshape(theta, (1, sh[0]*sh[1]))[0]
            chi_figures.scan_theta = theta

    except:
        warnings.warn('You Have Failed To Load In The Correct Detector Channel. '
                      'Correct The detector_channel_loc or Import Correct Data')
        chi_figures.images_location = None
    if im_check == False or mda_check == False:
        warnings.warn('You Have Failed To Load In The Correct Detector Channel. '
                      'Correct The detector_channel_loc or Import Correct Data '
                      'im_check: {} - mda_check: {}'.format(im_check, mda_check))
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
    chi_figures.user_rocking = self.user_rocking
    chi_figures.user_det_theta = self.scan_theta
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
    chi_figures.image_dimensions = np.shape(ims[0])
    for i,ax in enumerate(axs):
        try:
            ax.cla()
            ax.imshow(ims[i], vmin = vmin, vmax = vmax)
            ax.set_title('IDX {}'.format(i))
            ax.set_xticks([])
            ax.set_yticks([])
        except:
            ax.set_xticks([])
            ax.set_yticks([])
        plt.draw()

def second_chi_figure_setup(chi_figures):
    fig, axs = plt.subplots(1, 2, figsize=(10, 6), facecolor='w',
                            edgecolor='k')
    fig.subplots_adjust(hspace=.55, wspace=.11)
    axs = axs.ravel()
    sides = ['left', 'right', 'top', 'bottom']
    for side in sides:
        axs[0].spines[side].set_color('red')
        axs[1].spines[side].set_color('magenta')

    small_idx_ax = plt.axes([0.15, 0.90, 0.1, 0.05])
    small_idx_ax.set_title('First IDX')
    small_idx_ax.set_xticks([])
    small_idx_ax.set_yticks([])
    large_idx_ax = plt.axes([0.3, 0.90, 0.1, 0.05])
    large_idx_ax.set_title('Second IDX')
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


    close_button_ax = plt.axes([0.15, 0.05, 0.1, 0.05])
    closebtn_start(chi_figures, close_button_ax)

    chi_figures.second_fig = fig
    chi_figures.second_axs = axs
    chi_figures.small_idx_tb = small_idx_tb
    chi_figures.large_idx_tb = large_idx_tb
    chi_figures.pos1_tb = pos1_tb
    chi_figures.pos2_tb = pos2_tb

def closebtn_start(chi_figures, btn_ax):
    closebtn = Button(ax = btn_ax,
                           label = 'Finish',
                           color = 'teal',
                           hovercolor = 'tomato')
    chi_figures.closebtn = closebtn

def display_second_images(chi_figures):
    axs = chi_figures.second_axs
    ims = chi_figures.images
    small_idx_tb = chi_figures.small_idx_tb
    large_idx_tb = chi_figures.large_idx_tb
    pos1 = int(chi_figures.pos1_tb.text)
    pos2 = int(chi_figures.pos2_tb.text)
    vmin = int(chi_figures.vmin_spot_tb.text)
    vmax = int(chi_figures.vmax_spot_tb.text)
    idx1 = int(small_idx_tb.text)
    idx2 = int(large_idx_tb.text)
    if chi_figures.user_rocking == 'spl':
        angle1 = np.round(chi_figures.scan_theta[0][idx1][0], 5)
        angle2 = np.round(chi_figures.scan_theta[0][idx2][0], 5)
    elif chi_figures.user_rocking == 'det':
        angle1 = float(np.round(chi_figures.scan_theta[idx1], 5))
        angle2 = float(np.round(chi_figures.scan_theta[idx2], 5))
    chi_figures.angle1 = angle1
    chi_figures.angle2 = angle2
    axs[0].cla()
    axs[1].cla()
    axs[0].imshow(ims[idx1], vmin = vmin, vmax = vmax)
    axs[0].axvline(x = pos1)
    axs[0].set_title('IDX {}  Angle {}'.format(idx1, angle1))
    axs[1].imshow(ims[idx2], vmin = vmin, vmax = vmax)
    axs[1].axvline(x = pos2)
    axs[1].set_title('IDX {}  Angle {}'.format(idx2, angle2))
    chi_figures.pos1 = pos1
    chi_figures.pos2 = pos2

def closebtn_press(event, self, chi_figures):

    self.chi_angle_difference = abs(np.subtract(chi_figures.angle1, chi_figures.angle2))
    self.chi_position_difference = abs(np.subtract(chi_figures.pos1, chi_figures.pos2))
    self.chi_image_dimensions = chi_figures.image_dimensions

    plt.close('all')
    chis(self)

def vs_change(event,chi_figures):
    axs = chi_figures.first_axs
    ims = chi_figures.images
    vmin_spot_tb = chi_figures.vmin_spot_tb
    vmax_spot_tb = chi_figures.vmax_spot_tb
    display_first_images(chi_figures)

def second_change(event, chi_figures):
    display_second_images(chi_figures)

def chi_function(self):
    chi_figures = first_chi_figure_setup(self)
    chi_figures.user_rocking = self.user_rocking
    chi_figures.user_det_theta = self.scan_theta
    display_first_images(chi_figures)
    second_chi_figure_setup(chi_figures)
    display_second_images(chi_figures)

    p_display_images = partial(vs_change,chi_figures = chi_figures)
    p_display_second_images = partial(second_change, chi_figures = chi_figures)
    p_closebtn = partial(closebtn_press, self = self, chi_figures = chi_figures)

    chi_figures.vmin_spot_tb.on_submit(p_display_images)
    chi_figures.vmin_spot_tb.on_submit(p_display_second_images)
    chi_figures.vmax_spot_tb.on_submit(p_display_images)
    chi_figures.vmax_spot_tb.on_submit(p_display_second_images)

    chi_figures.small_idx_tb.on_submit(p_display_second_images)
    chi_figures.large_idx_tb.on_submit(p_display_second_images)
    chi_figures.pos1_tb.on_submit(p_display_second_images)
    chi_figures.pos2_tb.on_submit(p_display_second_images)
    chi_figures.closebtn.on_clicked(p_closebtn)

def minmax_tb_setup(vmin_spot_ax, vmax_spot_ax):
    vmin_spot_tb = TextBox(vmin_spot_ax, 'vmin', initial='0')
    vmax_spot_tb = TextBox(vmax_spot_ax, 'vmax', initial='2')
    plt.draw()
    return vmin_spot_tb, vmax_spot_tb

def idx_tb_setup(vmin_spot_ax, vmax_spot_ax):
    vmin_spot_tb = TextBox(vmin_spot_ax, '', initial='0')
    vmax_spot_tb = TextBox(vmax_spot_ax, '', initial='1')
    plt.draw()
    return vmin_spot_tb, vmax_spot_tb

def pos_tb_setup(pos1_ax, pos2_ax):
    pos1_ax_tb = TextBox(pos1_ax, '', initial='0')
    pos2_ax_tb = TextBox(pos2_ax, '', initial='0')
    plt.draw()
    return pos1_ax_tb, pos2_ax_tb

def chis(self):
    pix_size_um = float(h5grab_data(self.file, 'zone_plate/detector_pixel_size'))
    self.pix_size_um = pix_size_um
    tot_angle_diff = self.chi_angle_difference
    dimensions = self.chi_image_dimensions
    pixel_diff = self.chi_position_difference
    angle_rads = math.radians(tot_angle_diff)
    length = (pixel_diff * pix_size_um)

    r = ((length)/math.tan(angle_rads))/1000
    self.r_mm = r

    Chi=math.degrees(math.atan((((((dimensions[0])/2)*pix_size_um)/1000))/r))
    self.chi = Chi
    broadening_in_pixles(self)

    print('Chi bound is: {} Degrees\nFocal Length is : {} mm\nNumberical Aperature is: {} mrads\n'
          'Radius of Broadening is: {} pixels'.format(self.chi, self.focal_length_mm, self.NA_mrads, self.broadening_in_pix))

def broadening_in_pixles(self):
    Kev = float(h5read_attr(file=self.file, loc=self.dataset_name, attribute_name='Kev'))
    D_um = float(h5grab_data(self.file, 'zone_plate/D_um'))
    d_rN_nm = float(h5grab_data(self.file, 'zone_plate/d_rN_nm'))
    r_mm = self.r_mm

    pix_size_um = self.pix_size_um

    D_nm = D_um * 1000
    r_um = r_mm * 1000

    half_zp_nm = D_nm/2

    plancks_constant=(6.62607004*10**-34)/(1.60217662*10**-19)
    speed_of_light=299792458
    hc=(plancks_constant)*(speed_of_light)*10**9
    wavelength_nm=hc/(Kev*1000)

    f_nm = (D_nm * d_rN_nm)/wavelength_nm
    fraction = half_zp_nm/f_nm
    len_in_pix = r_um/pix_size_um

    self.focal_length_mm = f_nm/1000000
    self.NA_mrads = fraction * 1000
    self.broadening_in_pix = (half_zp_nm/f_nm) * len_in_pix