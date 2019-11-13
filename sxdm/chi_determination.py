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
    """A class function that allows the code to store figure data.
    Makes it easier to transfer data between figures

    """
    pass


def return_chi_images_loc(file,
                          chi_figures,
                          detector_channel_loc='detector_channels/detector_scan/Main_Scan',
                          zfill_num=4,
                          ):
    """Grabs the image location for the detector sweep scan

    Parameters
    ==========
    file: (str)
        the .h5 file associated with the dataset

    chi_figures: (Chi_FigureClass)
        the Chi_FigureClass allowing transfer of data from figure to figure

    detector_channel_loc: (str)
        the h5 group location to the detector sweep scan used for chi bounds determination

    zfill_num: (int)
        the integer value for how many digits the scan number must have


    Returns
    =======
    Nothing - sets the chi_figures.scan_theta and chi_figures.images_location valuess
    """

    # Attempt to pull chi determination scan information
    try:
        # Grab the detector channel data
        scan = h5grab_data(file=file,
                           data_loc=detector_channel_loc)
        scan_str = str(scan).zfill(zfill_num)

        # Grab the scans in the images and mda group
        im_loc = h5grab_data(file=file,
                             data_loc='images/{}'.format(scan_str))
        mda_loc = h5grab_data(file=file,
                              data_loc='mda/{}'.format(scan_str))

        # See if the images or mda group exsists
        im_check = h5path_exists(file=file,
                                 loc='images/{}'.format(scan_str))
        mda_check = h5path_exists(file=file,
                                  loc='mda/{}'.format(scan_str))

        # Formatting the image locations
        images_loc = ['images/{}/{}'.format(scan_str,
                                            loc) for loc in im_loc]
        chi_figures.images_location = images_loc

        # Based on what the user rocked to get the chi scan this will pull different values
        if chi_figures.user_rocking == 'spl':
            theta = return_det(file=file,
                               scan_numbers=[scan_str],
                               group='sample_theta')
            chi_figures.scan_theta = theta[0]

        elif chi_figures.user_rocking == 'det':
            det_find = 'D'+str(h5grab_data(file=file,
                                           data_loc='detector_channels/mis/2Theta')).zfill(2)
            theta = h5grab_data(file=file,
                                data_loc='/mda/{}/{}'.format(scan_str, det_find))
            sh = np.shape(theta)
            theta = np.reshape(theta, (1, sh[0]*sh[1]))[0]
            chi_figures.scan_theta = theta

    # Throw error if the program cannot pull info
    except Exception as ex:
        print('chi_determination.py/return_chi_images_loc', ex)
        warnings.warn('You Have Failed To Load In The Correct Detector Channel. '
                      'Correct The detector_channel_loc or Import Correct Data')
        chi_figures.images_location = None

    # Throw error if the images or mda group does not exist
    if im_check == False or mda_check == False:
        warnings.warn('You Have Failed To Load In The Correct Detector Channel. '
                      'Correct The detector_channel_loc or Import Correct Data '
                      'im_check: {} - mda_check: {}'.format(im_check, mda_check))
        chi_figures.images_location = None


def return_chi_images(file, chi_figures):
    """Return the detector movement data

    Parameters
    ==========
    file (str):
        the file the user would like to find the detector images from
    chi_figures (Chi_FigureClass):
        the figure class. used to make it easier to move data around
    Returns
    =======
    Nothing - sets chi_fiures.images value
    """
    # Obtain the images for the figure
    images_loc = chi_figures.images_location
    image_array = []

    if images_loc != None:
        for image in images_loc:
            image_array.append(h5grab_data(file=file,
                                           data_loc=image))

    # If it errors then load psyduck
    elif images_loc == None:
        image_array = [sum_error(), sum_error()]

    chi_figures.images = image_array


