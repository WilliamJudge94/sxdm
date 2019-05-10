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

import h5py

from postprocess import pixel_analysis_return, saved_return
from mis import  median_blur, centering_det
from postprocess import centroid_roi_map, pooled_return
from pixel import theta_maths, chi_maths
from clicks import check_mouse_ax, fig_leave


def figure_setup():

    fig = plt.figure(figsize = (12,6))
    mpl.rcParams['axes.linewidth'] = 2
    fluor_ax = plt.subplot2grid((4,5),(1,0), colspan=1, rowspan=2)
    roi_ax = plt.subplot2grid((4, 5), (1, 4), colspan=1, rowspan=2)
    spot_diff_ax = plt.subplot2grid((4, 5), (0, 1), colspan=1, rowspan=1)
    summed_dif_ax = plt.subplot2grid((4, 5), (0, 3), colspan=1, rowspan=1)

    ttheta_map_ax = plt.subplot2grid((4, 5), (2, 1), colspan=1, rowspan=1)
    ttheta_map_ax.set_xticks([])
    ttheta_map_ax.set_yticks([])
    ttheta_centroid_ax = plt.subplot2grid((4, 5), (2, 2), colspan=2, rowspan=1)

    chi_map_ax = plt.subplot2grid((4, 5), (3, 1), colspan=1, rowspan=1)
    chi_map_ax.set_xticks([])
    chi_map_ax.set_yticks([])
    chi_centroid_ax = plt.subplot2grid((4, 5), (3, 2), colspan=2, rowspan=1)

    reprocessbtn_ax = plt.subplot2grid((4, 5), (3, 0), colspan=1, rowspan=1)
    savingbtn_ax = plt.subplot2grid((4, 5), (3, 4), colspan=1, rowspan=1)

    vmin_spot_ax = plt.axes([0.1, 0.85, 0.1, 0.05])

    vmax_spot_ax = plt.axes([0.1, 0.78, 0.1, 0.05])

    vmin_sum_ax = plt.axes([0.82, 0.85, 0.1, 0.05])

    vmax_sum_ax = plt.axes([0.82, 0.78, 0.1, 0.05])

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
    full_path = os.path.realpath(__file__)
    new = full_path.split('/')[0:-1]
    new2 = np.append(new,['templates','psy.png'])
    new3 = '/'.join(new2)
    im = imageio.imread(new3)
    return im

def btn_setup(reproocessbtn_ax, savingbtn_ax):
    reproocessbtn = Button(ax = reproocessbtn_ax,
                           label = 'Reprocess',
                           color = 'teal',
                           hovercolor = 'tomato')
    savingbtn = Button(ax = savingbtn_ax,
                       label = 'Save/Reload',
                       color = 'teal',
                       hovercolor = 'tomato')
    plt.draw()
    return reproocessbtn, savingbtn

def tb_setup(vmin_spot_ax, vmax_spot_ax,
             vmin_sum_ax,vmax_sum_ax,
             med_blur_dis_ax, med_blur_h_ax,
             stdev_ax, multiplier_ax):

    vmin_spot_tb = TextBox(vmin_spot_ax, 'vmin', initial='0')
    vmax_spot_tb = TextBox(vmax_spot_ax, 'vmax', initial='2')
    vmin_sum_tb = TextBox(vmin_sum_ax, 'vmin', initial='0')
    vmax_sum_tb = TextBox(vmax_sum_ax, 'vmax', initial='1200')
    med_blur_dis_tb = TextBox(med_blur_dis_ax, 'med_dis', initial='2')
    med_blur_h_tb = TextBox(med_blur_h_ax, 'med_h', initial='1')
    stdev_tb = TextBox(stdev_ax, 'stdev_min', initial='25')
    multiplier_tb = TextBox(multiplier_ax, 'bkgx', initial='0')
    plt.draw()

    return vmin_spot_tb, vmax_spot_tb, vmin_sum_tb, vmax_sum_tb,\
           med_blur_dis_tb, med_blur_h_tb, stdev_tb, multiplier_tb

def load_static_data(results, vmin_sum, vmax_sum, fluor_ax, roi_ax,
                     summed_dif_ax, ttheta_map_ax, chi_map_ax, fluor_image):

    roi_im = centroid_roi_map(results, 'full_roi')
    chi_centroid = centroid_roi_map(results, 'chi_centroid')
    ttheta_centroid = centroid_roi_map(results, 'ttheta_centroid')
    if np.shape(fluor_image) != ():
        pass
    else:
        fluor_image = roi_im

    try:
        summed_dif = np.sum(results[:, 1], axis = 0)
        summed_dif_ax.imshow(summed_dif, vmin = vmin_sum, vmax = vmax_sum)
    except:
        summed_dif_ax.imshow(sum_error())
        summed_dif_ax.set_xticks = []
        summed_dif_ax.set_yticks = []

    ttheta_map_ax.imshow(ttheta_centroid)
    chi_map_ax.imshow(chi_centroid, cmap = 'magma')
    roi_ax.imshow(roi_im, cmap = 'inferno')
    fluor_ax.imshow(fluor_image, cmap = 'inferno')

