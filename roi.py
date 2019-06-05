
# scan_roi
# Top plot of the gaussian check
# bottom left have a way to flick through the rois
# bottom right summed roi
# be able to click on the scan_roi and pull up the median_blur_data for it
# show the median_blur_data

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.widgets import Button, TextBox

from roi_bounding import ROI_FiguresClass

def start_scan_roi():
    scan_roi = ROI_FiguresClass()
    scan_roi_figure_setup(figure_class=scan_roi)
    textbox_setup(figure_class=scan_roi)


def start_bounding_roi():
    bounding_roi = ROI_FiguresClass()
    bounding_roi_figure_setup(figure_class=bounding_roi)
    textbox_setup(figure_class=bounding_roi)


def scan_roi_figure_setup(figure_class):
    fig = plt.figure(figsize=(5, 10))
    mpl.rcParams['axes.linewidth'] = 1.5
    figure_class.fig = fig

    fig.canvas.set_window_title('Scan Region Of Interest')

    # Gaussian
    figure_class.gaus_ax = plt.axes([0.1, 0.75, 0.8, 0.2])
    figure_class.gaus_ax.set_title('Tot. Intensity vs. Scan')

    # scan roi
    figure_class.scan_roi_ax = plt.axes([0.1, 0.30, 0.3, 0.3])
    figure_class.scan_roi_ax.set_xticks([])
    figure_class.scan_roi_ax.set_yticks([])

    # scan roi slider
    figure_class.scan_slider_ax = plt.axes([0.1, 0.65, 0.8, 0.05])
    figure_class.scan_slider_ax.set_xticks([])
    figure_class.scan_slider_ax.set_yticks([])

    # summed roi
    figure_class.summed_roi_ax = plt.axes([0.6, 0.30, 0.3, 0.3])
    figure_class.summed_roi_ax.set_xticks([])
    figure_class.summed_roi_ax.set_yticks([])

    # med blur data
    figure_class.scan_med_data_ax = plt.axes([0.2, 0.05, 0.7, 0.2])
    figure_class.scan_med_data_ax.set_xticks([])
    figure_class.scan_med_data_ax.set_yticks([])
    figure_class.scan_med_data_ax.set_title('Pixel Interpretation')

    # vmin scan roi
    figure_class.vmin_scan_ax = plt.axes([0.42, 0.55, 0.13, 0.05])
    figure_class.vmin_scan_ax.set_xticks([])
    figure_class.vmin_scan_ax.set_yticks([])
    figure_class.vmin_scan_ax.set_title('vmin & vmax', fontsize=8)

    # vmax scan roi
    figure_class.vmax_scan_ax = plt.axes([0.42, 0.48, 0.13, 0.05])
    figure_class.vmax_scan_ax.set_xticks([])
    figure_class.vmax_scan_ax.set_yticks([])

    # vmin sum roi
    figure_class.vmin_sum_ax = plt.axes([0.45, 0.37, 0.13, 0.05])
    figure_class.vmin_sum_ax.set_xticks([])
    figure_class.vmin_sum_ax.set_yticks([])
    figure_class.vmin_sum_ax.set_title('vmin & vmax', fontsize=8)

    # vmax sum roi
    figure_class.vmax_sum_ax = plt.axes([0.45, 0.30, 0.13, 0.05])
    figure_class.vmax_sum_ax.set_xticks([])
    figure_class.vmax_sum_ax.set_yticks([])

    # medblur height
    figure_class.med_blur_h_ax = plt.axes([0.05, 0.05, 0.13, 0.05])
    figure_class.med_blur_h_ax.set_xticks([])
    figure_class.med_blur_h_ax.set_yticks([])
    figure_class.med_blur_h_ax.set_title('blur height', fontsize=8)

    # medblur distance
    figure_class.med_blur_dis_ax = plt.axes([0.05, 0.2, 0.13, 0.05])
    figure_class.med_blur_dis_ax.set_xticks([])
    figure_class.med_blur_dis_ax.set_yticks([])
    figure_class.med_blur_dis_ax.set_title('blur distance', fontsize=8)

    plt.draw()