def first_chi_figure_setup(self):
    """Setting up the chi figure GUI

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframeset object

    Returns
    =======
    The Chi_FigureClass object created by the function
    """
    # Initiate the figure
    chi_figures = Chi_FiguresClass()
    chi_figures.user_rocking = self.user_rocking
    chi_figures.user_det_theta = self.scan_theta
    return_chi_images_loc(file=self.file,
                          chi_figures=chi_figures)
    return_chi_images(file=self.file,
                      chi_figures=chi_figures)
    ims = chi_figures.images
    tot_ims = int(np.ceil(np.sqrt(len(ims))))

    # Create the figure
    fig, axs = plt.subplots(tot_ims, tot_ims, figsize=(10, 10), facecolor='w',
                            edgecolor='k')
    fig.subplots_adjust(hspace=.55, wspace=.11)
    axs = axs.ravel()

    # Initiate the axes for textboxes and input boxes
    vmin_spot_ax = plt.axes([0.15, 0.92, 0.1, 0.05])
    vmin_spot_ax.set_title('vmin')
    vmin_spot_ax.set_xticks([])
    vmin_spot_ax.set_yticks([])
    vmax_spot_ax = plt.axes([0.3, 0.92, 0.1, 0.05])
    vmax_spot_ax.set_title('vmax')
    vmax_spot_ax.set_xticks([])
    vmax_spot_ax.set_yticks([])
    vmin_spot_tb, vmax_spot_tb = minmax_tb_setup(vmin_spot_ax=vmin_spot_ax,
                                                 vmax_spot_ax=vmax_spot_ax)

    # Initiate the fig, axes, and other tb
    chi_figures.first_fig = fig
    chi_figures.first_axs = axs
    chi_figures.vmin_spot_tb = vmin_spot_tb
    chi_figures.vmax_spot_tb = vmax_spot_tb
    return chi_figures


def display_first_images(chi_figures):
    """From the chi figure class set up the first set of figures

    Returns
    =======
    Nothing
    """

    # Get all image data
    axs = chi_figures.first_axs
    ims = chi_figures.images
    vmin = int(chi_figures.vmin_spot_tb.text)
    vmax = int(chi_figures.vmax_spot_tb.text)
    chi_figures.image_dimensions = np.shape(ims[0])

    # Show all images in appropriate axis
    for i, ax in enumerate(axs):
        try:
            ax.cla()
            ax.imshow(ims[i], vmin=vmin, vmax=vmax)
            ax.set_title('IDX {}'.format(i))
            ax.set_xticks([])
            ax.set_yticks([])
        except:
            ax.set_xticks([])
            ax.set_yticks([])
        plt.draw()


def second_chi_figure_setup(chi_figures):
    """Setting up the second figure

    Parameters
    ==========
    chi_figures (Chi_FigureClass)
        the chi_figuresclass

    Returns
    =======
    Nothing
    """

    # Initiate figure
    fig, axs = plt.subplots(1, 2, figsize=(10, 6), facecolor='w',
                            edgecolor='k')
    fig.subplots_adjust(hspace=.55, wspace=.11)
    axs = axs.ravel()
    sides = ['left', 'right', 'top', 'bottom']
    for side in sides:
        axs[0].spines[side].set_color('red')
        axs[1].spines[side].set_color('magenta')

    # Initiate all axes
    small_idx_ax = plt.axes([0.15, 0.90, 0.1, 0.05])
    small_idx_ax.set_title('First IDX')
    small_idx_ax.set_xticks([])
    small_idx_ax.set_yticks([])
    large_idx_ax = plt.axes([0.3, 0.90, 0.1, 0.05])
    large_idx_ax.set_title('Second IDX')
    large_idx_ax.set_xticks([])
    large_idx_ax.set_yticks([])
    small_idx_tb, large_idx_tb = idx_tb_setup(vmin_spot_ax=small_idx_ax,
                                              vmax_spot_ax=large_idx_ax)

    # Initiate textboxes
    pos1_ax = plt.axes([0.65, 0.90, 0.1, 0.05])
    pos1_ax.set_title('Position 1')
    pos1_ax.set_xticks([])
    pos1_ax.set_yticks([])
    pos2_ax = plt.axes([0.8, 0.90, 0.1, 0.05])
    pos2_ax.set_title('Position 2')
    pos2_ax.set_xticks([])
    pos2_ax.set_yticks([])
    pos1_tb, pos2_tb = pos_tb_setup(pos1_ax=pos1_ax,
                                    pos2_ax=pos2_ax)

    # Initiate Buttons
    close_button_ax = plt.axes([0.15, 0.05, 0.1, 0.05])
    closebtn_start(chi_figures=chi_figures,
                   btn_ax=close_button_ax)

    # Initiate the fig, axs, and other tb
    chi_figures.second_fig = fig
    chi_figures.second_axs = axs
    chi_figures.small_idx_tb = small_idx_tb
    chi_figures.large_idx_tb = large_idx_tb
    chi_figures.pos1_tb = pos1_tb
    chi_figures.pos2_tb = pos2_tb


def closebtn_start(chi_figures, btn_ax):
    """Set up the close button

    Parameters
    ==========
    chi_figures (Chi_FiguresClass)
        the chi_figuresclass
    btn_ax (matplotlib_axis)
        the figure axis corresponding to the close button

    Returns
    =======
    Nothing
    """
    closebtn = Button(ax=btn_ax,
                      label='Finish',
                      color='teal',
                      hovercolor='tomato')

    chi_figures.closebtn = closebtn


