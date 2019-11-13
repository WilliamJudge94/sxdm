import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.widgets import Button, TextBox, RectangleSelector
import imageio
import numpy as np
from functools import partial


class ROI_FiguresClass():
    """A class function which will make it easier to move variable in and out of functions

    """
    pass


def bounding_figure_setup(figure_class):
    """Set up the viewer figure

    Parameters
    ==========
    figure_class (ROI_FigureClass)
        the roi_figureclass object
    Returns
    =======
    Nothing - sets figure_class.axes
    """

    fig = plt.figure(figsize=(6, 5))
    mpl.rcParams['axes.linewidth'] = 1.5
    figure_class.fig = fig

    # Initiate the axes
    figure_class.summed_dif_ax = plt.axes([0.05, 0.15, 0.7, 0.7])
    figure_class.summed_dif_ax.set_xticks([])
    figure_class.summed_dif_ax.set_yticks([])

    figure_class.vmin_ax = plt.axes([0.85, 0.80, 0.1, 0.05])
    figure_class.vmin_ax.set_xticks([])
    figure_class.vmin_ax.set_yticks([])

    figure_class.vmax_ax = plt.axes([0.85, 0.70, 0.1, 0.05])
    figure_class.vmax_ax.set_xticks([])
    figure_class.vmax_ax.set_yticks([])

    figure_class.rm_box_btn_ax = plt.axes([0.835, 0.44, 0.13, 0.15])
    figure_class.rm_box_btn_ax.set_xticks([])
    figure_class.rm_box_btn_ax.set_yticks([])

    figure_class.contbtn_ax = plt.axes([0.835, 0.15, 0.13, 0.05])
    figure_class.contbtn_ax.set_xticks([])
    figure_class.contbtn_ax.set_yticks([])

    plt.draw()


def textbox_btn_dropdown_setup(figure_class):
    """Sets up all the textboxes and buttons

    Parameters
    ==========
    figure_class (ROI_FigureClass)
        the roi_figureclass object

    Returns
    =======
    Nothing
    """
    # Starting the textboxes
    figure_class.vmin_tb = TextBox(figure_class.vmin_ax, 'vmin', initial='0')
    figure_class.vmax_tb = TextBox(figure_class.vmax_ax, 'vmax', initial='1000')

    # Starting the buttons
    figure_class.rm_box_btn = Button(ax=figure_class.rm_box_btn_ax,
                           label='Remove\nPrevious\nBox',
                           color='teal',
                           hovercolor='tomato')

    figure_class.contbtn = Button(ax=figure_class.contbtn_ax,
                           label='Continue',
                           color='teal',
                           hovercolor='tomato')
    plt.draw()


def line_select_callback(eclick, erelease, figure_class):
    """Creates interactive bounding boxes for roi analysis

    Parameters
    ==========
    eclick (event)
        the click event
    erelease (event)
        the release event
    figure_class (ROI_FigureClass)
        the roi_figureclass object

    Returns
    =======
    Nothing
    """
    # Obtain the User event data
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata

    # Create a rectangle
    rect = plt.Rectangle((min(x1, x2), min(y1, y2)), np.abs(x1-x2), np.abs(y1-y2),
                         fill=False, color='w')
    figure_class.summed_dif_ax.add_patch(rect)

    # Append stored array - if it doesn't exist make it
    try:
        figure_class.pre_roi_bounding.append([x1, x2, y1, y2])
    except:
        figure_class.pre_roi_bounding = ([[x1, x2, y1, y2]])


