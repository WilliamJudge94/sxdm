import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from matplotlib.widgets import Button, TextBox
import imageio
from pathlib import Path
import os
import sys
from functools import partial
from time import time
import warnings
import time

import h5py

from postprocess import pixel_analysis_return, saved_return
from mis import centering_det, results_2dsum#, median_blur
from postprocess import centroid_roi_map, pooled_return
from pixel import theta_maths, chi_maths, grab_pix, sum_pixel
from clicks import check_mouse_ax, fig_leave
from h5 import h5get_image_destination
from background import scan_background_finder
from summed2d import summed2d_all_data, summed2d_all_data_v2

import config

def figure_setup():
    """Set up the viewer figure

    Returns
    =======
    All axes for the figure
    """

    fig = plt.figure(figsize=(12, 6))
    mpl.rcParams['axes.linewidth'] = 2

    # Initiate the basic axes
    fluor_ax = plt.subplot2grid((4, 5), (1, 0), colspan=1, rowspan=2)
    fluor_ax.set_title('Fluorescence')
    roi_ax = plt.subplot2grid((4, 5), (1, 4), colspan=1, rowspan=2)
    roi_ax.set_title('ROI')
    spot_diff_ax = plt.subplot2grid((4, 5), (0, 1), colspan=1, rowspan=1)
    spot_diff_ax.set_title('User Spot Diff.')
    summed_dif_ax = plt.subplot2grid((4, 5), (0, 3), colspan=1, rowspan=1)
    summed_dif_ax.set_title('Summed Diff.')

    # Initiate the ttheta axes
    ttheta_map_ax = plt.subplot2grid((4, 5), (2, 1), colspan=1, rowspan=1)
    ttheta_map_ax.set_xticks([])
    ttheta_map_ax.set_yticks([])
    ttheta_centroid_ax = plt.subplot2grid((4, 5), (2, 2), colspan=2, rowspan=1)

    # Initiate the chi axes
    chi_map_ax = plt.subplot2grid((4, 5), (3, 1), colspan=1, rowspan=1)
    chi_map_ax.set_xticks([])
    chi_map_ax.set_yticks([])
    chi_centroid_ax = plt.subplot2grid((4, 5), (3, 2), colspan=2, rowspan=1)

    # Initiate the buttons
    reprocessbtn_ax = plt.subplot2grid((4, 5), (3, 0), colspan=1, rowspan=1)
    savingbtn_ax = plt.subplot2grid((4, 5), (3, 4), colspan=1, rowspan=1)

    # Initiate the vmin/vmax textbox axes for the spot diffraction
    vmin_spot_ax = plt.axes([0.1, 0.85, 0.1, 0.05])
    vmax_spot_ax = plt.axes([0.1, 0.78, 0.1, 0.05])

    # Initiate the vmin/vmax textbox axes for the summed diffraction
    vmin_sum_ax = plt.axes([0.82, 0.85, 0.1, 0.05])
    vmax_sum_ax = plt.axes([0.82, 0.78, 0.1, 0.05])

    # Initiate the analysis textbox axes
    med_blur_dis_ax = plt.axes([0.40, 0.60, 0.06, 0.05])
    med_blur_h_ax = plt.axes([0.40, 0.53, 0.06, 0.05])
    stdev_ax = plt.axes([0.6, 0.6, 0.06, 0.05])
    multiplier_ax = plt.axes([0.6, 0.53, 0.06, 0.05])

    return fig, fluor_ax, roi_ax, spot_diff_ax,\
           summed_dif_ax, ttheta_map_ax, ttheta_centroid_ax,\
           chi_map_ax, chi_centroid_ax, reprocessbtn_ax, savingbtn_ax,\
           vmin_spot_ax, vmax_spot_ax, vmin_sum_ax, vmax_sum_ax,\
           med_blur_dis_ax, med_blur_h_ax, stdev_ax, multiplier_ax


def sum_error():
    """If there is an error loading data, import psyduck

    Return
    ======
    psyduck image
    """

    # Obtain the module location
    full_path = os.path.realpath(__file__)
    new = full_path.split('/')[0:-1]

    # Grab the psyduck image
    new2 = np.append(new, ['templates', 'psy.png'])
    new3 = '/'.join(new2)
    im = imageio.imread(new3)

    return im