def reload_some_static_data(results,roi_ax,
                     ttheta_map_ax, chi_map_ax):
    roi_ax.cla()
    ttheta_map_ax.cla()
    chi_map_ax.cla()
    roi_im = centroid_roi_map(results, 'full_roi')
    chi_centroid = centroid_roi_map(results, 'chi_centroid')
    ttheta_centroid = centroid_roi_map(results, 'ttheta_centroid')

    ttheta_map_ax.imshow(ttheta_centroid)
    chi_map_ax.imshow(chi_centroid, cmap = 'magma')
    roi_ax.imshow(roi_im, cmap = 'inferno')



def load_dynamic_data(results, vmin_spot, vmax_spot, spot_dif_ax,
                      ttheta_centroid_ax, chi_centroid_ax, med_blur_distance,
                      med_blur_height, stdev_min, row, column, self):

    spot_dif_ax.cla()
    ttheta_centroid_ax.cla()
    chi_centroid_ax.cla()

    return_dic = pixel_analysis_return(results, row, column)
    #spot_dif = return_dic['summed_dif']
    try:
        if self.diffraction_load == True:
            spot_dif = return_dic['summed_dif']
        elif self.diffraction_load == False:
            #print(self.diffraction_load)
            f = h5py.File(self.save_filename, 'r')
            finder = False
            new_idx = 0
            while finder == False:
                position = f['{}/row_column'.format(self.dataset_name)][new_idx]
                if position[0] == self.row and position[1] == self.column:
                    finder = True
                else:
                    new_idx = new_idx + 1
            spot_dif = f['{}/summed_dif'.format(self.dataset_name) ][new_idx]
            #print('Row: {}, Column: {}, L_Row_column: {}'.format(self.row, self.column,
                                                                 #f['{}/row_column'.format(self.dataset_name)][new_idx]))
            f.close()
    except:
        pass


    try:
        spot_dif_ax.imshow(spot_dif, vmin=vmin_spot, vmax=vmax_spot)
    except:
        spot_dif_ax.imshow(sum_error())
        spot_dif_ax.set_xticks = []
        spot_dif_ax.set_yticks = []

    try:

        ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2 = theta_maths(spot_dif,
                                                                               med_blur_distance,
                                                                               med_blur_height,
                                                                               stdev_min)
        chi, chi_centroid, chi_centroid_finder = chi_maths(spot_dif,
                                                           med_blur_distance,
                                                           med_blur_height,
                                                           stdev_min)
        #centroid is val
        #centroid finder is corr
        #ttheta is raw
        ttheta_centroid_ax.plot(ttheta, color = 'blue')
        ttheta_centroid_ax.plot(ttheta_centroid_finder, color = 'red')
        ttheta_centroid_ax.axvline(x = ttheta_centroid, color = 'black')

        chi_centroid_ax.plot(chi, color = 'blue')
        chi_centroid_ax.plot(chi_centroid_finder, color = 'red')
        chi_centroid_ax.axvline(x = chi_centroid)

    except:
        ttheta = return_dic['ttheta']
        ttheta_centroid_finder = return_dic['ttheta_corr']
        ttheta_centroid = return_dic['ttheta_cent']

        chi = return_dic['chi']
        chi_centroid_finder = return_dic['chi_corr']
        chi_centroid = return_dic['chi_cent']

        ttheta_centroid_ax.plot(ttheta, color = 'blue')
        ttheta_centroid_ax.plot(ttheta_centroid_finder, color = 'red')
        ttheta_centroid_ax.axvline(x = ttheta_centroid, color = 'black')

        chi_centroid_ax.plot(chi, color = 'blue')
        chi_centroid_ax.plot(chi_centroid_finder, color = 'red')
        chi_centroid_ax.axvline(chi_centroid, color = 'black')

