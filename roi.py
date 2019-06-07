
# scan_roi
# Top plot of the gaussian check
# bottom left have a way to flick through the rois
# bottom right summed roi
# be able to click on the scan_roi and pull up the median_blur_data for it
# show the median_blur_data

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.widgets import Button, TextBox, Slider

from roi_bounding import ROI_FiguresClass
from mis import create_rois, results_2dsum
from roi_bounding import *
from postprocess import twodsummed

from functools import partial

def pre_figures(self):
    """WIP

    :param self:
    :return:
    """
    main_results = self.results

    #summed_dif_pattern = twodsummed(main_results)

    out = start_figure(summed_dif_pattern, self)

    #roi_results = self.roi_results

    #readable_roi_results = create_rois(roi_results)

    return out


def start_scan_roi(user_class):
    """Displays the scan roi figure with appropriate textboxes

    :return:
    """
    scan_roi = ROI_FiguresClass()
    scan_roi_figure_setup(figure_class=scan_roi)
    textbox_setup(figure_class=scan_roi)
    scan_slider_setup(figure_class=scan_roi, user_class=user_class)
    grab_int_v_scan(user_class=user_class)

    top_plot_start(scan_roi, user_class)

    display_right_roi(figure_class=scan_roi, im=right_roi(user_class, types='scan'))
    display_left_roi(figure_class=scan_roi, user_class=user_class, types='scan')

    p_top_plot_reload = partial(top_plot_reload, figure_class=scan_roi, user_class=user_class, types='scan')
    p_display_left_roi_reload = partial(display_left_roi_reload, figure_class=scan_roi, user_class=user_class, types='scan')


    user_class.scan_slider.on_changed(p_top_plot_reload)
    user_class.scan_slider.on_changed(p_display_left_roi_reload)



def start_bounding_roi(user_class):
    """Displays the bounding box roi with aproptiate textboxes

    :return:
    """

    bounding_roi = ROI_FiguresClass()
    bounding_roi_figure_setup(figure_class=bounding_roi)
    textbox_setup(figure_class=bounding_roi)
    bounding_slider_setup(figure_class=bounding_roi, user_class=user_class)
    grab_int_v_scan(user_class=user_class, types='bounding')
    top_plot_start(bounding_roi, user_class, types='bounding')

    display_right_roi(figure_class=bounding_roi, im=right_roi(user_class, types='bounding'))
    display_left_roi(figure_class=bounding_roi, user_class=user_class, types='bounding')




    user_class.roi_sum_im = results_2dsum(user_class)
    sum_fig = ROI_FiguresClass()
    bounding_box_setup(sum_fig)
    bounding_tb_setup(sum_fig)
    display_summed_ims(sum_fig, user_class)


    p_top_plot_reload = partial(top_plot_reload, figure_class=bounding_roi, user_class=user_class, types='bounding')
    p_display_left_roi_reload = partial(display_left_roi_reload, figure_class=bounding_roi, user_class=user_class, types='bounding')

    p_display_summed_ims_reload = partial(display_summed_ims_reload, figure_class=sum_fig, user_class=user_class)

    user_class.bounding_slider.on_changed(p_top_plot_reload)
    user_class.bounding_slider.on_changed(p_display_left_roi_reload)

    user_class.bounding_slider.on_changed(p_display_summed_ims_reload)

def scan_roi_figure_setup(figure_class):
    """Initiates the scan roi figure with proper axes locations
current_roi_slider_val
    :param figure_class:
    :return:
    """
    fig = plt.figure(figsize=(5.5, 10))
    mpl.rcParams['axes.linewidth'] = 1.5
    figure_class.fig = fig

    fig.canvas.set_window_title('Scan Region Of Interest')

    # Gaussian
    figure_class.gaus_ax = plt.axes([0.1, 0.75, 0.8, 0.2])
    figure_class.gaus_ax.set_title('Tot. Intensity vs. Scan')
    figure_class.gaus_ax.tick_params(axis="y", labelsize=8)

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
    """Initiates the bounding box figure with axes

    :param figure_class:
    :return:
    """
    fig = plt.figure(figsize=(5, 10))
    mpl.rcParams['axes.linewidth'] = 1.5
    figure_class.fig = fig

    fig.canvas.set_window_title('Bounding Region Of Interest')

    # Gaussian
    figure_class.gaus_ax = plt.axes([0.1, 0.75, 0.8, 0.2])
    figure_class.gaus_ax.set_title('Tot. Intensity vs. Bounding Box #')
    figure_class.gaus_ax.tick_params(axis="y", labelsize=8)

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
    """Sets up textboxes for the scan roi and the bounding box roi figures

    :param figure_class:
    :return:
    """
    figure_class.vmin_scan_tb = TextBox(figure_class.vmin_scan_ax, '', initial='0')
    figure_class.vmax_scan_tb = TextBox(figure_class.vmax_scan_ax, '', initial='1000')

    figure_class.vmin_sum_tb = TextBox(figure_class.vmin_sum_ax, '', initial='0')
    figure_class.vmax_sum_tb = TextBox(figure_class.vmax_sum_ax, '', initial='1000')

    figure_class.med_blur_dis_tb = TextBox(figure_class.med_blur_dis_ax, '', initial='5')
    figure_class.med_blur_h_tb = TextBox(figure_class.med_blur_h_ax, '', initial='100')