def start_bounding_box(summed_diff_pattern, user_class):
    """Starts the ROI bounding box GUI

    Returns
    =======
    Nothing
    """

    roi = ROI_FiguresClass()
    bounding_figure_setup(roi)
    textbox_btn_dropdown_setup(roi)

    roi.im = summed_diff_pattern

    roi.summed_dif_ax.imshow(roi.im, vmin=0, vmax=1000)

    # Functions for clicking on figure
    p_line_select_callback = partial(line_select_callback, figure_class=roi)
    p_contbtn_click = partial(contbtn_click, figure_class=roi, user_class=user_class)
    p_vs_change = partial(vs_change, figure_class=roi)
    p_rm_box_click = partial(rm_box_click, figure_class=roi)

    # Selecting a rectangle
    rs = RectangleSelector(roi.summed_dif_ax, p_line_select_callback,
                           drawtype='box', useblit=False, button=[1],
                           minspanx=5, minspany=5, spancoords='pixels',
                           interactive=True)

    plt.show()

    roi.contbtn.on_clicked(p_contbtn_click)
    roi.vmin_tb.on_submit(p_vs_change)
    roi.vmax_tb.on_submit(p_vs_change)
    roi.rm_box_btn.on_clicked(p_rm_box_click)

    return roi, rs


def rec_select_setup(figure_class):
    """Initiate the rectangle interactive

    Parameters
    ==========
    figure_class (ROI_FigureClass)
        the roi_figureclass object

    Returns
    =======
    Nothing
    """
    # Create a partial function for ease of use
    p_line_select_callback = partial(line_select_callback, ax=figure_class.summed_dif_ax)

    # Make a rectangle selector
    rs = RectangleSelector(figure_class.summed_dif_ax, p_line_select_callback,
                           drawtype='box', useblit=False, button=[1],
                           minspanx=5, minspany=5, spancoords='pixels',
                           interactive=True)

    # This allows the User to see the box being drawn when they click and drag
    plt.show(block=True)


def contbtn_click(event, figure_class, user_class):
    """Close the bounding box figure once complete

    Parameters
    ==========
    event (matplotlib event)
        the matplotlib event
    fig (matplotlib figure)
        the matplotlib figure to close

    Returns
    =======
    Nothing
    """
    # Setting the bounding box data
    user_class.diff_segment_squares =figure_class.pre_roi_bounding

    # Close all figures
    plt.close(figure_class.fig)


def vs_change(text, figure_class):
    """Change the vmin and vmax of a plot

    Parameters
    ==========
    text (matplotlib textbox)
        the matplotlib textbox
    figure_class (ROI_FigureClass)
        the roi_figureclass object

    Returns
    =======
    Nothing
    """
    # Obtain the vmin and vmax values
    vmin = int(figure_class.vmin_tb.text)
    vmax = int(figure_class.vmax_tb.text)

    # Clear the axes
    figure_class.summed_dif_ax.cla()

    # Show the image
    figure_class.summed_dif_ax.imshow(figure_class.im, vmin=vmin, vmax=vmax)

    # Do this
    figure_class.pre_roi_bounding = []


def rm_box_click(event, figure_class):
    """Removed the last bounding box the user made

    Parameters
    ==========
    event (matplotlib event)
        the matploblib event
    figure_class (ROI_FigureClass)
        the roi_figureclass object

    Returns
    =======
    Nothing
    """
    try:
        all_boxes = figure_class.pre_roi_bounding
    except:
        pass

    # Clear axis and reload image
    vmin = int(figure_class.vmin_tb.text)
    vmax = int(figure_class.vmax_tb.text)
    figure_class.summed_dif_ax.cla()
    figure_class.summed_dif_ax.imshow(figure_class.im, vmin=vmin, vmax=vmax)
    store_bound = []

    # Remove the last bounding box created
    try:
        for r in all_boxes[0:-1]:
            x1 = r[0]
            x2 = r[1]
            y1 = r[2]
            y2 = r[3]

            rect = plt.Rectangle((min(x1, x2), min(y1, y2)), np.abs(x1 - x2), np.abs(y1 - y2),
                                 fill=False, color='w')
            figure_class.summed_dif_ax.add_patch(rect)
            store_bound.append([x1, x2, y1, y2])
        figure_class.pre_roi_bounding = store_bound

    except Exception as ex:
        print('roi_bounding.py/rm_box_click', ex)