def btn_setup(reproocessbtn_ax, savingbtn_ax):
    """Set up the reprocess and saving button

    Parameters
    ==========
    reproocessbtn_ax: (matplotlib axis)
        the reproocess button figure axis
    savingbtn_ax: (matplotlib axis)
        the saving button figure axis

    Return
    ======
    reprocess and saving button
    """

    # Start the reprocess and saving buttons
    reproocessbtn = Button(ax=reproocessbtn_ax,
                           label='Reprocess',
                           color='teal',
                           hovercolor='tomato')
    savingbtn = Button(ax=savingbtn_ax,
                       label='Save/Reload',
                       color='teal',
                       hovercolor='tomato')
    plt.draw()

    return reproocessbtn, savingbtn


def tb_setup(vmin_spot_ax, vmax_spot_ax,
             vmin_sum_ax, vmax_sum_ax,
             med_blur_dis_ax, med_blur_h_ax,
             stdev_ax, multiplier_ax, self):

    """Set up all textboxes
    Parameters
    ==========
    vmin_spot_ax (matplotlib axis)
        the figure axis that goes to the vmin change for the spot diffraction
    vmax_spot_ax (matplotlib axis)
        the figure axis that goes to the vmax change for the spot diffraction
    vmin_sum_ax (matplotlib axis)
        the figure axis that goes to the vmin change for the summed diffraction
    vmax_spot_ax (matplotlib axis)
        the figure axis that goes to the vmax change for the summed diffraction
    med_blur_dis_ax (matplotlib axis)
        the figure axis that goes to the median blur distance value
    med_blur_h_ax (matplotlib axis)
        the figure axis that goes to the median blur height value
    stdev_ax (matplotlib axis)
        the figure axis that goes to the standard deviation value
    multiplier_ax (matplotlib axis)
        the figure axis that goes to the background multiplier value
    self (SXDMFrameset)
        the sxdmframset
    Returns
    =======
    All textboxes associated with these axis
    """

    # If you can't load in previous analysis parameters, set them to default
    try:
        med_blur_dis = str(int(self.analysis_params[0]))
        med_blur_hei = str(int(self.analysis_params[1]))
        stdev = str(int(self.analysis_params[2]))
        bkg_x = str(int(self.analysis_params[3]))

    except:
        med_blur_dis = '2'
        med_blur_hei = '1'
        stdev = '25'
        bkg_x = '0'

    # Set TextBox values
    vmin_spot_tb = TextBox(vmin_spot_ax, 'vmin', initial='0')
    vmax_spot_tb = TextBox(vmax_spot_ax, 'vmax', initial='2')
    vmin_sum_tb = TextBox(vmin_sum_ax, 'vmin', initial='0')
    vmax_sum_tb = TextBox(vmax_sum_ax, 'vmax', initial='1200')
    med_blur_dis_tb = TextBox(med_blur_dis_ax, 'med_dis', initial=med_blur_dis)
    
    if config.algorithm != 'selective':
        med_blur_h_tb = TextBox(med_blur_h_ax, 'med_h', initial=med_blur_hei, color='red')
        warnings.warn('User In --{}-- Mode. Use --selective-- Mode For Median_Blur_Height Access.'.format(config.algorithm))

    else:
        med_blur_h_tb = TextBox(med_blur_h_ax, 'med_h', initial=med_blur_hei)
    
    stdev_tb = TextBox(stdev_ax, 'stdev_min', initial=stdev)
    multiplier_tb = TextBox(multiplier_ax, 'bkgx', initial=bkg_x)
    plt.draw()

    return vmin_spot_tb, vmax_spot_tb, vmin_sum_tb, vmax_sum_tb,\
           med_blur_dis_tb, med_blur_h_tb, stdev_tb, multiplier_tb


