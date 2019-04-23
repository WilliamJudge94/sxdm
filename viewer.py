import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, TextBox
import imageio
from pathlib import Path
import os
import sys

from postprocess import pixel_analysis_return
from mis import  median_blur, centering_det
from postprocess import centroid_roi_map, pooled_return
from pixel import theta_maths, chi_maths

def figure_setup():

    fig = plt.figure(figsize = (8,4))

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
                       label = 'Save',
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
    med_blur_dis_tb = TextBox(med_blur_dis_ax, 'med_dis', initial='4')
    med_blur_h_tb = TextBox(med_blur_h_ax, 'med_h', initial='10')
    stdev_tb = TextBox(stdev_ax, 'stdev_min', initial='35')
    multiplier_tb = TextBox(multiplier_ax, 'bkgx', initial='1')
    plt.draw()

    return vmin_spot_tb, vmax_spot_tb, vmin_sum_tb, vmax_sum_tb,\
           med_blur_dis_tb, med_blur_h_tb, stdev_tb, multiplier_tb

def load_static_data(results, vmin_sum, vmax_sum, fluor_ax, roi_ax,
                     summed_dif_ax, ttheta_map_ax, chi_map_ax):

    roi_im = centroid_roi_map(results, 'full_roi')
    chi_centroid = centroid_roi_map(results, 'chi_centroid')
    ttheta_centroid = centroid_roi_map(results, 'ttheta_centroid')
    #fluor_im = centering_det(self, group='fluor', summed=True)

    try:
        summed_dif = np.sum(stored[:, 1], axis = 0)
        summed_dif_ax.imshow(summed_dif, vmin = vmin_sum, vmax = vmax_sum)
    except:
        summed_dif_ax.imshow(sum_error())
        summed_dif_ax.set_xticks = []
        summed_dif_ax.set_yticks = []

    ttheta_map_ax.imshow(ttheta_centroid)
    chi_map_ax.imshow(chi_centroid)
    roi_ax.imshow(roi_im)
    fluor_ax.imshow(roi_im)


def load_dynamic_data(results, vmin_spot, vmax_spot, spot_dif_ax,
                      ttheta_centroid_ax, chi_centroid_ax, med_blur_distance,
                      med_blur_height, stdev_min, row, column):

    spot_dif_ax.cla()
    ttheta_centroid_ax.cla()
    chi_centroid_ax.cla()

    return_dic = pixel_analysis_return(results, row, column)

    spot_dif = return_dic['summed_dif']
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





