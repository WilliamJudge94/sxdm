# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sxdm3.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import tifffile as tif
import imageio
from functools import partial
import sys

from det_chan import return_det
from postprocess import centroid_roi_map
from summed2d import summed2d_all_data
from pixel import grab_pix, sum_pixel, theta_maths, chi_maths
from h5 import h5get_image_destination
from background import scan_background_finder, scan_background
from mis import median_blur_numpy, median_blur_selective
import config

from time import sleep
from tqdm import tqdm



class Ui_MainWindow(object):
    
    def setupUi(self, MainWindow):
        """Sets up the PyQt5 GUI
        
        :param MainWindow: QtDev Tool Variable
        :return: Nothing
        """

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1161, 821)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.gridLayout_4 = QtWidgets.QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.frame_3 = QtWidgets.QFrame(self.centralwidget)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.frame_3)
        self.gridLayout_5.setObjectName("gridLayout_5")


        all_grid_layouts = [self.frame_3, self. gridLayout_6, self.gridLayout_5]


        # 2Theta 2D
        self.ttheta_2d_widget = QtWidgets.QWidget(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.ttheta_2d_widget.sizePolicy().hasHeightForWidth())
        self.ttheta_2d_widget.setSizePolicy(sizePolicy)
        self.ttheta_2d_widget.setObjectName("ttheta_2d_widget")
        self.ttheta_2d_widget.setSizePolicy(sizePolicy)

        # Creating the Widget
        self.ttheta_2d_widget = make_2d(self.ttheta_2d_widget, self.im_ttheta_2d, types='ttheta')
        self.gridLayout_5.addWidget(self.ttheta_2d_widget, 0, 0, 1, 1)

        # Chi 2D
        self.chi_2d_widget = QtWidgets.QWidget(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.chi_2d_widget.sizePolicy().hasHeightForWidth())
        self.chi_2d_widget.setSizePolicy(sizePolicy)
        self.chi_2d_widget.setObjectName("chi_2d_widget")

        # Creating the Widget
        self.chi_2d_widget = make_2d(self.chi_2d_widget, self.im_chi_2d, types='chi')
        self.chi_2d_widget.setSizePolicy(sizePolicy)

        self.gridLayout_5.addWidget(self.chi_2d_widget, 1, 0, 1, 1)

        # 2Theta 1D
        self.ttheta_1d_widget = QtWidgets.QWidget(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.ttheta_1d_widget.sizePolicy().hasHeightForWidth())
        self.ttheta_1d_widget.setSizePolicy(sizePolicy)
        self.ttheta_1d_widget.setObjectName("ttheta_1d_widget")

        # Creating the Widget
        self.ttheta_1d_widget = make_1d(self.ttheta_1d_widget, self.ttheta_1d_data)
        self.ttheta_1d_widget.setSizePolicy(sizePolicy)
        self.gridLayout_5.addWidget(self.ttheta_1d_widget, 0, 1, 1, 1)

        # Chi 1D
        self.chi_1d_widget = QtWidgets.QWidget(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.chi_1d_widget.sizePolicy().hasHeightForWidth())
        self.chi_1d_widget.setSizePolicy(sizePolicy)
        self.chi_1d_widget.setObjectName("chi_1d_widget")

        # Creating the Widget
        self.chi_1d_widget = make_1d(self.chi_1d_widget, self.chi_1d_data)
        self.chi_1d_widget.setSizePolicy(sizePolicy)
        self.gridLayout_5.addWidget(self.chi_1d_widget, 1, 1, 1, 1)

        # Fluor
        self.gridLayout_4.addWidget(self.frame_3, 0, 0, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_4, 0, 1, 1, 1)
        self.fluor_widget = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.fluor_widget.sizePolicy().hasHeightForWidth())
        self.fluor_widget.setSizePolicy(sizePolicy)
        self.fluor_widget.setMinimumSize(QtCore.QSize(260, 0))
        self.fluor_widget.setObjectName("fluor_widget")

        # Creating the Widget
        self.fluor_widget = make_2d(self.fluor_widget, self.im_flour)
        self.fluor_widget.setSizePolicy(sizePolicy)
        self.fluor_widget.setMinimumSize(QtCore.QSize(260, 0))
        self.gridLayout_6.addWidget(self.fluor_widget, 0, 0, 1, 1)

        # ROI
        self.roi_widget = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.roi_widget.sizePolicy().hasHeightForWidth())
        self.roi_widget.setSizePolicy(sizePolicy)
        self.roi_widget.setMinimumSize(QtCore.QSize(260, 0))
        self.roi_widget.setObjectName("roi_widget")

        # Creating the Widget
        self.roi_widget = make_2d(self.roi_widget, self.im_roi)
        self.roi_widget.setSizePolicy(sizePolicy)
        self.roi_widget.setMinimumSize(QtCore.QSize(260, 0))
        self.gridLayout_6.addWidget(self.roi_widget, 0, 2, 1, 1)


        self.gridLayout.addLayout(self.gridLayout_6, 2, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setContentsMargins(-1, 60, -1, 60)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.spot_vmax_label = QtWidgets.QLabel(self.centralwidget)
        self.spot_vmax_label.setObjectName("spot_vmax_label")
        self.gridLayout_2.addWidget(self.spot_vmax_label, 1, 0, 1, 1)
        self.spot_vmin_label = QtWidgets.QLabel(self.centralwidget)
        self.spot_vmin_label.setObjectName("spot_vmin_label")
        self.gridLayout_2.addWidget(self.spot_vmin_label, 0, 0, 1, 1)
        self.summed_vmin_label = QtWidgets.QLabel(self.centralwidget)
        self.summed_vmin_label.setObjectName("summed_vmin_label")
        self.gridLayout_2.addWidget(self.summed_vmin_label, 2, 0, 1, 1)
        self.summed_vmax_label = QtWidgets.QLabel(self.centralwidget)
        self.summed_vmax_label.setObjectName("summed_vmax_label")
        self.gridLayout_2.addWidget(self.summed_vmax_label, 3, 0, 1, 1)
        self.spot_vmin_lcd = QtWidgets.QLCDNumber(self.centralwidget)
        self.spot_vmin_lcd.setObjectName("spot_vmin_lcd")
        self.gridLayout_2.addWidget(self.spot_vmin_lcd, 0, 1, 1, 1)
        self.spot_vmax_lcd = QtWidgets.QLCDNumber(self.centralwidget)
        self.spot_vmax_lcd.setObjectName("spot_vmax_lcd")
        self.gridLayout_2.addWidget(self.spot_vmax_lcd, 1, 1, 1, 1)
        self.summed_vmin_lcd = QtWidgets.QLCDNumber(self.centralwidget)
        self.summed_vmin_lcd.setObjectName("summed_vmin_lcd")
        self.gridLayout_2.addWidget(self.summed_vmin_lcd, 2, 1, 1, 1)
        self.summed_vmax_lcd = QtWidgets.QLCDNumber(self.centralwidget)
        self.summed_vmax_lcd.setObjectName("summed_vmax_lcd")
        self.gridLayout_2.addWidget(self.summed_vmax_lcd, 3, 1, 1, 1)

        self.horizontalLayout_2.addLayout(self.gridLayout_2)

        # Spot Dif
        self.spot_widget = QtWidgets.QWidget(self.centralwidget)
        self.spot_widget.setObjectName("spot_widget")
        self.spot_widget = make_2d(self.spot_widget, self.im_spot_dif, types='spot_dif')
        self.horizontalLayout_2.addWidget(self.spot_widget)
        self.summed_widget = QtWidgets.QWidget(self.centralwidget)
        self.summed_widget.setObjectName("summed_widget")

        # Creating the Widget
        self.summed_widget = make_2d(self.summed_widget, self.im_summed_dif, types='sum_dif')
        self.horizontalLayout_2.addWidget(self.summed_widget)

        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setContentsMargins(-1, 60, -1, 60)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.stdev_min_label = QtWidgets.QLabel(self.centralwidget)
        self.stdev_min_label.setObjectName("stdev_min_label")
        self.gridLayout_3.addWidget(self.stdev_min_label, 2, 0, 1, 1)
        self.med_blur_height_label = QtWidgets.QLabel(self.centralwidget)
        self.med_blur_height_label.setObjectName("med_blur_height_label")
        self.gridLayout_3.addWidget(self.med_blur_height_label, 1, 0, 1, 1)
        self.med_blur_dis_label = QtWidgets.QLabel(self.centralwidget)
        self.med_blur_dis_label.setObjectName("med_blur_dis_label")
        self.gridLayout_3.addWidget(self.med_blur_dis_label, 0, 0, 1, 1)
        self.bkg_m_label = QtWidgets.QLabel(self.centralwidget)
        self.bkg_m_label.setObjectName("bkg_m_label")
        self.gridLayout_3.addWidget(self.bkg_m_label, 3, 0, 1, 1)
        self.med_blur_dist_lcd = QtWidgets.QLCDNumber(self.centralwidget)
        self.med_blur_dist_lcd.setObjectName("med_blur_dist_lcd")
        self.gridLayout_3.addWidget(self.med_blur_dist_lcd, 0, 1, 1, 1)
        self.med_blur_height_lcd = QtWidgets.QLCDNumber(self.centralwidget)
        self.med_blur_height_lcd.setObjectName("med_blur_height_lcd")
        self.gridLayout_3.addWidget(self.med_blur_height_lcd, 1, 1, 1, 1)
        self.stdev_min_lcd = QtWidgets.QLCDNumber(self.centralwidget)
        self.stdev_min_lcd.setObjectName("stdev_min_lcd")
        self.gridLayout_3.addWidget(self.stdev_min_lcd, 2, 1, 1, 1)
        self.bkg_m_lcd = QtWidgets.QLCDNumber(self.centralwidget)
        self.bkg_m_lcd.setObjectName("bkg_m_lcd")
        self.gridLayout_3.addWidget(self.bkg_m_lcd, 3, 1, 1, 1)

        self.alg_label = QtWidgets.QLabel(self.centralwidget)
        self.alg_label.setObjectName("alg_label")
        self.gridLayout_3.addWidget(self.alg_label, 4, 0, 1, 1)
        self.alg_lcd = QtWidgets.QLCDNumber(self.centralwidget)
        self.alg_lcd.setObjectName("alg_lcd")
        self.gridLayout_3.addWidget(self.alg_lcd, 4, 1, 1, 1)

        self.horizontalLayout_2.addLayout(self.gridLayout_3)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 3, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1161, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuBlur_Algorithm = QtWidgets.QMenu(self.menuFile)
        self.menuBlur_Algorithm.setObjectName("menuBlur_Algorithm")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget = QtWidgets.QDockWidget(MainWindow)
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.map_label = QtWidgets.QLabel(self.dockWidgetContents)
        self.map_label.setMinimumSize(QtCore.QSize(0, 0))
        self.map_label.setMaximumSize(QtCore.QSize(35, 16777215))
        self.map_label.setObjectName("map_label")
        self.horizontalLayout_4.addWidget(self.map_label)
        self.vmin_vmax_map_picker = QtWidgets.QComboBox(self.dockWidgetContents)
        self.vmin_vmax_map_picker.setMinimumSize(QtCore.QSize(175, 0))
        self.vmin_vmax_map_picker.setObjectName("vmin_vmax_map_picker")
        self.vmin_vmax_map_picker.addItem("")
        self.vmin_vmax_map_picker.addItem("")
        self.vmin_vmax_map_picker.addItem("")
        self.vmin_vmax_map_picker.addItem("")
        self.horizontalLayout_4.addWidget(self.vmin_vmax_map_picker)
        self.label_2 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_2.setMaximumSize(QtCore.QSize(40, 16777215))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_4.addWidget(self.label_2)
        self.vmin_box = QtWidgets.QDoubleSpinBox(self.dockWidgetContents)

        # Setting Min and Max Values
        self.vmin_box.setDecimals(1)
        self.vmin_box.setMinimum(-10000000000.0)
        self.vmin_box.setMaximum(10000000000.0)

        self.vmin_box.setObjectName("vmin_box")
        self.horizontalLayout_4.addWidget(self.vmin_box)
        self.label_3 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_3.setMaximumSize(QtCore.QSize(45, 16777215))
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_4.addWidget(self.label_3)
        self.vmax_box = QtWidgets.QDoubleSpinBox(self.dockWidgetContents)

        self.vmax_box.setDecimals(1)
        self.vmax_box.setMinimum(-10000000000.0)
        self.vmax_box.setMaximum(10000000000.0)

        self.vmax_box.setObjectName("vmax_box")
        self.horizontalLayout_4.addWidget(self.vmax_box)
        spacerItem = QtWidgets.QSpacerItem(35, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.label_4 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_4.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.analysis_param_picker = QtWidgets.QComboBox(self.dockWidgetContents)
        self.analysis_param_picker.setMinimumSize(QtCore.QSize(230, 0))
        self.analysis_param_picker.setObjectName("analysis_param_picker")
        self.analysis_param_picker.addItem("")
        self.analysis_param_picker.addItem("")
        self.analysis_param_picker.addItem("")
        self.analysis_param_picker.addItem("")
        self.horizontalLayout_4.addWidget(self.analysis_param_picker)
        self.analysis_param_value = QtWidgets.QDoubleSpinBox(self.dockWidgetContents)

        self.analysis_param_value.setDecimals(1)
        self.analysis_param_value.setMinimum(-1000000.0)
        self.analysis_param_value.setMaximum(10000000.0)

        self.analysis_param_value.setObjectName("analysis_param_value")
        self.horizontalLayout_4.addWidget(self.analysis_param_value)
        spacerItem1 = QtWidgets.QSpacerItem(30, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)

        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(4), self.dockWidget)
        self.actionReprocess = QtWidgets.QAction(MainWindow)
        self.actionReprocess.setObjectName("actionReprocess")
        self.actionSave_Reload = QtWidgets.QAction(MainWindow)
        self.actionSave_Reload.setObjectName("actionSave_Reload")
        self.actionScipy = QtWidgets.QAction(MainWindow)
        self.actionScipy.setObjectName("actionScipy")
        self.actionSelective = QtWidgets.QAction(MainWindow)
        self.actionSelective.setObjectName("actionSelective")
        self.menuBlur_Algorithm.addAction(self.actionScipy)
        self.menuBlur_Algorithm.addAction(self.actionSelective)

        self.menuFile.addAction(self.actionReprocess)
        self.menuFile.addAction(self.actionSave_Reload)
        self.menuFile.addAction(self.menuBlur_Algorithm.menuAction())
        self.menubar.addAction(self.menuFile.menuAction())

        # Setting Up Variables
        self.vmin_vmax_map = 1

        # Spot Values
        self.spot_vmin_value = 0
        self.spot_vmax_value = np.max(self.im_spot_dif)

        # Summed Values
        self.summed_vmin_value = np.min(self.im_summed_dif)
        self.summed_vmax_value = np.max(self.im_summed_dif)

        # Flour Values
        self.flour_vmin_value = np.min(self.im_flour)
        self.flour_vmax_value = np.max(self.im_flour)

        # ROI Values
        self.roi_vmin_value = np.min(self.im_roi)
        self.roi_vmax_value = np.max(self.im_roi)

        # Analysis Values
        self.med_blur_dist_value = self.start_med_blur_dist
        self.med_blur_height_value = self.start_med_blur_height
        self.stdev_min_value = self.start_stdev_min
        self.bkg_m_value = self.start_bkg_multi
        self.alg_value = 'sel'

        # Position Values
        self.x_pos = 0
        self.y_pos = 0

        self.old_vmin_vmax_selector = 'Spot Diffraction'
        self.old_params_selector = 'Median Blur Distance (odd int)'

        self.cross_hair_color = 'black'


        # LCD Colors
        self.spot_vmin_lcd.setStyleSheet("QLCDNumber { background-color: black }")
        self.spot_vmax_lcd.setStyleSheet("QLCDNumber { background-color: black }")
        self.summed_vmin_lcd.setStyleSheet("QLCDNumber { background-color: black }")
        self.summed_vmax_lcd.setStyleSheet("QLCDNumber { background-color: black }")
        self.med_blur_dist_lcd.setStyleSheet("QLCDNumber { background-color: black }")
        self.med_blur_height_lcd.setStyleSheet("QLCDNumber { background-color: black }")
        self.stdev_min_lcd.setStyleSheet("QLCDNumber { background-color: black }")
        self.bkg_m_lcd.setStyleSheet("QLCDNumber { background-color: black }")
        self.alg_lcd.setStyleSheet("QLCDNumber { background-color: black }")

        # ProgressBar
        self.progressBar.setValue(0)

        # Starting Values
        self.med_blur_dist_lcd.display(self.med_blur_dist_value)
        self.med_blur_height_lcd.display(self.med_blur_height_value)
        self.stdev_min_lcd.display(self.stdev_min_value)
        self.bkg_m_lcd.display(self.bkg_m_value)
        self.alg_lcd.display(self.alg_value)

        self.spot_vmin_lcd.display(self.spot_vmin_value)
        self.spot_vmax_lcd.display(self.spot_vmax_value)
        self.summed_vmin_lcd.display(self.summed_vmin_value)
        self.summed_vmax_lcd.display(self.summed_vmax_value)

        # vmin, vmax, and params setup
        self.vmin_box.setValue(self.spot_vmin_value)
        self.vmax_box.setValue(self.spot_vmax_value)
        self.analysis_param_value.setValue(self.med_blur_dist_value)

        # Pickers
        self.vmin_vmax_map_picker.currentTextChanged.connect(self.change_vmin_vmax_selector)
        self.analysis_param_picker.currentTextChanged.connect(self.change_vmin_vmax_selector)

        # Vmin and Vmax change
        self.vmin_box.valueChanged.connect(self.change_vmin_vmax)
        self.vmax_box.valueChanged.connect(self.change_vmin_vmax)

        self.analysis_param_value.valueChanged.connect(self.change_vmin_vmax)

        # Functions
        self.fluor_widget.fig.canvas.mpl_connect('button_press_event', self.change_spot)
        self.roi_widget.fig.canvas.mpl_connect('button_press_event', self.change_spot)
        self.ttheta_2d_widget.fig.canvas.mpl_connect('button_press_event', self.change_spot)
        self.chi_2d_widget.fig.canvas.mpl_connect('button_press_event', self.change_spot)

        # Val Changes
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        """Starts the PyQt5 GUI
        
        :param MainWindow: Qt Dev Tool variable
        :return: Nothing
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SXDM Centroid Viewer"))
        self.spot_vmax_label.setText(_translate("MainWindow", "Spot VMax:"))
        self.spot_vmin_label.setText(_translate("MainWindow", "Spot VMin:                       "))
        self.summed_vmin_label.setText(_translate("MainWindow", "Summed VMin:"))
        self.summed_vmax_label.setText(_translate("MainWindow", "Summed VMax:"))
        self.stdev_min_label.setText(_translate("MainWindow", "Standard Deviation Min:"))
        self.med_blur_height_label.setText(_translate("MainWindow", "Median Blur Height:"))
        self.med_blur_dis_label.setText(_translate("MainWindow", "Median Blur Distance:"))
        self.alg_label.setText(_translate("MainWindow", "Alg:"))
        self.bkg_m_label.setText(_translate("MainWindow", "Background Multiplier:"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuBlur_Algorithm.setTitle(_translate("MainWindow", "Blur Algorithm"))

        self.map_label.setText(_translate("MainWindow", "Map:"))
        self.vmin_vmax_map_picker.setItemText(0, _translate("MainWindow", "Spot Diffraction"))
        self.vmin_vmax_map_picker.setItemText(1, _translate("MainWindow", "Summed Diffraction"))
        self.vmin_vmax_map_picker.setItemText(2, _translate("MainWindow", "Fluorescence"))
        self.vmin_vmax_map_picker.setItemText(3, _translate("MainWindow", "ROI"))
        self.label_2.setText(_translate("MainWindow", "VMin:"))
        self.label_3.setText(_translate("MainWindow", "VMax:"))
        self.label_4.setText(_translate("MainWindow", "Analysis Parameter:"))
        self.analysis_param_picker.setItemText(0, _translate("MainWindow", "Median Blur Distance (odd int)"))
        self.analysis_param_picker.setItemText(1, _translate("MainWindow", "Median Blur Height (int)"))
        self.analysis_param_picker.setItemText(2, _translate("MainWindow", "Standard Deviation Min (float, int)"))
        self.analysis_param_picker.setItemText(3, _translate("MainWindow", "Background Multiplier (float, int)"))

        self.actionReprocess.setText(_translate("MainWindow", "Reprocess"))
        self.actionReprocess.setStatusTip(_translate("MainWindow", "Reprocess data with updated parameters"))
        self.actionReprocess.setShortcut(_translate("MainWindow", "Ctrl+R"))
        self.actionSave_Reload.setText(_translate("MainWindow", "Save/Reload"))
        self.actionSave_Reload.setStatusTip(_translate("MainWindow", "Savecurrent analysis and reload the data"))
        self.actionSave_Reload.setShortcut(_translate("MainWindow", "Ctrl+S"))

        self.analysis_param_picker.setStatusTip(_translate("MainWindow", "Change the Analyis Parameters"))
        self.frame_3.setStatusTip(_translate("MainWindow", "Left: Fluorescence  - " +
                                                           "Middle: upper: 2theta 2D, 1D  lower: chi 2D, 1D - " +
                                                           "Right: ROI"))

        # Blur Alg
        self.actionScipy.setText(_translate("MainWindow", "Scipy"))
        self.actionSelective.setText(_translate("MainWindow", "Selective"))

        self.actionSelective.triggered.connect(self.change_alg_selective)
        self.actionScipy.triggered.connect(self.change_alg_scipy)

        self.actionReprocess.triggered.connect(self.reprocess)
        self.actionSave_Reload.triggered.connect(self.save_reload)


        #self.pprogresss = tqdm([1,2,3,4,5])
        #self.threadclass = ThreadClass(pbar_tqdm = self.pprogresss)
        #self.threadclass.start()

    def change_vmin_vmax_selector(self):
        """When User would like to change the vmin or vmax settings,
        This will reload all data with the appropriate bound values.
        
        :return: Nothing
        """
        current_value = self.vmin_vmax_map_picker.currentText()
        if current_value == 'Spot Diffraction':
            self.vmin_box.setValue(self.spot_vmin_value)
            self.vmax_box.setValue(self.spot_vmax_value)
        elif current_value == 'Summed Diffraction':
            self.vmin_box.setValue(self.summed_vmin_value)
            self.vmax_box.setValue(self.summed_vmax_value)
        elif current_value == 'Fluorescence':
            self.vmin_box.setValue(self.flour_vmin_value)
            self.vmax_box.setValue(self.flour_vmax_value)
        elif current_value == 'ROI':
            self.vmin_box.setValue(self.roi_vmin_value)
            self.vmax_box.setValue(self.roi_vmax_value)

        current_value = self.analysis_param_picker.currentText()

        if current_value == 'Median Blur Distance (odd int)':
            self.analysis_param_value.setValue(self.med_blur_dist_value)

        elif current_value == 'Median Blur Height (int)':
            self.analysis_param_value.setValue(self.med_blur_height_value)

        elif current_value == 'Standard Deviation Min (float, int)':
            self.analysis_param_value.setValue(self.stdev_min_value)

        elif current_value == 'Background Multiplier (float, int)':
            self.analysis_param_value.setValue(self.bkg_m_value)

    def change_alg_selective(self):
        """Handels all processes after chaning the median blur algorithm to selective.
        
        :return: Nothing
        """
        self.alg_value = 'sel'
        self.alg_lcd.display(self.alg_value)
        self.med_blur_height_lcd.setStyleSheet("QLCDNumber { background-color: black }")
        config.median_blur = median_blur_selective
        self.replot_chi_1d()
        self.replot_ttheta_1d()

    def change_alg_scipy(self):
        """Handels all processes after chaning the median blur algorithm to selective.

        :return: Nothing
        """
        self.alg_value = 'scpy'
        self.alg_lcd.display(self.alg_value)
        self.med_blur_height_lcd.setStyleSheet("QLCDNumber { background-color: red }")
        config.median_blur = median_blur_numpy
        self.replot_chi_1d()
        self.replot_ttheta_1d()

    def pbar(self, inputs):
        """One day will allow for a progress bar at the bottom of the PyQt5 GUI
        
        :param inputs: a tqdm() object
        :return: Nothing
        """

        for link in inputs:
            progress += 100 / len(inputs)
            self.progressChanged.emit(progress)

    def change_vmin_vmax(self):
        """ Deals with all processes after chaning the vmin or vmax values.
        
        :return: Nothing
        """

        current_value = self.vmin_vmax_map_picker.currentText()

        if current_value == self.old_vmin_vmax_selector:

            if current_value == 'Spot Diffraction':
                self.spot_vmin_value = self.vmin_box.value()
                self.spot_vmax_value = self.vmax_box.value()

                self.spot_vmin_lcd.display(self.spot_vmin_value)
                self.spot_vmax_lcd.display(self.spot_vmax_value)

            elif current_value == 'Summed Diffraction':
                self.summed_vmin_value = self.vmin_box.value()
                self.summed_vmax_value = self.vmax_box.value()

                self.summed_vmin_lcd.display(self.summed_vmin_value)
                self.summed_vmax_lcd.display(self.summed_vmax_value)

            elif current_value == 'Fluorescence':
                self.flour_vmin_value = self.vmin_box.value()
                self.flour_vmax_value = self.vmax_box.value()

            elif current_value == 'ROI':
                self.roi_vmin_value = self.vmin_box.value()
                self.roi_vmax_value = self.vmax_box.value()


            self.determine_replot()

        else:
            self.old_vmin_vmax_selector = current_value


        current_value = self.analysis_param_picker.currentText()

        if current_value == self.old_params_selector:

            if self.cross_hair_color == 'black':
                self.cross_hair_color = 'red'
                self.replot_chi_2d()
                self.replot_ttheta_2d()

            if current_value == 'Median Blur Distance (odd int)':
                self.med_blur_dist_value = int(self.analysis_param_value.value())
                self.med_blur_dist_lcd.display(self.med_blur_dist_value)

            elif current_value == 'Median Blur Height (int)':
                self.med_blur_height_value = self.analysis_param_value.value()
                self.med_blur_height_lcd.display(self.med_blur_height_value)

            elif current_value == 'Standard Deviation Min (float, int)':
                self.stdev_min_value = self.analysis_param_value.value()
                self.stdev_min_lcd.display(self.stdev_min_value)

            elif current_value == 'Background Multiplier (float, int)':
                self.bkg_m_value = self.analysis_param_value.value()
                self.bkg_m_lcd.display(self.bkg_m_value)
                self.change_bkg_value()

            self.replot_ttheta_1d()
            self.replot_chi_1d()

        else:
            self.old_params_selector = current_value


    def determine_replot(self):
        """Determines which maps to replot based on User's current selections
        
        :return: Nothing
        """
        current_value = self.vmin_vmax_map_picker.currentText()
        if current_value == 'Spot Diffraction':
            self.replot_spot()

        elif current_value == 'Summed Diffraction':
            self.replot_summed()
        elif current_value == 'Fluorescence':
            self.replot_flour()

        elif current_value == 'ROI':
            self.replot_roi()

    def replot_flour(self):
        """Replots everything needed for changing flourescence images
        
        :return: Nothing
        """

        self.fluor_widget.ax.cla()
        if self.flour_vmax_value < self.flour_vmin_value:
            self.flour_vmax_value = self.flour_vmin_value

        self.fluor_widget.ax.imshow(self.im_flour, vmin=self.flour_vmin_value, vmax=self.flour_vmax_value)

        self.fluor_widget.ax.axvline(x=self.x_pos, color='w')
        self.fluor_widget.ax.axhline(y=self.y_pos, color='w')

        self.fluor_widget.ax.axis('off')

        self.fluor_widget.fig.canvas.draw()
        self.gridLayout_6.update()

    def replot_roi(self):
        """Replots everything needed for changing region of interest images

        :return: Nothing
        """
        self.roi_widget.ax.cla()

        if self.roi_vmax_value < self.roi_vmin_value:
            self.roi_vmax_value = self.roi_vmin_value

        self.roi_widget.ax.imshow(self.im_roi, vmin=self.roi_vmin_value, vmax=self.roi_vmax_value)

        self.roi_widget.ax.axvline(x=self.x_pos, color='w')
        self.roi_widget.ax.axhline(y=self.y_pos, color='w')

        self.roi_widget.ax.axis('off')

        self.roi_widget.fig.canvas.draw()
        self.gridLayout_6.update()

    def replot_spot(self):
        """Replots everything needed for changing the diffraction spot image

        :return: Nothing
        """
        self.spot_widget.ax.cla()
        if self.spot_vmax_value < self.spot_vmin_value:
            self.spot_vmax_value = self.spot_vmin_value

        self.spot_widget.ax.imshow(self.im_spot_dif, vmin=self.spot_vmin_value, vmax=self.spot_vmax_value)
        self.spot_widget.ax.set_title('Spot Diffraction', fontsize=8)
        self.spot_widget.ax.tick_params(axis='both', which='major', labelsize=8)
        self.spot_widget.fig.canvas.draw()
        self.horizontalLayout_2.update()

    def replot_summed(self):
        """Replots everything needed for changing the summed diffraction image

        :return: Nothing
        """
        self.summed_widget.ax.cla()
        if self.summed_vmax_value < self.summed_vmin_value:
            self.summed_vmax_value = self.summed_vmin_value

        self.summed_widget.ax.imshow(self.im_summed_dif, vmin=self.summed_vmin_value, vmax=self.summed_vmax_value)
        self.summed_widget.ax.set_title('Sum. Diffraction', fontsize=8)
        self.summed_widget.ax.tick_params(axis='both', which='major', labelsize=8)
        self.summed_widget.fig.canvas.draw()
        self.horizontalLayout_2.update()

    def replot_ttheta_2d(self):
        """Replots everything needed for changing the 2theta 2D centroid plots

        :return: Nothing
        """
        self.ttheta_2d_widget.ax.cla()
        self.ttheta_2d_widget.ax.imshow(self.im_ttheta_2d)
        min_val = np.nanmin(self.im_ttheta_2d)
        max_val = np.nanmax(self.im_ttheta_2d)
        diff_val = max_val = min_val
        #self.ttheta_2d_widget.ax.imshow(self.im_ttheta_2d, cmap='inferno')

        self.ttheta_2d_widget.ax.axvline(x=self.x_pos, color=self.cross_hair_color, linewidth=0.5)
        self.ttheta_2d_widget.ax.axhline(y=self.y_pos, color=self.cross_hair_color, linewidth=0.5)
        self.ttheta_2d_widget.ax.set_title(f'Min: {min_val}  Max: {max_val}  Delta: {diff_val}')

        self.ttheta_2d_widget.ax.axis('off')

        self.ttheta_2d_widget.fig.canvas.draw()
        self.gridLayout_5.update()

    def replot_chi_2d(self):
        """Replots everything needed for changing the chi 2D centroid plots

        :return: Nothing
        """
        self.chi_2d_widget.ax.cla()
        self.chi_2d_widget.ax.imshow(self.im_chi_2d, cmap='plasma')

        self.chi_2d_widget.ax.axvline(x=self.x_pos, color=self.cross_hair_color, linewidth=0.5)
        self.chi_2d_widget.ax.axhline(y=self.y_pos, color=self.cross_hair_color, linewidth=0.5)

        self.chi_2d_widget.ax.axis('off')

        self.chi_2d_widget.fig.canvas.draw()
        self.gridLayout_5.update()

    def replot_ttheta_1d(self):
        """Replots everything needed for changing the 2theta 1D centroid plots

        :return: Nothing
        """
        ttheta, ttheta_centroid, ttheta_centroid_finder, ttheta2 = theta_maths(self.im_spot_dif,
                                                                               self.med_blur_dist_value,
                                                                               self.med_blur_height_value,
                                                                               self.stdev_min_value)

        self.ttheta_1d_widget.ax.cla()

        self.ttheta_1d_widget.ax.plot(ttheta, color='blue')
        self.ttheta_1d_widget.ax.plot(ttheta_centroid_finder, color='red')
        self.ttheta_1d_widget.ax.axvline(x=ttheta_centroid, color='black')
        self.ttheta_1d_widget.ax.tick_params(axis='both', which='major', labelsize=2)

        self.ttheta_1d_widget.fig.canvas.draw()
        self.gridLayout_5.update()

    def replot_chi_1d(self):
        """Replots everything needed for changing the chi 1D centroid plots

        :return: Nothing
        """
        chi, chi_centroid, chi_centroid_finder = chi_maths(self.im_spot_dif,
                                                            self.med_blur_dist_value,
                                                            self.med_blur_height_value,
                                                            self.stdev_min_value)

        self.chi_1d_widget.ax.cla()

        self.chi_1d_widget.ax.plot(chi, color='blue')
        self.chi_1d_widget.ax.plot(chi_centroid_finder, color='red')
        self.chi_1d_widget.ax.axvline(x=chi_centroid, color='black')
        self.chi_1d_widget.ax.tick_params(axis='both', which='major', labelsize=2)

        self.chi_1d_widget.fig.canvas.draw()
        self.gridLayout_5.update()

    def change_spot(self, event):
        """Handels all processes after changing to a different User selected spot. 
        
        :param event: matplotlib event variable
        :return: Nothing
        """


        #inputs = np.arange(0, 10, 1)

        #total_len = len(inputs)
        #self.pprogresss = tqdm(inputs)


        #self.inputs = self.pprogresss

        #config.inputs = self.inputs

        #for i in self.pprogresss:
        #    sleep(1)
        #    print(config.inputs.n, 'config inner function')
        #    print(self.pprogresss.n, 'config inner function 2')

        #from time import sleep

        #self.pbar(inputs)

        #self.progressBar.setValue(10)

        #count = 0
        #while count < 10:
        #    count += 1
        #    sleep(1)
        #    self.progressBar.setValue(count)
        #    QtGui.qApp.processEvents()
        #for i in inputs:
        #    sleep(2)
        #    print(inputs.n)
        #    self.progressBar.setValue(int((inputs.n/total_len)*100))
        #    print('hi')
        #    self.progressBar.update()

        self.x_pos = int(np.round(event.xdata,  decimals=0))
        self.y_pos = int(np.round(event.ydata, decimals=0))
        
        #self.x_pos = self.x_pos + self.fs.analysis_total_columns[0]
        #self.y_pos = self.y_pos + self.fs.analysis_total_rows[0]

        try:
            sub_rows = self.fs.analysis_total_rows[0]
        except:
            sub_rows = 0

        try:
            sub_columns = self.fs.analysis_total_columns[0]
        except:
            sub_columns = 0

        self.im_spot_dif = determine_spot_diff(self.fs,
                                               self.y_pos + sub_rows,
                                               self.x_pos + sub_columns)

        self.replot_spot()
        self.replot_flour()
        self.replot_roi()
        self.replot_ttheta_2d()
        self.replot_ttheta_1d()
        self.replot_chi_2d()
        self.replot_chi_1d()

    def change_analysis_params(self):
        """Handels changing the analysis parameters and reloads plot accordingly
        
        :return: Nothing
        """
        
        self.med_blur_dist_value = int(self.analysis_param_value.value())
        self.med_blur_height_value = self.analysis_param_value.value()
        self.stdev_min_value = self.analysis_param_value.value()
        self.bkg_m_value = self.analysis_param_value.value()

        self.replot_ttheta_1d()
        self.replot_chi_1d()

    def mousePressEvent(self, event):
        """Matplotlib event than handels the button clicking
        
        :param event: Matplotlib event
        :return: Nothing
        """
        if event.button() == Qt.LeftButton:
            self.x_pos = event.x
            self.y_pos = event.y

            self.change_spot()

    def reprocess(self):
        """Handels when the User clicks on reprocess
        
        :return: Nothing
        """

        self.fs.centroid_analysis(self.fs.analysis_total_rows,
                                  self.fs.analysis_total_columns,
                                  self.med_blur_dist_value,
                                  self.med_blur_height_value,
                                  self.stdev_min_value,
                                  self.bkg_m_value)

        self.im_ttheta_2d = centroid_roi_map(self.fs.results, 'ttheta_centroid')
        self.im_chi_2d = centroid_roi_map(self.fs.results, 'chi_centroid')

        self.cross_hair_color = 'purple'
        self.replot_chi_2d()
        self.replot_ttheta_2d()

    def save_reload(self):
        """Allows the User to save the data
        
        :return: Nothing
        """
        self.fs.save()
        self.cross_hair_color = 'black'
        self.replot_chi_2d()
        self.replot_ttheta_2d()


    def change_bkg_value(self):
        """Handels changing the background multiplier value
        
        :return: Nothing
        """
        bk_dic = scan_background(self.fs, multiplier=self.bkg_m_value)
        self.im_summed_dif = summed2d_all_data_v2(self=self.fs, bkg_multiplier=self.bkg_m_value)
        self.replot_summed()


#class ThreadClass(QtCore.QThread):
#    def __init__(self, pbar_tqdm, parent=None):
#        super(ThreadClass, self).__init__(parent)
#        self.pbar_tqdm = pbar_tqdm

#    def run(self):
#        for i in range(100):
#            sleep(1)
#            try:
#                print(config.n)
#            except Exception as ex:
#                print(ex)
#                config.n = 0


def make_2d(widget, image, types='norm'):
    """Creates the first 2D plots
    
    :param widget: the PyQt5 widget you are trying to make a plot for
    :param image: the image you want to show
    :param types: the type of image - sets the image title
    :return: the PyQt5 Completed widget
    """
    fig, ax = plt.subplots()

    plt.imshow(image)

    if types == 'norm':
        plt.axis('off')
        plt.tight_layout()

    elif types == 'ttheta':
        plt.axis('off')
        plt.tight_layout()

    elif types == 'chi':
        plt.axis('off')
        plt.tight_layout()

    elif types == 'spot_dif':
        plt.title('Spot Diffraction', fontsize=8)
        plt.tight_layout(pad=3)

    elif types == 'sum_dif':
        plt.title('Sum. Diffraction', fontsize=8)
        plt.tight_layout(pad=3)


    widget = FigureCanvas(fig)

    widget.fig = fig
    widget.ax = ax

    return widget


def make_1d(widget, data):
    """Created the 1 dimensional widgets
    
    :param widget: the PyQt5 widget
    :param data: the data the Users wants to show
    :return: the PyQt5 widget
    """
    fig, ax = plt.subplots()
    plt.plot(data)
    plt.xlabel(' ')
    plt.tight_layout(pad=2)
    widget = FigureCanvas(fig)
    widget.fig = fig
    widget.ax = ax
    return widget


def determine_spot_diff(self, row, column, auto_sum=True):
    """Determines the diffraction pattern for a given x and y location
    
    :param self: the SXDMFrameset
    :param row: the row value
    :param column: the column value
    :param auto_sum: (bool) would you like to summ all the diffraction patterns? True = yes
    :return: the diffraction pattern(s)
    """

    pix = grab_pix(array=self.image_array, row=row, column=column, int_convert=True)
    destination = h5get_image_destination(self=self, pixel=pix)
    each_scan_diffraction = sum_pixel(self=self, images_loc=destination)

    # Background Correction
    backgrounds = scan_background_finder(destination=destination, background_dic=self.background_dic)
    each_scan_diffraction_post = np.subtract(each_scan_diffraction, backgrounds)

    if auto_sum:
        summed_dif = np.sum(each_scan_diffraction_post, axis=0)
    elif not auto_sum:
        summed_dif = each_scan_diffraction_post

    return summed_dif


def qt_centroid_view(fs, fluor_im, start_analysis_params) :
    """Initiates the Centroid Viewer
    
    
    :param fs: the SXDMFrameset
    :param fluor_im: the flourescence image to show in the viewer
    :param start_analysis_params: the staring analaysis parameters
    :return: Nothing
    """

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()

    ui.fs = fs

    ui.im_flour = fluor_im

    ui.im_roi = centroid_roi_map(fs.results, 'full_roi')
    ui.im_ttheta_2d = centroid_roi_map(fs.results, 'ttheta_centroid')
    ui.im_chi_2d = centroid_roi_map(fs.results, 'chi_centroid')

    ui.start_med_blur_dist, ui.start_med_blur_height, ui.start_stdev_min, ui.start_bkg_multi = start_analysis_params


    im_dif = determine_spot_diff(fs, 0, 0)
    ui.im_summed_dif = summed2d_all_data(self=fs, bkg_multiplier=ui.start_bkg_multi)
    ui.im_spot_dif = im_dif

    ui.ttheta_1d_data = [1]
    ui.chi_1d_data = [1]
    
    
    
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