def scan_slider_setup(figure_class, user_class):
    amount = len(user_class.scan_theta) - 1
    sld1 = Slider(figure_class.scan_slider_ax, 'Scan', 0, amount, valinit=0, valstep=1)
    plt.draw()
    user_class.scan_slider = sld1


def bounding_slider_setup(figure_class, user_class):
    amount = len(user_class.diff_segment_squares) - 1
    sld2 = Slider(figure_class.scan_slider_ax, 'Box', 0, amount, valinit=0, valstep=1)
    plt.draw()
    user_class.bounding_slider = sld2

# bounding_roi
## there are different boxes the user can select and see their roi maps and their summed roi colormap
# left side had a figure where the user selects roi boxes
# create a way to flick through all the boxes roi individually
# right summing all the roi boxes as difference colors
# bottom plot show the gaussian curve for the current selected bounding ox the user is viewing (center)
# show the median_blur_data depending where the user clicks and which scan they click


def bounding_box_setup(figure_class):
    """Set up the viewer figure for what bounding boxes have been selected

    Parameters
    ==========
    figure_class (ROI_FigureClass)
        the roi_figureclass object
    Returns
    =======
    Nothing - sets figure_class.axes
    """

    fig = plt.figure(figsize=(8, 3))
    mpl.rcParams['axes.linewidth'] = 1.5
    figure_class.fig = fig

    fig.canvas.set_window_title('Bounding Boxes')

    # Initiate the axes
    figure_class.summed_dif_ax1 = plt.axes([0.05, 0.15, 0.35, 0.7])
    figure_class.summed_dif_ax1.set_xticks([])
    figure_class.summed_dif_ax1.set_yticks([])

    # Initiate the axes
    figure_class.summed_dif_ax2 = plt.axes([0.45, 0.15, 0.35, 0.7])
    figure_class.summed_dif_ax2.set_xticks([])
    figure_class.summed_dif_ax2.set_yticks([])


    figure_class.vmin_ax = plt.axes([0.85, 0.80, 0.1, 0.05])
    figure_class.vmin_ax.set_xticks([])
    figure_class.vmin_ax.set_yticks([])

    figure_class.vmax_ax = plt.axes([0.85, 0.70, 0.1, 0.05])
    figure_class.vmax_ax.set_xticks([])
    figure_class.vmax_ax.set_yticks([])


    figure_class.closebtn_ax = plt.axes([0.835, 0.15, 0.13, 0.05])
    figure_class.closebtn_ax.set_xticks([])
    figure_class.closebtn_ax.set_yticks([])

    plt.draw()

def bounding_tb_setup(figure_class):
    """Sets up all the textboxes and buttons

    Parameters
    ==========
    figure_class (ROI_FigureClass)
        the roi_figureclass object

    Returns
    =======
    Nothing
    """
    figure_class.vmin_tb = TextBox(figure_class.vmin_ax, 'vmin', initial='0')
    figure_class.vmax_tb = TextBox(figure_class.vmax_ax, 'vmax', initial='1000')


    figure_class.closebtn = Button(ax=figure_class.closebtn_ax,
                           label='Close All',
                           color='teal',
                           hovercolor='tomato')
    plt.draw()

def display_summed_ims(figure_class, user_class):
    """Show the summed diffraction pattern with all assigned bounding boxes

    :param figure_class:
    :param user_class:
    :return:
    """

    rect = user_class.diff_segment_squares
    im = user_class.roi_sum_im
    vmin = int(figure_class.vmin_tb.text)
    vmax = int(figure_class.vmax_tb.text)


    figure_class.summed_dif_ax1.cla()
    figure_class.summed_dif_ax2.cla()


    figure_class.summed_dif_ax1.imshow(im, vmin=vmin, vmax=vmax)
    figure_class.summed_dif_ax2.imshow(im, vmin=vmin, vmax=vmax)


    try:
        for i, r in enumerate(rect):
            x1 = r[0]
            x2 = r[1]
            y1 = r[2]
            y2 = r[3]

            rect1 = plt.Rectangle((min(x1, x2), min(y1, y2)), np.abs(x1 - x2), np.abs(y1 - y2),
                                 fill=False, color='w')
            figure_class.summed_dif_ax1.add_patch(rect1)

            if i == user_class.current_roi_slider_val:

                rect2 = plt.Rectangle((min(x1, x2), min(y1, y2)), np.abs(x1 - x2), np.abs(y1 - y2),
                                 fill=False, color='w')
                figure_class.summed_dif_ax2.add_patch(rect2)

    except Exception as ex:
        print(ex)
        pass

    plt.draw()