def bounding_roi_figure_setup(figure_class):
    fig = plt.figure(figsize=(5, 10))
    mpl.rcParams['axes.linewidth'] = 1.5
    figure_class.fig = fig

    fig.canvas.set_window_title('Bounding Region Of Interest')

    # Gaussian
    figure_class.gaus_ax = plt.axes([0.1, 0.75, 0.8, 0.2])
    figure_class.gaus_ax.set_title('Tot. Intensity vs. Scan')

    # scan roi
    figure_class.scan_roi_ax = plt.axes([0.1, 0.30, 0.3, 0.3])
    figure_class.scan_roi_ax.set_xticks([])
    figure_class.scan_roi_ax.set_yticks([])

    # scan roi slider
    figure_class.scan_slider_ax = plt.axes([0.1, 0.65, 0.8, 0.05])
    figure_class.scan_slider_ax.set_xticks([])
    figure_class.scan_slider_ax.set_yticks([])

    # summed roi
    figure_class.summed_roi_ax = plt.axes([0.6, 0.30, 0.3, 0.3])
    figure_class.summed_roi_ax.set_xticks([])
    figure_class.summed_roi_ax.set_yticks([])

    # med blur data
    figure_class.scan_med_data_ax = plt.axes([0.2, 0.05, 0.7, 0.2])
    figure_class.scan_med_data_ax.set_xticks([])
    figure_class.scan_med_data_ax.set_yticks([])
    figure_class.scan_med_data_ax.set_title('Pixel Interpretation')

    # vmin scan roi
    figure_class.vmin_scan_ax = plt.axes([0.42, 0.55, 0.13, 0.05])
    figure_class.vmin_scan_ax.set_xticks([])
    figure_class.vmin_scan_ax.set_yticks([])
    figure_class.vmin_scan_ax.set_title('vmin & vmax', fontsize=8)

    # vmax scan roi
    figure_class.vmax_scan_ax = plt.axes([0.42, 0.48, 0.13, 0.05])
    figure_class.vmax_scan_ax.set_xticks([])
    figure_class.vmax_scan_ax.set_yticks([])

    # vmin sum roi
    figure_class.vmin_sum_ax = plt.axes([0.45, 0.37, 0.13, 0.05])
    figure_class.vmin_sum_ax.set_xticks([])
    figure_class.vmin_sum_ax.set_yticks([])
    figure_class.vmin_sum_ax.set_title('vmin & vmax', fontsize=8)

    # vmax sum roi
    figure_class.vmax_sum_ax = plt.axes([0.45, 0.30, 0.13, 0.05])
    figure_class.vmax_sum_ax.set_xticks([])
    figure_class.vmax_sum_ax.set_yticks([])

    # medblur height
    figure_class.med_blur_h_ax = plt.axes([0.05, 0.05, 0.13, 0.05])
    figure_class.med_blur_h_ax.set_xticks([])
    figure_class.med_blur_h_ax.set_yticks([])
    figure_class.med_blur_h_ax.set_title('blur height', fontsize=8)

    # medblur distance
    figure_class.med_blur_dis_ax = plt.axes([0.05, 0.2, 0.13, 0.05])
    figure_class.med_blur_dis_ax.set_xticks([])
    figure_class.med_blur_dis_ax.set_yticks([])
    figure_class.med_blur_dis_ax.set_title('blur distance', fontsize=8)

    plt.draw()


def textbox_setup(figure_class):
    figure_class.vmin_scan_tb = TextBox(figure_class.vmin_scan_ax, '', initial='0')
    figure_class.vmax_scan_tb = TextBox(figure_class.vmax_scan_ax, '', initial='1000')

    figure_class.vmin_sum_tb = TextBox(figure_class.vmin_sum_ax, '', initial='0')
    figure_class.vmax_sum_tb = TextBox(figure_class.vmax_sum_ax, '', initial='1000')

    figure_class.med_blur_dis_tb = TextBox(figure_class.med_blur_dis_ax, '', initial='5')
    figure_class.med_blur_h_tb = TextBox(figure_class.med_blur_h_ax, '', initial='100')
# bounding_roi
## there are different boxes the user can select and see their roi maps and their summed roi colormap
# left side had a figure where the user selects roi boxes
# create a way to flick through all the boxes roi individually
# right summing all the roi boxes as difference colors
# bottom plot show the gaussian curve for the current selected bounding ox the user is viewing (center)
# show the median_blur_data depending where the user clicks and which scan they click


