import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.widgets import Button, TextBox, Slider
import warnings

from roi_bounding import ROI_FiguresClass
from mis import create_rois, results_2dsum#, median_blur
from roi_bounding import *
from postprocess import twodsummed

from functools import partial

import config

def create_bounding_box_rois(fs):
    main_roi = create_rois(fs)
    return main_roi[1]


def create_total_linescan(fs):
    main_roi = create_rois(fs)
    linescan_store = []
    for roi1 in main_roi[0]:
        linescan_store.append(np.nansum(roi1))
    return linescan_store


def start_scan_roi(user_class):
    """Displays the scan roi figure with appropriate settings

    Parameters
    ==========
    user_class (SXDMFrameset)
        the sxdmframeset object

    Returns
    =======
    Nothing
    """

    # close all figures to stop errors from happening
    plt.close('all')

    # setup the figure clas
    scan_roi = ROI_FiguresClass()
    scan_roi_figure_setup(figure_class=scan_roi)
    textbox_setup(figure_class=scan_roi)
    scan_slider_setup(figure_class=scan_roi, user_class=user_class)
    grab_int_v_scan(user_class=user_class)
    top_plot_start(scan_roi, user_class)


    display_right_roi(figure_class=scan_roi, im=right_roi(user_class, types='scan'))
    display_left_roi(figure_class=scan_roi, user_class=user_class, types='scan')

    # setup event functions
    p_top_plot_reload = partial(top_plot_reload, figure_class=scan_roi, user_class=user_class, types='scan')
    p_display_left_roi_reload = partial(display_left_roi_reload, figure_class=scan_roi, user_class=user_class, types='scan')
    p_display_right_roi_reload = partial(display_right_roi_reload, figure_class=scan_roi, im=np.sum(user_class.ordered_scan_roi, axis=0))


    user_class.scan_slider.on_changed(p_top_plot_reload)
    user_class.scan_slider.on_changed(p_display_left_roi_reload)


    scan_roi.vmin_scan_tb.on_submit(p_display_left_roi_reload)
    scan_roi.vmax_scan_tb.on_submit(p_display_left_roi_reload)


    scan_roi.vmin_sum_tb.on_submit(p_display_right_roi_reload)
    scan_roi.vmax_sum_tb.on_submit(p_display_right_roi_reload)

    p_on_scan_click = partial(on_scan_click, figure_class=scan_roi, user_class=user_class, types='scan')


    scan_roi.fig.canvas.mpl_connect('button_press_event', p_on_scan_click)


def on_scan_click(event, figure_class, user_class, types='scan'):
    """Obtains all the raw scan data for a user clicked pixel

    Parameters
    ==========
    event (matplotlib event)
        the matplotlib event
    figure_class (ROI_FiguresClass)
        the roi_figuresclass object
    user_class (SXDMFrameset)
        the sxdmframeset object
    types (str)
        either 'scan' or 'bounding'

    Returns
    =======
    Nothing - obtains all data and diplays data to appropriate location
    """

    median_blur = config.median_blur
    
    if not event.dblclick:
        ax = event.inaxes
        cont = True
        begin = 0
        med_dis = int(figure_class.med_blur_dis_tb.text)
        med_h = int(figure_class.med_blur_h_tb.text)

        # make sure that the click was in the right axis
        if ax == figure_class.scan_roi_ax:
            figure_class.user_click_x = int(np.ceil(event.xdata))
            figure_class.user_click_y = int(np.ceil(event.ydata))

            # set the index value based on the results
            idx = 0

            # try to find the pixel location
            while cont == True:
                results = user_class.roi_results
                try:
                    x, y = results[begin][idx]
                except Exception as ex:
                    print('roi.py/on_scan_click', ex)
                    fail_safe = input('Loop Error')

                # plot it in the correct location
                if y == figure_class.user_click_x and x == figure_class.user_click_y:
                    figure_class.scan_med_data_ax.cla()
                    figure_class.scan_med_data_ax.set_title('Row {} Column {}'.format(x, y))

                    data = []
                    if types == 'scan':
                        new_idx = 2
                    elif types == 'bounding':
                        new_idx = 5
                    for array in results[begin][new_idx]:
                        a = array.copy()
                        data.append(median_blur(a, med_dis, med_h, with_low=True))

                    for ar in data:
                        figure_class.scan_med_data_ax.plot(ar)

                    cont = False
                    plt.draw()

                else:
                    begin = begin + 1