def load_static_data(results, vmin_sum, vmax_sum, fluor_ax, roi_ax,
                     summed_dif_ax, ttheta_map_ax, chi_map_ax, fluor_image, user_class=False):
    """Load all the static data for the viewer
    Parameters
    ==========
    results (nd.array)
        the output of the self.analysis function or the self.results value
    vmin_sum (int)
        the vmin for the summed diffraction image
    vmax_sum (int)
        the vmax for the summed diffraction image
    fluor_ax (matplotlib axis)
        the figure axis for the fluorescence image
    roi_ax (matplotlib axis)
        the figure axis for the region of interest image
    summed_dif_ax (matplotlib axis)
        the figure axis for the summed diffraction image
    ttheta_map_ax (matplotlib axis)
        the figure axis for the 2theta centroid map
    chi_map_ax (matplotlib axis)
        the figure axis for the chi centroid map
    fluor_image (image array)
        the fluorescence image the user would like to display in the figure
    user_class (SXDMFrameset)
        the sxdmframeset object or False
    Returns
    =======
    Nothing - displays figure images
    """
    
    # Grab image data
    roi_im = centroid_roi_map(results, 'full_roi')
    chi_centroid = centroid_roi_map(results, 'chi_centroid')
    ttheta_centroid = centroid_roi_map(results, 'ttheta_centroid')

    # If there is no fluor image display the roi image in its place
    if np.shape(fluor_image) != ():
        pass
    else:
        fluor_image = roi_im

    # Grabbing the summed diffraction pattern
    try:
        try:
            # If the diffraction pattern has already been loaded, reload the image
            summed_dif_ax.imshow(user_class.centroid_viewer_summed_dif,
                                 vmin=vmin_sum, vmax=vmax_sum, extent=user_class.extents)
        except:
            # If it hasn't the create the image and store it to difference sxdmframeset.variables
            user_class.centroid_viewer_summed_dif = summed2d_all_data(self=user_class, bkg_multiplier=1)
            summed_dif_ax.imshow(user_class.centroid_viewer_summed_dif,
                                 vmin=vmin_sum, vmax=vmax_sum, extent=user_class.extents)
            user_class.dif_im = user_class.centroid_viewer_summed_dif

    except:
        try:
            # If above fails try to reload the summed data from the user_class.results variable
            summed_dif_ax.imshow(results_2dsum(ERRORuser_class))
            summed_dif_ax.set_xticks = []
            summed_dif_ax.set_yticks = []
        except:
            # If this also fails throw the psyduck error
            summed_dif_ax.imshow(sum_error())
            summed_dif_ax.set_xticks = []
            summed_dif_ax.set_yticks = []

    # Plot other image data
    ttheta_map_ax.imshow(ttheta_centroid)
    chi_map_ax.imshow(chi_centroid, cmap='magma')
    roi_ax.imshow(roi_im, cmap='inferno')
    fluor_ax.imshow(fluor_image, cmap='inferno')
    


def reload_some_static_data(results, roi_ax,
                     ttheta_map_ax, chi_map_ax):
    """Reloading some of the static data when you save/reload image
    Parameters
    ==========
    results (nd.array)
        the output of the self.analysis function or the self.results value
    roi_ax (matplotlib axis)
        the figure axis for the region of interest map
    ttheta_map_ax (matplotlib axis)
        the figure axis for the 2theta centroid map
    chi_map_ax (matplotlib axis)
        the figure axis for the chi centroid map
    Returns
    =======
    Nothing - displays figure images
    """

    # Get image data
    roi_ax.cla()
    ttheta_map_ax.cla()
    chi_map_ax.cla()
    roi_im = centroid_roi_map(results, 'full_roi')
    chi_centroid = centroid_roi_map(results, 'chi_centroid')
    ttheta_centroid = centroid_roi_map(results, 'ttheta_centroid')

    # Plot image data
    ttheta_map_ax.imshow(ttheta_centroid)
    chi_map_ax.imshow(chi_centroid, cmap='magma')
    roi_ax.imshow(roi_im, cmap='inferno')


def spot_dif_ram_save(self):
    """Allows the program to take all the user_class.image_array images and sum them together to get a
    single summed diffraction image

    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframeset object

    Returns
    =======
    the summed diffraction image for the entire FOV set by the create_imagearray() function
    """
    image_array = self.image_array

    # Grab the diffraction images
    pix = grab_pix(array=image_array, row=self.row, column=self.column, int_convert=True)
    destination = h5get_image_destination(self=self, pixel=pix)
    each_scan_diffraction = sum_pixel(self=self, images_loc=destination)

    # Background Correction
    backgrounds = scan_background_finder(destination=destination, background_dic=self.background_dic)
    each_scan_diffraction_post = np.subtract(each_scan_diffraction, backgrounds)

    # Make the summed diffraction image
    summed_dif = np.sum(each_scan_diffraction_post, axis=0)

    return summed_dif