def run_viewer(user_class, fluor_image):
    try:

        results = user_class.results
        return_dic = pixel_analysis_return(user_class.results, 0, 0)
        if np.shape(return_dic['summed_dif']) == () and user_class.diffraction_load == True:
            user_class.reload_save(summed_dif_return=user_class.diffraction_load)
            results = user_class.results
    except:
        print('No Results Found. Importing From Saved File...')
    if user_class.diffraction_load == False:
        print("Not Importing Diffraction")
        user_class.reload_save(summed_dif_return=user_class.diffraction_load)
        results = user_class.results
    #make buttons and tb do something
    #make clicking figures do something
    current_figure = FiguresClass()
    current_figure.diffraction_load = user_class.diffraction_load
    current_figure.save_filename = user_class.save_filename
    current_figure.dataset_name = user_class.dataset_name
    try:
        dummy = current_figure.row
    except:
        current_figure.row = 10
        current_figure.column = 10
        current_figure.viewer_currentax = 'roi'

    current_figure.results = results

    current_figure.fig, current_figure.fluor_ax, current_figure.roi_ax, current_figure.spot_diff_ax, \
    current_figure.summed_dif_ax, current_figure.ttheta_map_ax, current_figure.ttheta_centroid_ax, \
    current_figure.chi_map_ax, current_figure.chi_centroid_ax, current_figure.reprocessbtn_ax, \
    current_figure.savingbtn_ax, \
    current_figure.vmin_spot_ax, current_figure.vmax_spot_ax, current_figure.vmin_sum_ax,\
    current_figure.vmax_sum_ax, \
    current_figure.med_blur_dis_ax, current_figure.med_blur_h_ax, current_figure.stdev_ax,\
    current_figure.multiplier_ax = figure_setup()

    current_figure.reproocessbtn, current_figure.savingbtn = btn_setup(current_figure.reprocessbtn_ax,
                                                                       current_figure.savingbtn_ax)
    current_figure.vmin_spot_tb, current_figure.vmax_spot_tb, current_figure.vmin_sum_tb,\
    current_figure.vmax_sum_tb, \
    current_figure.med_blur_dis_tb, current_figure.med_blur_h_tb, current_figure.stdev_tb,\
    current_figure.multiplier_tb = \
        tb_setup(current_figure.vmin_spot_ax, current_figure.vmax_spot_ax, current_figure.vmin_sum_ax,
                 current_figure.vmax_sum_ax, current_figure.med_blur_dis_ax,
                 current_figure.med_blur_h_ax, current_figure.stdev_ax, current_figure.multiplier_ax)

    current_figure.vmin_spot_val = int(current_figure.vmin_spot_tb.text)
    current_figure.vmax_spot_val = int(current_figure.vmax_spot_tb.text)
    current_figure.vmin_sum_val = int(current_figure.vmin_sum_tb.text)
    current_figure.vmax_sum_val = int(current_figure.vmax_sum_tb.text)
    current_figure.med_blur_dis_val = int(current_figure.med_blur_dis_tb.text)
    current_figure.med_blur_h_val = int(current_figure.med_blur_h_tb.text)
    current_figure.stdev_val = float(current_figure.stdev_tb.text)
    current_figure.bkgx_val = float(current_figure.multiplier_tb.text)


    load_static_data(current_figure.results, current_figure.vmin_sum_val, current_figure.vmax_sum_val,
                     current_figure.fluor_ax,
                     current_figure.roi_ax, current_figure.summed_dif_ax,
                     current_figure.ttheta_map_ax, current_figure.chi_map_ax, fluor_image)

    load_dynamic_data(current_figure.results, current_figure.vmin_spot_val, current_figure.vmax_spot_val,
                      current_figure.spot_diff_ax, current_figure.ttheta_centroid_ax, current_figure.chi_centroid_ax,
                      current_figure.med_blur_dis_val, current_figure.med_blur_h_val, current_figure.stdev_val,
                      current_figure.row, current_figure.column, user_class)


    p_check_mouse_ax = partial(check_mouse_ax,self = current_figure)
    p_viewer_mouse_click = partial(viewer_mouse_click, self = current_figure)
    p_analysis_change = partial(analysis_change, self = current_figure)
    p_fig_leave = partial(fig_leave, self = current_figure)

    current_figure.fig.canvas.mpl_connect('axes_enter_event', p_check_mouse_ax)
    current_figure.fig.canvas.mpl_connect('axes_leave_event', p_fig_leave)
    current_figure.fig.canvas.mpl_connect('button_press_event', p_viewer_mouse_click)

    p_spot_change = partial(spot_change, self = current_figure)
    p_reprocessbtn_click = partial(reprocessbtn_click, user_class = user_class, figure_class = current_figure )
    p_savingbtn_click = partial(savingbtn_click, user_class = user_class, figure_class = current_figure )

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

    self.spot_diff_ax.cla()
    self.summed_dif_ax.cla()

    return_dic = pixel_analysis_return(self.results, self.row, self.column)
    if self.diffraction_load == True:
        spot_dif = return_dic['summed_dif']
    elif self.diffraction_load == False:
        #print(self.diffraction_load)
        f = h5py.File(self.save_filename, 'r')
        finder = False
        new_idx = 0
        while finder == False:
            position = f['{}/row_column'.format(self.dataset_name)][new_idx]
            if position[0] == self.row and position[1] == self.column:
                finder = True
            else:
                new_idx = new_idx + 1
        spot_dif = f['{}/summed_dif'.format(self.dataset_name) ][new_idx]
        #print('Row: {}, Column: {}, L_Row_column: {}'.format(self.row, self.column,
                                                             #f['{}/row_column'.format(self.dataset_name)][new_idx]))
        f.close()
    self.vmin_spot_val = int(self.vmin_spot_tb.text)
    self.vmax_spot_val = int(self.vmax_spot_tb.text)
    self.vmin_sum_val = int(self.vmin_sum_tb.text)
    self.vmax_sum_val = int(self.vmax_sum_tb.text)

    try:
        summed_dif = np.sum(self.results[:, 1], axis = 0)
        self.summed_dif_ax.imshow(summed_dif, vmin = self.vmin_sum_val, vmax = self.vmax_sum_val)
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
    make_red(self)
    self.med_blur_dis_val = int(self.med_blur_dis_tb.text)
    self.med_blur_h_val = int(self.med_blur_h_tb.text)
    self.stdev_val = float(self.stdev_tb.text)
    self.bkgx_val = float(self.multiplier_tb.text)
    load_dynamic_data(self.results, self.vmin_spot_val, self.vmax_spot_val,
                      self.spot_diff_ax, self.ttheta_centroid_ax, self.chi_centroid_ax,
                      self.med_blur_dis_val, self.med_blur_h_val, self.stdev_val,
                      self.row, self.column, self)