def initiate_roi_viewer(user_class):
    """Sets up all the ROI viewer figures

    Parameters
    ==========
    user_class (SXDMFrameset)
        the sxdmframeset object

    Returns
    =======
    Nothing
    """
    start_scan_roi(user_class=user_class)
    start_bounding_roi(user_class=user_class)


def start_bounding_roi(user_class):
    """Displays the bounding box roi with aproptiate textboxes

    Parameters
    ==========
    user_class (SXDMFrameset)
        the sxdmframeset object

    Returns
    =======
    Nothing
    """
    bounding_roi = ROI_FiguresClass()
    bounding_roi_figure_setup(figure_class=bounding_roi)
    textbox_setup(figure_class=bounding_roi)
    bounding_slider_setup(figure_class=bounding_roi, user_class=user_class)
    grab_int_v_scan(user_class=user_class, types='bounding')
    top_plot_start(bounding_roi, user_class, types='bounding')

    display_right_roi(figure_class=bounding_roi, im=right_roi(user_class, types='bounding'))
    display_left_roi(figure_class=bounding_roi, user_class=user_class, types='bounding')

    try:
        user_class.roi_sum_im = user_class.dif_im #results_2dsum(user_class)
    except:
        user_class.roi_sum_im = user_class.dif_im

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


    p_display_left_roi_reload = partial(display_left_roi_reload, figure_class=bounding_roi, user_class=user_class, types='bounding')
    p_display_right_roi_reload = partial(display_right_roi_reload, figure_class=bounding_roi, im=np.sum(user_class.ordered_bounding_roi, axis=0))

    bounding_roi.vmin_scan_tb.on_submit(p_display_left_roi_reload)
    bounding_roi.vmax_scan_tb.on_submit(p_display_left_roi_reload)


    bounding_roi.vmin_sum_tb.on_submit(p_display_right_roi_reload)
    bounding_roi.vmax_sum_tb.on_submit(p_display_right_roi_reload)





    p_on_scan_click2 = partial(on_scan_click, figure_class=bounding_roi, user_class=user_class, types='bounding')
    bounding_roi.fig.canvas.mpl_connect('button_press_event', p_on_scan_click2)

    sum_fig.closebtn.on_clicked(close_all)

def scan_roi_figure_setup(figure_class):
    """Initiates the scan roi figure with proper axes locations current_roi_slider_val

    Parameters
    ==========
    figure_class (ROI_FiguresClass)
        the roi_figuresclass object

    Returns
    =======
    Nothing
    """
    fig = plt.figure(figsize=(5.5, 10))
    figure_class.fig = fig
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
    figure_class.med_blur_h_ax = plt.axes([0.05, 0.05, 0.10, 0.05])
    figure_class.med_blur_h_ax.set_xticks([])
    figure_class.med_blur_h_ax.set_yticks([])
    figure_class.med_blur_h_ax.set_title('blur height', fontsize=8)

    # medblur distance
    figure_class.med_blur_dis_ax = plt.axes([0.05, 0.15, 0.08, 0.05])
    figure_class.med_blur_dis_ax.set_xticks([])
    figure_class.med_blur_dis_ax.set_yticks([])
    figure_class.med_blur_dis_ax.set_title('blur distance', fontsize=8)

    plt.draw()