def load_dynamic_data(results, vmin_spot, vmax_spot, spot_dif_ax,
                      ttheta_centroid_ax, chi_centroid_ax, med_blur_distance,
                      med_blur_height, stdev_min, row, column, self):
    """Load the dynamic data in the viewer based on the user inputs
    Parameters
    ==========
    results (nd.array)
        the output of self.analysis or the self.results value
    vmin_spot (int)
        the vmin for the summed diffraction spot image
    vmax_spot (int)
        the vmax for the summed diffraction spot image
    spot_dif_ax (matplotlib axis)
        the figure axis for the diffraction spot image
    ttheta_centroid_ax (matplotlib axis)
        the figure axis for the 1D two theta plot
    chi_centroid_ax (matplotlib axis)
        the figure axis for the 1D chi plot
    med_blur_distance (int)
        the integer value used in the median_blur() function
    med_blur_height (int)
        the integer value used in the median_blur() function
    stdev_min (int)
        the standard deviation value used in the median_blur() segmentation function
    row (int)
        the row the user would like to load the data for
    column (int)
        the bolumn the user would like to load the data for
    self (SXDMFramset)
        the sxdmframset
    Returns
    =======
    Nothing - loads figure data
    """

    # Clear axes
    spot_dif_ax.cla()
    spot_dif_ax.set_title('User Spot Diff.')
    ttheta_centroid_ax.cla()
    chi_centroid_ax.cla()

    # See if the User has selected a pixel - if not set it to the 0, 0 pixel
    try:
        pre1, pre2, = self.row, self.column

    except:
        self.row = 0
        self.column = 0

    # Return all the data from the analysis function
    return_dic = pixel_analysis_return(results, self.row, self.column)

    # Grab RAM required summed diffraction
    # Redundent - used to have difference functions for self.diffraction_load True vs False
    try:
        if self.diffraction_load == True:

            self.centroid_viewer_spot_diff = spot_dif_ram_save(self)

        elif self.diffraction_load == False:

            self.centroid_viewer_spot_diff = spot_dif_ram_save(self)

        spot_dif = self.centroid_viewer_spot_diff

    except Exception as ex:
        print('viewer.py/load_dynamic_data', ex)

    # Grab spot diffraction
    try:
        spot_dif_ax.imshow(spot_dif, vmin=vmin_spot, vmax=vmax_spot, extent=self.extents)
    except Exception as ex:
        print('viewer.py/load_dynamic_data - 2', ex)
        spot_dif_ax.imshow(sum_error())
        spot_dif_ax.set_xticks = []
        spot_dif_ax.set_yticks = []

    try:

        # Calculate centroid map data and analysis
        ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2 = theta_maths(spot_dif,
                                                                               med_blur_distance,
                                                                               med_blur_height,
                                                                               stdev_min)
        chi, chi_centroid, chi_centroid_finder = chi_maths(spot_dif,
                                                           med_blur_distance,
                                                           med_blur_height,
                                                           stdev_min)

    except Exception as ex:
        print('viewer.py/load_dynamic_data', ex)

        # If you can't calculate centroid, pull data from save file
        # SET TITLE COLOR TO RED

        ttheta = return_dic['ttheta']
        ttheta_centroid_finder = return_dic['ttheta_corr']
        ttheta_centroid = return_dic['ttheta_cent']

        chi = return_dic['chi']
        chi_centroid_finder = return_dic['chi_corr']
        chi_centroid = return_dic['chi_cent']

    # Plot the analysis
    ttheta_x_bounds = convert_x_axis(ttheta, self.extents, type='ttheta', centroid_value=ttheta_centroid)
    ttheta_centroid_ax.plot(ttheta_x_bounds[0], ttheta, color='blue')
    ttheta_centroid_ax.plot(ttheta_x_bounds[0], ttheta_centroid_finder, color='red')
    ttheta_centroid_ax.axvline(x=ttheta_x_bounds[1], color='black')

    chi_x_bounds = convert_x_axis(chi, self.extents, type='chi', centroid_value=chi_centroid)
    chi_centroid_ax.plot(chi_x_bounds[0], chi, color='blue')
    chi_centroid_ax.plot(chi_x_bounds[0], chi_centroid_finder, color='red')
    chi_centroid_ax.axvline(x=chi_x_bounds[1], color='black')