def display_second_images(chi_figures):
    """Display the second figure

    Parameters
    ==========
    chi_figures (Chi_FiguresClass)
        the chi_figuresclass

    Returns
    =======
    Nothing
    """

    # Grab image axes
    axs = chi_figures.second_axs
    ims = chi_figures.images

    # Set initial tb-input vals
    small_idx_tb = chi_figures.small_idx_tb
    large_idx_tb = chi_figures.large_idx_tb
    pos1 = int(chi_figures.pos1_tb.text)
    pos2 = int(chi_figures.pos2_tb.text)
    vmin = int(chi_figures.vmin_spot_tb.text)
    vmax = int(chi_figures.vmax_spot_tb.text)
    idx1 = int(small_idx_tb.text)
    idx2 = int(large_idx_tb.text)

    # Ask user what kind of scan they are running through
    # spl rock vs det rock have difference theta positions on detectors
    if chi_figures.user_rocking == 'spl':
        angle1 = np.round(chi_figures.scan_theta[0][idx1][0], 5)
        angle2 = np.round(chi_figures.scan_theta[0][idx2][0], 5)
    elif chi_figures.user_rocking == 'det':
        angle1 = float(np.round(chi_figures.scan_theta[idx1], 5))
        angle2 = float(np.round(chi_figures.scan_theta[idx2], 5))

    # Reset image values
    chi_figures.angle1 = angle1
    chi_figures.angle2 = angle2
    axs[0].cla()
    axs[1].cla()
    axs[0].imshow(ims[idx1], vmin=vmin, vmax=vmax)
    axs[0].axvline(x=pos1)
    axs[0].set_title('IDX {}  Angle {}'.format(idx1, angle1))
    axs[1].imshow(ims[idx2], vmin=vmin, vmax=vmax)
    axs[1].axvline(x=pos2)
    axs[1].set_title('IDX {}  Angle {}'.format(idx2, angle2))
    chi_figures.pos1 = pos1
    chi_figures.pos2 = pos2


def closebtn_press(event, self, chi_figures):
    """Set the chi angle difference, position difference, and image dimension
    upon closing the figure

    Parameters
    ==========
    event (matplotlib event)
        matplotlib event
    self (SXDMFrameset)
        the SXDMFrameset)
    chi_figures (Chi_FiguresClass)
        the chi_figuresclass

    Returns
    =======
    Nothing - runs chis() function. see documentation for values set
    """
    # Subtract the two sample/detector angles
    self.chi_angle_difference = abs(np.subtract(chi_figures.angle1, chi_figures.angle2))

    # Subtract the two pixel center values
    self.chi_position_difference = abs(np.subtract(chi_figures.pos1, chi_figures.pos2))

    # Get the image dimensions
    self.chi_image_dimensions = chi_figures.image_dimensions

    plt.close('all')

    # Determining broadening, numberical aperature, chi bounds, and other stuff
    chis(self)


def vs_change(event, chi_figures):
    """When the user changes the vmin or vmax update the figures

    Parameters
    ==========
    event (matplotlib event)
        matplotlib event
    chi_figures (Chi_FiguresClass)
        the chi_figuresclass

    Returns
    =======
    Nothing
    """
    # axs = chi_figures.first_axs
    # ims = chi_figures.images
    # vmin_spot_tb = chi_figures.vmin_spot_tb
    # vmax_spot_tb = chi_figures.vmax_spot_tb
    display_first_images(chi_figures=chi_figures)


def second_change(event, chi_figures):
    """When the second figure values change, update the second figure

    Parameters
    ==========
    event (matplotlib event)
        matplotlib event
    chi_figures (Chi_FiguresClass)
        the chi_figuresclass

    Returns
    =======
    Nothing
    """

    display_second_images(chi_figures=chi_figures)


def chi_function(self):
    """Runs all code necessary to determine the chi bounds

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframeset

    Returns
    =======
    Nothing
    """

    chi_figures = first_chi_figure_setup(self=self)
    chi_figures.user_rocking = self.user_rocking
    chi_figures.user_det_theta = self.scan_theta
    display_first_images(chi_figures=chi_figures)
    second_chi_figure_setup(chi_figures=chi_figures)
    display_second_images(chi_figures=chi_figures)

    p_display_images = partial(vs_change,
                               chi_figures=chi_figures)
    p_display_second_images = partial(second_change,
                                      chi_figures=chi_figures)
    p_closebtn = partial(closebtn_press, self=self, chi_figures=chi_figures)

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
    """Set up the minmax textboxes

    Parameters
    ==========
    vmin_spot_ax (matplotlib axis)
        the figure axis that corresponds to the vmin value of the spot diffraction
    vmax_spot_ax (matplotlib axis)
        the figure axis that corresponds to the vmax value of the spot diffraction

    Returns
    =======
    vmin and vmax textboxes
    """
    vmin_spot_tb = TextBox(vmin_spot_ax, 'vmin', initial='0')
    vmax_spot_tb = TextBox(vmax_spot_ax, 'vmax', initial='2')
    plt.draw()
    return vmin_spot_tb, vmax_spot_tb