def bounding_roi_figure_setup(figure_class):
    """Initiates the bounding box figure with axes

    Parameters
    ==========
    figure_class (ROI_FiguresClass)
        the roi_figuresclass object

    Returns
    =======
    Nothing
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
    figure_class.med_blur_h_ax = plt.axes([0.05, 0.05, 0.10, 0.05])
    figure_class.med_blur_h_ax.set_xticks([])
    figure_class.med_blur_h_ax.set_yticks([])
    figure_class.med_blur_h_ax.set_title('blur height', fontsize=8)

    # medblur distance
    figure_class.med_blur_dis_ax = plt.axes([0.05, 0.15, 0.08, 0.05])
    figure_class.med_blur_dis_ax.set_xticks([])
    figure_class.med_blur_dis_ax.set_yticks([])
    figure_class.med_blur_dis_ax.set_title('blur distance', fontsize=8)

    plt.draw()


def textbox_setup(figure_class):
    """Sets up textboxes for the scan roi and the bounding box roi figures

    Parameters
    ==========
    figure_class (ROI_FiguresClass)
        the roi_figuresclass object

    Returns
    =======
    Nothing
    """
    figure_class.vmin_scan_tb = TextBox(figure_class.vmin_scan_ax, '', initial='0')
    figure_class.vmax_scan_tb = TextBox(figure_class.vmax_scan_ax, '', initial='1000')

    figure_class.vmin_sum_tb = TextBox(figure_class.vmin_sum_ax, '', initial='0')
    figure_class.vmax_sum_tb = TextBox(figure_class.vmax_sum_ax, '', initial='1000')

    figure_class.med_blur_dis_tb = TextBox(figure_class.med_blur_dis_ax, '', initial='5')
    #figure_class.med_blur_h_tb = TextBox(figure_class.med_blur_h_ax, '', initial='100')

    if config.algorithm != 'selective':

        figure_class.med_blur_h_tb = TextBox(figure_class.med_blur_h_ax, '', initial='100', color='red')
        #med_blur_h_tb = TextBox(med_blur_h_ax, 'med_h', initial=med_blur_hei, color='red')
        warnings.warn('User In --{}-- Mode. Use --selective-- Mode For Median_Blur_Height Access.'.format(config.algorithm))

    else:
        figure_class.med_blur_h_tb = TextBox(figure_class.med_blur_h_ax, '', initial='100')
        #med_blur_h_tb = TextBox(med_blur_h_ax, 'med_h', initial=med_blur_hei)

def scan_slider_setup(figure_class, user_class):
    """Sets up the scan figure slider inside the roi figures

    Parameters
    ==========
    figure_class (ROI_FiguresClass)
        the roi_figuresclass object
    user_class (SXDMFrameset)
        the sxdmframeset object

    Returns
    =======
    Nothing
    """
    amount = len(user_class.scan_theta) - 1
    if amount == 0:
        amount = 0.1
    sld1 = Slider(ax=figure_class.scan_slider_ax, label='Scan', valmin=0, valmax=amount, valinit=0, valstep=1)
    plt.draw()
    user_class.scan_slider = sld1


def bounding_slider_setup(figure_class, user_class):
    """Sets up the bounding figure slider inside the roi figures

    Parameters
    ==========
    figure_class (ROI_FiguresClass)
        the roi_figuresclass object
    user_class (SXDMFrameset)
        the sxdmframeset object

    Returns
    =======
    Nothing
    """
    amount = len(user_class.diff_segment_squares) - 1
    if amount == 0:
        amount = 0.1
    sld2 = Slider(figure_class.scan_slider_ax, 'Box', 0, amount, valinit=0, valstep=1)
    plt.draw()
    user_class.bounding_slider = sld2


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


def close_all(event):
    plt.close('all')


def display_summed_ims(figure_class, user_class):
    """Show the summed diffraction pattern with all assigned bounding boxes

    Parameters
    ==========
    figure_class: (ROI_FigureClass)
        the roi_figureclass object
    user_class: (SXDMFrameset)
        the sxdmframeset object

    Returns
    =======
    Nothing - displays the summed diffraction pattern along with the User selected bounding boxes
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
    """Allows the summed diffraction images to be displayed

    Parameters
    ==========
    val: (matplotlib val)
        matplotlib variable
    figure_class: (ROI_FigureClass)
        the roifigureclass object
    user_class: (SXDMFrameset)
        the sxdmframeset object

    Return
    ======
    Nothing - reloads the summed diffraction images in the figure
    """
    display_summed_ims(figure_class=figure_class, user_class=user_class)