def run_viewer(user_class, fluor_image):
    """Function that compiles functions to get the viewer working
    Parameters
    ==========
    user_class (SXDMFrameset)
        the sxdmframeset
    fluor_image (image)
        the fluorescence image the user would like to load into the viewer
    Returns
    =======
    Nothing - loads figure data
    """
    image_array_bkg_check(user_class)

    try:
        dummy = user_class.centroid_viewer_summed_dif
    except:
        user_class.centroid_viewer_summed_dif = summed2d_all_data_v2(self=user_class, bkg_multiplier=1)
    # Determine that the starting row and column values should be
    ro = user_class.analysis_total_rows
    co = user_class.analysis_total_columns

    if isinstance(ro, tuple):
        st_row = ro[0]
    else:
        st_row = 0
    user_class.row = st_row

    if isinstance(co, tuple):
        st_column = co[0]
    else:
        st_column = 0
    user_class.column = st_column

    # Show results for the starting row and column
    try:
        results = user_class.results
        return_dic = pixel_analysis_return(user_class.results, st_row, st_column)

    # If nothing found try to reload the data from the save file
    except:
        print('No Results Found. Importing From Saved File...')

    if user_class.diffraction_load == False:
        print("Not Importing Diffraction")
        user_class.reload_save(summed_dif_return=user_class.diffraction_load)
        results = user_class.results

    # make buttons and tb do something
    # make clicking figures do something
    current_figure = FiguresClass()
    current_figure.user_class = user_class
    current_figure.diffraction_load = user_class.diffraction_load
    current_figure.diffraction_load = user_class.diffraction_load
    current_figure.save_filename = user_class.save_filename
    current_figure.dataset_name = user_class.dataset_name

    # See if there has been an analysis and set the row and column values
    try:
        dummy = current_figure.row
    except:
        ro = user_class.analysis_total_rows
        co = user_class.analysis_total_columns

        if isinstance(ro, tuple):
            current_figure.row = ro[0]
        else:
            current_figure.row = 0

        if isinstance(co, tuple):
            current_figure.column = co[0]
        else:
            current_figure.column = 0


        current_figure.viewer_currentax = 'roi'

    current_figure.results = results

    # Setting up axis
    current_figure.fig, current_figure.fluor_ax, current_figure.roi_ax, current_figure.spot_diff_ax, \
    current_figure.summed_dif_ax, current_figure.ttheta_map_ax, current_figure.ttheta_centroid_ax, \
    current_figure.chi_map_ax, current_figure.chi_centroid_ax, current_figure.reprocessbtn_ax, \
    current_figure.savingbtn_ax, \
    current_figure.vmin_spot_ax, current_figure.vmax_spot_ax, current_figure.vmin_sum_ax,\
    current_figure.vmax_sum_ax, \
    current_figure.med_blur_dis_ax, current_figure.med_blur_h_ax, current_figure.stdev_ax,\
    current_figure.multiplier_ax = figure_setup()

    # Setting up buttons
    current_figure.reproocessbtn, current_figure.savingbtn = btn_setup(current_figure.reprocessbtn_ax,
                                                                       current_figure.savingbtn_ax)

    # Setting up textboxes
    current_figure.vmin_spot_tb, current_figure.vmax_spot_tb, current_figure.vmin_sum_tb,\
    current_figure.vmax_sum_tb, \
    current_figure.med_blur_dis_tb, current_figure.med_blur_h_tb, current_figure.stdev_tb,\
    current_figure.multiplier_tb = \
        tb_setup(current_figure.vmin_spot_ax, current_figure.vmax_spot_ax, current_figure.vmin_sum_ax,
                 current_figure.vmax_sum_ax, current_figure.med_blur_dis_ax,
                 current_figure.med_blur_h_ax, current_figure.stdev_ax, current_figure.multiplier_ax, user_class)

    # Finding current textbox values
    current_figure.vmin_spot_val = int(current_figure.vmin_spot_tb.text)
    current_figure.vmax_spot_val = int(current_figure.vmax_spot_tb.text)
    current_figure.vmin_sum_val = int(current_figure.vmin_sum_tb.text)
    current_figure.vmax_sum_val = int(current_figure.vmax_sum_tb.text)
    current_figure.med_blur_dis_val = int(current_figure.med_blur_dis_tb.text)
    current_figure.med_blur_h_val = int(current_figure.med_blur_h_tb.text)
    current_figure.stdev_val = float(current_figure.stdev_tb.text)
    current_figure.bkgx_val = float(current_figure.multiplier_tb.text)

    # Loading all static data
    load_static_data(current_figure.results, current_figure.vmin_sum_val, current_figure.vmax_sum_val,
                     current_figure.fluor_ax,
                     current_figure.roi_ax, current_figure.summed_dif_ax,
                     current_figure.ttheta_map_ax, current_figure.chi_map_ax, fluor_image, user_class=user_class)

    # Loading initial dynamic data
    load_dynamic_data(current_figure.results, current_figure.vmin_spot_val, current_figure.vmax_spot_val,
                      current_figure.spot_diff_ax, current_figure.ttheta_centroid_ax, current_figure.chi_centroid_ax,
                      current_figure.med_blur_dis_val, current_figure.med_blur_h_val, current_figure.stdev_val,
                      current_figure.row, current_figure.column, user_class)

    # Functions used for matplotlib interactions
    p_check_mouse_ax = partial(check_mouse_ax, self=current_figure)
    p_viewer_mouse_click = partial(viewer_mouse_click, self=current_figure)
    p_analysis_change = partial(analysis_change, self=current_figure)
    p_fig_leave = partial(fig_leave, self=current_figure)

    current_figure.fig.canvas.mpl_connect('axes_enter_event', p_check_mouse_ax)
    current_figure.fig.canvas.mpl_connect('axes_leave_event', p_fig_leave)
    current_figure.fig.canvas.mpl_connect('button_press_event', p_viewer_mouse_click)

    p_spot_change = partial(spot_change, self=current_figure)
    p_reprocessbtn_click = partial(reprocessbtn_click, user_class=user_class, figure_class=current_figure)
    p_savingbtn_click = partial(savingbtn_click, user_class=user_class, figure_class=current_figure)

    current_figure.vmin_spot_tb.on_submit(p_spot_change)
    current_figure.vmax_spot_tb.on_submit(p_spot_change)
    current_figure.vmin_sum_tb.on_submit(p_spot_change)
    current_figure.vmax_sum_tb.on_submit(p_spot_change)
    current_figure.stdev_tb.on_submit(p_analysis_change)
    current_figure.med_blur_h_tb.on_submit(p_analysis_change)
    current_figure.med_blur_dis_tb.on_submit(p_analysis_change)
    current_figure.multiplier_tb.on_submit(p_analysis_change)

    current_figure.reproocessbtn.on_clicked(p_reprocessbtn_click)
    current_figure.savingbtn.on_clicked(p_savingbtn_click)