def idx_tb_setup(vmin_spot_ax, vmax_spot_ax):
    """Set up the index textboxes
    DEPRECIATED

    Returns
    =======
    position 1 and position 2 textboxes for index values
    """
    pos1_tb = TextBox(vmin_spot_ax, '', initial='0')
    pos2_tb = TextBox(vmax_spot_ax, '', initial='1')
    plt.draw()
    return pos1_tb, pos2_tb


def pos_tb_setup(pos1_ax, pos2_ax):
    """Set up the position text boxes

    Parameters
    ==========
    pos1_ax (matplotlib axis)
        the figure axis corresponding to the vertical line position of the first (left) image
    pos2_ax (matplotlib axis)
        the figure axis corresponding to the vertical line position of the second (right) image

    Returns
    =======
    position 1 and position 2 textboxes for index values
    """
    pos1_ax_tb = TextBox(pos1_ax, '', initial='0')
    pos2_ax_tb = TextBox(pos2_ax, '', initial='0')
    plt.draw()
    return pos1_ax_tb, pos2_ax_tb


def chis(self):
    """Calculates the bounds for the detector

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframeset

    Returns
    =======
    Nothing

    Prints and Sets
    ======
    self.chi value,
    self.focal_length,
    self.NA_mrads (numberical aperature),
    self.broadening_in_pix of the detector
    """
    # Grab pixel size, and angle difference, and scan dimensions
    pix_size_um = float(h5grab_data(file=self.file,
                                    data_loc='zone_plate/detector_pixel_size'))
    self.pix_size_um = pix_size_um
    tot_angle_diff = self.chi_angle_difference
    dimensions = self.chi_image_dimensions
    pixel_diff = self.chi_position_difference

    # Determine the angle and total length
    angle_rads = math.radians(tot_angle_diff)
    length = (pixel_diff * pix_size_um)

    r = (length/math.tan(angle_rads))/1000
    self.r_mm = r

    Chi = math.degrees(math.atan((((((dimensions[0])/2)*pix_size_um)/1000))/r))
    self.chi = Chi
    broadening_in_pixles(self)

    print('Chi bound is: {} Degrees\nFocal Length is : {} mm\nNumberical Aperature is: {} mrads\n'
          'Radius of Broadening is: {} pixels'.format(self.chi,
                                                      self.focal_length_mm,
                                                      self.NA_mrads,
                                                      self.broadening_in_pix))

    # Making sure the output is OK
    self.testing_chi_output = [self.chi,
                               self.focal_length_mm,
                               self.NA_mrads,
                               self.broadening_in_pix]


def broadening_in_pixles(self):
    """Determine the instrumental broadening in pixels as well as the focal length
    and numberical aperature

    Returns
    =======
    Nothing

    Sets
    ====
    self.focal_length_mm
    self.NA_mrads
    self.broadening_in_pix
    """

    # Read attributes set by the User
    Kev = float(h5read_attr(file=self.file, loc=self.dataset_name, attribute_name='Kev'))
    D_um = float(h5grab_data(file=self.file,
                             data_loc='zone_plate/D_um'))
    d_rN_nm = float(h5grab_data(file=self.file,
                                data_loc='zone_plate/d_rN_nm'))
    r_mm = self.r_mm

    pix_size_um = self.pix_size_um

    D_nm = D_um * 1000
    r_um = r_mm * 1000

    half_zp_nm = D_nm/2

    plancks_constant = (6.62607004*10**-34)/(1.60217662*10**-19)
    speed_of_light = 299792458
    hc = plancks_constant * speed_of_light*10**9
    wavelength_nm = hc/(Kev*1000)

    f_nm = (D_nm * d_rN_nm)/wavelength_nm
    fraction = half_zp_nm/f_nm
    len_in_pix = r_um/pix_size_um

    self.focal_length_mm = f_nm/1000000
    self.NA_mrads = fraction * 1000
    self.broadening_in_pix = (half_zp_nm/f_nm) * len_in_pix