def display_summed_ims_reload(val, figure_class, user_class):
    display_summed_ims(figure_class=figure_class, user_class=user_class)

def bounding_box_total_setup(user_class):
    """Complete setup of the summed diffraction pattern with the bounding boxes on top of them

    :param user_class:
    :return:
    """
    user_class.roi_sum_im = results_2dsum(user_class)
    sum_fig = ROI_FiguresClass()
    bounding_box_setup(sum_fig)
    bounding_tb_setup(sum_fig)
    display_summed_ims(sum_fig, user_class)

def top_plot_start(figure_class, user_class, types='scan'):
    figure_class.gaus_ax.cla()

    if types == 'scan':
        vlin = int(user_class.scan_slider.val)
        figure_class.gaus_ax.plot(user_class.scan_top_x, user_class.scan_top_y)
        try:
            figure_class.gaus_ax.axvline(x=user_class.ordered_scan_theta[vlin])
            figure_class.gaus_ax.set_title('Int. vs Scan Theta ({} deg)'.format(np.round(user_class.ordered_scan_theta[vlin], 2)))
        except:
            pass
    elif types == 'bounding':
        vlin = int(user_class.bounding_slider.val)
        user_class.current_roi_slider_val = vlin
        figure_class.gaus_ax.plot(user_class.bounding_top_x, user_class.bounding_top_y)
        figure_class.gaus_ax.set_title(
            'Int. vs Bounding Box (box {})'.format(int(vlin)))
        try:
            figure_class.gaus_ax.axvline(x=vlin)
        except:
            pass

def top_plot_reload(val, figure_class, user_class, types='scan'):
    top_plot_start(figure_class=figure_class, user_class=user_class, types=types)

def grab_int_v_scan(user_class, types='scan'):
    output = create_rois(user_class)

    if types == 'scan':
        theta = np.asarray(user_class.scan_theta)
        inds = theta.argsort()
        copy_theta = theta.copy()

        user_class.ordered_scan_theta = copy_theta[inds]
        user_class.scan_theta_inds = inds

        copy_output = output[0].copy()

        user_class.ordered_scan_roi = []
        user_class.ordered_scan_roi = copy_output[inds]
        x = theta[inds]

        pre_y = add_rois(output, types='scan')

        y = pre_y[inds]
        user_class.scan_top_x = x.copy()
        user_class.scan_top_y = np.nan_to_num(y).copy()


    elif types == 'bounding':
        x = np.arange(0, len(output[1]))
        y = add_rois(output, types='bounding')
        user_class.ordered_bounding_roi = output[1].copy()
        user_class.bounding_top_x = x
        user_class.bounding_top_y = np.nan_to_num(y)

def add_rois(rois, types='scan'):
    summed = []

    if types == 'scan':
        master_roi = rois[0]
    elif types == 'bounding':
        master_roi = rois[1]

    for array in master_roi:
        ar = array.copy()
        s = np.nansum(ar)
        c = np.count_nonzero(np.isnan(ar)) * np.nanmedian(ar)
        summed.append(s)

    return np.asarray(summed)

def right_roi(user_class, types='scan'):
    output = create_rois(user_class)
    output = np.asarray(output)
    output2 = output.copy()
    if types == 'scan':
        return np.nansum(output2[0], axis=0)
    elif types == 'bounding':
        return np.nansum(output2[1], axis=0)

def display_right_roi(figure_class, im):
    figure_class.summed_roi_ax.imshow(im)

def display_left_roi(figure_class, user_class, types='scan'):

    figure_class.scan_roi_ax.cla()
    vmin = int(figure_class.vmin_scan_tb.text)
    vmax = int(figure_class.vmax_scan_tb.text)
    if types == 'scan':
        im = user_class.ordered_scan_roi
        idx = int(user_class.scan_slider.val)

    elif types == 'bounding':
        im = user_class.ordered_bounding_roi
        idx = int(user_class.bounding_slider.val)

    figure_class.scan_roi_ax.imshow(im[idx], vmin=vmin, vmax=vmax)

def display_left_roi_reload(val, figure_class, user_class, types='scan'):
    display_left_roi(figure_class=figure_class, user_class=user_class, types=types)