def spot_change(text, self):
    """When the user changes texbox value spots on the image, reload all the data for the new spot
    Parameters
    ==========
    text (texbox text event)
        textbox text event
    self (CurrentFigure Class)
        the currecnt figure class
    Returns
    =======
    Nothing - loads figure data
    """

    # Clearing axes
    self.spot_diff_ax.cla()
    self.summed_dif_ax.cla()
    
    self.summed_dif_ax.set_title('Summed Diff.')
    self.spot_diff_ax.set_title('User Spot Diff.')

    # Reloading summed diffraction image
    im = self.user_class.centroid_viewer_summed_dif

    return_dic = pixel_analysis_return(self.results, self.user_class.row, self.user_class.column)

    if self.diffraction_load == True:
        spot_dif = self.user_class.centroid_viewer_spot_diff

    elif self.diffraction_load == False:
        spot_dif = self.user_class.centroid_viewer_spot_diff

    # Obtaining new vmin and vmax values
    self.vmin_spot_val = int(self.vmin_spot_tb.text)
    self.vmax_spot_val = int(self.vmax_spot_tb.text)
    self.vmin_sum_val = int(self.vmin_sum_tb.text)
    self.vmax_sum_val = int(self.vmax_sum_tb.text)

    # Replotting diffraction images with new vmin and vmax
    try:
        summed_dif = im
        self.summed_dif_ax.imshow(summed_dif, vmin=self.vmin_sum_val, vmax=self.vmax_sum_val, 
                                  extent=self.user_class.extents)

    except:
        self.summed_dif_ax.imshow(sum_error())
        self.summed_dif_ax.set_xticks = []
        self.summed_dif_ax.set_yticks = []

    try:
        self.spot_diff_ax.imshow(spot_dif, vmin=self.vmin_spot_val, vmax=self.vmax_spot_val)
    except:
        self.spot_diff_ax.imshow(sum_error())
        self.spot_diff_ax.set_xticks = []
        self.spot_diff_ax.set_yticks = []