def bounding_box_total_setup(user_class):
    """Complete setup of the summed diffraction pattern with the bounding boxes on top of them

    Parameters
    ==========
    user_class: (SXDMFrameset)
        the sxdmframeset object

    Returns
    =======
    Nothing - sets up all the bounding box figures and loads all items
    """
    user_class.roi_sum_im = results_2dsum(user_class)
    sum_fig = ROI_FiguresClass()
    bounding_box_setup(sum_fig)
    bounding_tb_setup(sum_fig)
    display_summed_ims(sum_fig, user_class)


def top_plot_start(figure_class, user_class, types='scan'):
    """Initiate the gaus plot

    Parameters
    ==========
    figure_class: (ROI_FigureClass)
        the roi_figureclass object
    user_class: (SXDMFrameset)
        the sxdmframeset object
    types: (str)
        either 'scan' or 'bounding' allow the User to choose which figure they are working on

    Returns
    =======
    Nothing
    """
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
    """Reloads the gaus plot

    Parameters
    ==========
    val: (matplotlib val)
        the value for matplot lib events
    figure_class: (ROIFigure_Class)
        the roifigure_class objects
    user_class: (SXDMFrameset)
        the sxdmframeset object
    types: (str)
        either 'scan' or 'bounding' - determines which plots need to be reloaded

    Returns
    =======
    Nothing - reloads the top plot in the roi figures
    """
    top_plot_start(figure_class=figure_class, user_class=user_class, types=types)


def grab_int_v_scan(user_class, types='scan'):
    """Grab the data needed for the gaus plot

    Parameters
    ==========
    user_class: (SXDMFrameset)
        the sxdmframeset object
    types: (str)
        either 'scan' or 'bounding' - determines which plots the User would like to get information for

    Returns
    =======
    Nothing - sets up the x and y values for the top plot of either the Scan ROI or the Bounding Box ROI
    """

    # Return the ROI data for each scan
    output = create_rois(user_class)

    y_values_scan = create_total_linescan(user_class)

    # If we are looking at the scans as a whole
    if types == 'scan':
        # Grab the scan thetas
        theta = np.asarray(user_class.scan_theta)

        # Get their indexes when they are in order
        inds = theta.argsort()

        # Make sure data isn't overwritten
        copy_theta = theta.copy()

        # Get the corrected scan theta order
        user_class.ordered_scan_theta = copy_theta[inds]
        user_class.scan_theta_inds = inds

        # Make sure data isn't overwritten
        copy_output = output[0].copy()

        # Place the scan ROI's in the same order
        user_class.ordered_scan_roi = []
        user_class.ordered_scan_roi = copy_output[inds]
        x = theta[inds]

        # Add the ROI's together
        pre_y = add_rois(output, types='scan')

        # Make sure the summed values are in order
        y = y_values_scan

        # Save the data so it can be called later
        user_class.scan_top_x = x.copy()
        user_class.scan_top_y = np.nan_to_num(y).copy()


    elif types == 'bounding':
        # Determine how many bounding boxes there are
        x = np.arange(0, len(output[1]))

        # Add up all the bounding box data
        y = add_rois(output, types='bounding')

        # Store their data so it can be called later
        user_class.ordered_bounding_roi = output[1].copy()
        user_class.bounding_top_x = x
        user_class.bounding_top_y = np.nan_to_num(y)