class FiguresClass():
    pass

def make_red(self):
    axes = [self.ttheta_map_ax, self.chi_map_ax,
            self.reprocessbtn_ax]
    sides = ['left', 'right', 'top', 'bottom']
    for ax in axes:
        for side in sides:
            ax.spines[side].set_color('red')
    plt.draw() 

def make_pink(self):
    axes = [self.ttheta_map_ax, self.chi_map_ax,
            self.savingbtn_ax, self.med_blur_dis_ax,
            self.med_blur_h_ax, self.stdev_ax,
            self.multiplier_ax]
    sides = ['left', 'right', 'top', 'bottom']
    for ax in axes:
        for side in sides:
            ax.spines[side].set_color('fuchsia')
    for side in sides:
        self.reprocessbtn_ax.spines[side].set_color('black')
    plt.draw()

def make_black(self):
    axes = [self.ttheta_map_ax, self.chi_map_ax,
            self.reprocessbtn_ax, self.savingbtn_ax,self.med_blur_dis_ax,
            self.med_blur_h_ax, self.stdev_ax,
            self.multiplier_ax]
    sides = ['left', 'right', 'top', 'bottom']
    for ax in axes:
        for side in sides:
            ax.spines[side].set_color('black')
    plt.draw() 


def viewer_mouse_click(event, self):
    if self.viewer_currentax in [self.fluor_ax, self.roi_ax] and self.viewer_currentax != None:
        self.row = int(np.floor(event.ydata))
        self.column = int(np.floor(event.xdata))
        try:
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
        self.fluor_ax.axvline(x = self.column, color = 'w', linewidth = 1)
        self.fluor_ax.axhline(y = self.row, color = 'w', linewidth = 1)

        self.roi_ax.axvline(x = self.column, color = 'w', linewidth = 1)
        self.roi_ax.axhline(y = self.row, color = 'w', linewidth = 1)

        self.ttheta_map_ax.axvline(x = self.column, color = 'r', linewidth = 0.5)
        self.ttheta_map_ax.axhline(y = self.row, color = 'r', linewidth = 0.5)

        self.chi_map_ax.axvline(x = self.column, color = 'r', linewidth = 0.5)
        self.chi_map_ax.axhline(y = self.row, color = 'r', linewidth = 0.5)

        load_dynamic_data(self.results, self.vmin_spot_val, self.vmax_spot_val, self.spot_diff_ax,
                              self.ttheta_centroid_ax, self.chi_centroid_ax, self.med_blur_dis_val,
                              self.med_blur_h_val, self.stdev_val, self.row, self.column, self)

        plt.draw()
    else:
        pass


def reprocessbtn_click(event,user_class, figure_class):
    make_pink(figure_class)
    user_class.analysis(user_class.analysis_total_rows,
                        user_class.analysis_total_columns,
                        med_blur_distance = figure_class.med_blur_dis_val,
                        med_blur_height = figure_class.med_blur_h_val,
                        stdev_min = figure_class.stdev_val,
                        bkg_multiplier = figure_class.bkgx_val)
    #Set Attrs For reprocessbtn

def savingbtn_click(event, user_class, figure_class):
    make_black(figure_class)
    user_class.save()
    reload_some_static_data(user_class.results, figure_class.roi_ax,
                            figure_class.ttheta_map_ax, figure_class.chi_map_ax)

    