def analysis_change(text, self):
    """When analysis values change, make the plots change as well to fit analysis parameters
    Parameters
    ==========
    text (textbox text event)
        textbox text event
    self (SXDMFrameset)
        the sxdmframeset
    Returns
    =======
    Nothing - loads figure data
    """
    # Make boarders red as an indicator to the User
    make_red(self)

    # Obtaining new textbox values
    self.med_blur_dis_val = int(self.med_blur_dis_tb.text)
    self.med_blur_h_val = int(self.med_blur_h_tb.text)
    self.stdev_val = float(self.stdev_tb.text)
    self.bkgx_val = float(self.multiplier_tb.text)

    # Reloading dynamic data
    load_dynamic_data(self.results, self.vmin_spot_val, self.vmax_spot_val,
                      self.spot_diff_ax, self.ttheta_centroid_ax, self.chi_centroid_ax,
                      self.med_blur_dis_val, self.med_blur_h_val, self.stdev_val,
                      self.row, self.column, self.user_class)


class FiguresClass():
    """A class function which will make it easier to move variable in and out of functions
    """
    pass


def make_red(self):
    """Show the user which figures are not current by turning them red
    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframeset
    Returns
    =======
    Nothing - loads figure formatting
    """
    axes = [self.ttheta_map_ax, self.chi_map_ax,
            self.reprocessbtn_ax]
    sides = ['left', 'right', 'top', 'bottom']
    # Making all the axes red
    for ax in axes:
        for side in sides:
            ax.spines[side].set_color('red')
    plt.draw()


def make_pink(self):
    """Show the user which values have not been saved by turning them pink
    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframeset
    Returns
    =======
    Nothing - loads figure formatting
    """
    axes = [self.ttheta_map_ax, self.chi_map_ax,
            self.savingbtn_ax, self.med_blur_dis_ax,
            self.med_blur_h_ax, self.stdev_ax,
            self.multiplier_ax]
    sides = ['left', 'right', 'top', 'bottom']
    # Making all the axis pink or black
    for ax in axes:
        for side in sides:
            ax.spines[side].set_color('fuchsia')
    for side in sides:
        self.reprocessbtn_ax.spines[side].set_color('black')
    plt.draw()


def make_black(self):
    """Reset figures to black when everything is up to date
    Parameters
    ==========
    self (SXDMFrameset)
        the sxdmframeset
    Returns
    =======
    Nothing - loads figure formatting
    """
    axes = [self.ttheta_map_ax, self.chi_map_ax,
            self.reprocessbtn_ax, self.savingbtn_ax, self.med_blur_dis_ax,
            self.med_blur_h_ax, self.stdev_ax,
            self.multiplier_ax]
    sides = ['left', 'right', 'top', 'bottom']
    # Making all axes black
    for ax in axes:
        for side in sides:
            ax.spines[side].set_color('black')
    plt.draw()