def add_rois(rois, types='scan'):
    """Add the create_rois output and return the correct plots

    Parameters
    ==========
    rois: (nd.array)
        the rois the user would like to add together
    types: (str)
        either 'scan' or 'bounding' - depends on what roi's the User sets for the rois variable

    Returns
    =======
    1d.array of the roi's summed
    """
    summed = []

    # Get the right roi location based on User types input
    if types == 'scan':
        master_roi = rois[0]
    elif types == 'bounding':
        master_roi = rois[1]

    # For each roi sum the value and store it
    for array in master_roi:
        ar = array.copy()
        s = np.nansum(ar)
        c = np.count_nonzero(np.isnan(ar)) * np.nanmedian(ar)
        summed.append(s)

    # Return the stored array
    return np.asarray(summed)


def right_roi(user_class, types='scan'):
    """Plots the right roi plot

    Parameters
    ==========
    user_class: (SXDMFrameset)
        the sxdmframeset object
    types: (str)
        either 'scan' or 'bounding' - depends on which figure is being called

    Returns
    =======
    The entire summed region of interest for either the scans or the bounding boxes
    """

    # Obtain the ROI's
    output = create_rois(user_class)
    output = np.asarray(output)
    output2 = output.copy()

    # Return the right axis
    if types == 'scan':
        return np.nansum(output2[0], axis=0)
    elif types == 'bounding':
        return np.nansum(output2[1], axis=0)


def display_right_roi(figure_class, im):
    """Displays the right roi plot

    Parameters
    ==========
    figure_class: (ROI_FigureClass)
        the roi_figureclass object
    im: (nd.array)
        the image array to be displayed

    Returns
    =======
    Nothing - displays the right roi image
    """
    # Obtain the vmin and vmax values for the imshow function
    vmin = int(figure_class.vmin_sum_tb.text)
    vmax = int(figure_class.vmax_sum_tb.text)

    # Display the image
    figure_class.summed_roi_ax.imshow(im, vmin=vmin, vmax=vmax)

def display_right_roi_reload(val, figure_class, im):
    """Load the Right ROI data

    Parameters
    ==========
    val: (matplotlib event)
        the val matplotlib event
    figure_class: (ROI_FigureClass)
        the roi_figureclass object
    im: (nd.array)
        the image to be displayed

    Returns
    =======
    Nothing - reloads the right figure data
    """
    display_right_roi(figure_class=figure_class, im=im)


def display_left_roi(figure_class, user_class, types='scan'):
    """Sets up the display for the left roi plot

    Parameters
    ==========
    figure_class: (ROI_FigureClass)
        the roi_figureclass object
    user_class: (SXDMFrameset)
        the sxdmframeset object
    types: (str)
        either 'scan' or 'bounding'

    Returns
    =======
    Nothing - displays the left roi figure
    """
    # Clear the axis
    figure_class.scan_roi_ax.cla()

    # Grab the vmin and vmax values
    vmin = int(figure_class.vmin_scan_tb.text)
    vmax = int(figure_class.vmax_scan_tb.text)

    # Grab the correct image to be displayed
    if types == 'scan':
        im = user_class.ordered_scan_roi
        idx = int(user_class.scan_slider.val)

    elif types == 'bounding':
        im = user_class.ordered_bounding_roi
        idx = int(user_class.bounding_slider.val)

    # Display the image
    figure_class.scan_roi_ax.imshow(im[idx], vmin=vmin, vmax=vmax)


def display_left_roi_reload(val, figure_class, user_class, types='scan'):
    """Reloads the left roi

    Parameters
    ==========
    val: (matplotlib event)
        the val matplotlib event
    figure_class: (ROI_FigureClass)
        the roi_figureclass object
    user_class: (SXDMFrameset)
        the sxdmframeset object
    types: (str)
        either 'scan' or 'bounding'

    Returns
    =======
    Nothing - reloads the left image
    """
    display_left_roi(figure_class=figure_class, user_class=user_class, types=types)