def viewer_mouse_click(event, self):
    """Based on what is clicked in the figure change the viewer accordingly
    Parameters
    ==========
    event (matplotlib event)
        matplotlib event
    self (FigureClass)
        the figureclass object
    Returns
    =======
    Nothing - loads figure formatting
    """
    if self.viewer_currentax in [self.fluor_ax, self.roi_ax] and self.viewer_currentax != None:
        # Grabbing the x and y event data for the row and column values

        t_rows = self.user_class.analysis_total_rows
        t_columns = self.user_class.analysis_total_columns

        if isinstance(t_rows, tuple):
            correction_y = min(t_rows)
        else:
            correction_y = 0

        if isinstance(t_columns, tuple):
            correction_x = min(t_columns)
        else:
            correction_x = 0

        self.row = int(np.floor(event.ydata)) + correction_y
        self.column = int(np.floor(event.xdata)) + correction_x
        self.user_class.row = self.row
        self.user_class.column = self.column

        try:
            # Resetting plots
            self.fluor_ax.lines[1].remove()
            self.fluor_ax.lines[0].remove()
            self.roi_ax.lines[1].remove()
            self.roi_ax.lines[0].remove()
            self.ttheta_map_ax.lines[1].remove()
            self.ttheta_map_ax.lines[0].remove()
            self.chi_map_ax.lines[1].remove()
            self.chi_map_ax.lines[0].remove()
        except:
            pass
        # Replotting plots
        self.fluor_ax.axvline(x=self.column, color='w', linewidth=1)
        self.fluor_ax.axhline(y=self.row, color='w', linewidth=1)

        self.roi_ax.axvline(x=self.column - correction_x, color='w', linewidth=1)
        self.roi_ax.axhline(y=self.row - correction_y, color='w', linewidth=1)

        self.ttheta_map_ax.axvline(x=self.column - correction_x, color='r', linewidth=0.5)
        self.ttheta_map_ax.axhline(y=self.row - correction_y, color='r', linewidth=0.5)

        self.chi_map_ax.axvline(x=self.column - correction_x, color='r', linewidth=0.5)
        self.chi_map_ax.axhline(y=self.row - correction_y, color='r', linewidth=0.5)

        load_dynamic_data(self.results, self.vmin_spot_val, self.vmax_spot_val, self.spot_diff_ax,
                              self.ttheta_centroid_ax, self.chi_centroid_ax, self.med_blur_dis_val,
                              self.med_blur_h_val, self.stdev_val, self.row, self.column, self.user_class)

        plt.draw()
    else:
        pass


def reprocessbtn_click(event, user_class, figure_class):
    """Calls the self.analysis function once the reprocessed button is clicked
    Parameters
    ==========
    event (matplotlib event)
        matplotlib event
    user_class (SXDMFrameset)
        the sxdmframeset
    figure_class (FigureClass)
        the figureclass
    Returns
    =======
    Nothing - loads figure formatting
    """
    # Running analysis once button has been pressed
    make_pink(figure_class)
    user_class.centroid_analysis(user_class.analysis_total_rows,
                        user_class.analysis_total_columns,
                        med_blur_distance=figure_class.med_blur_dis_val,
                        med_blur_height=figure_class.med_blur_h_val,
                        stdev_min=figure_class.stdev_val,
                        bkg_multiplier=figure_class.bkgx_val)
    # Set Attrs For reprocessbtn?


def savingbtn_click(event, user_class, figure_class):
    """Calls the self.save function and reloads data to the viewer
    Parameters
    ==========
    event (matplotlib event)
        matplotlib event
    user_class (SXDMFrameset)
        the sxdmframeset
    figure_class (FigureClass)
        the figureclass
    Returns
    =======
    Nothing - loads figure formatting
    """
    make_black(figure_class)
    user_class.save()

    # Reloading data
    reload_some_static_data(user_class.results, figure_class.roi_ax,
                            figure_class.ttheta_map_ax, figure_class.chi_map_ax)


def image_array_bkg_check(self):
    """Warns the User if they have not started the create_imagearray() or scan_background() functions

    :param self:
    :return:
    """
    try:
        im_array = self.image_array

    except:
        warnings.warn('Please Run The create_immagearray(self) Function')

    print(' ')
    time.sleep(0.5)
    try:
        bkg = self.background_dic

    except:
        warnings.warn('Please Run The scan_background(self) Function')


def convert_x_axis(intensity_values, extents, centroid_value, type='ttheta'):
    len_ints = len(intensity_values)
    ttheta_low, ttheta_high, chi_low, chi_high = extents
    if extents:
        if type == 'ttheta':
            x_vals = np.linspace(ttheta_low, ttheta_high, len_ints)
        elif type == 'chi':
            x_vals = np.linspace(chi_high, chi_low, len_ints)

        if np.isnan(centroid_value):
            new_centroid_value = np.nan
        else:
            rounded = int(centroid_value)
            new_centroid_value = x_vals[rounded]
    else:
        x_vals = np.arange(0, len_ints)
        new_centroid_value = centroid_value

    return x_vals, new_centroid_value