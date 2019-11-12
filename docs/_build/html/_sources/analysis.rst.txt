******************
Analyzing the Data
******************


Setting Up Detector Channels
============================

After importing the data, the User will likley want to store detector
channel values for the Experimental Run. This avoids having to remember
them every time the User would like to go back and analyze a specific
dataset. To begin, run the following

.. code:: python
    
    from sxdm import *

    file='/path/to/file.h5'
    
    # Display a preset detector channel input that the User can copy
    disp_det_chan(file)


    # Example Output

    detector_scan = {
        'Main_Scan': 2,
        }
    
    filenumber = 2
    
    fluor = {
        'Cu': 2,
        'Fe': 2,
        'Zn': 2,
        'O': 2,
        }
    
    hybrid_x = 2
    
    hybrid_y = 2
    
    mis = {
        '2Theta': 2,
        'Relative_r_To_Detector': 2,
        'Storage_Ring_Current': 2,
        }
    
    roi = {
        'ROI_1': 2,
        'ROI_2': 2,
        'ROI_3': 2,
        }
    
    sample_theta = 2

If detector channels have not been previously set default values will present themselves. Change all values according
to your experimental setup. 

``Main_Scan``   is the scan number used to determine binstrumental broadening. 

``filenumber``  is the detector channel accosiated with the .tif file numbers. 

``fluor``       is a dictionary of User defined fluoresence detector channels.

``hybrid_x``    is the detector channel accociated with the x-axis motor movements for the scan.

``hybrid_y``    is the detector channel associated with the y-axis motor movements for the scan.

``mis``         is a dictionary for the User to input any other useful detector channels for their own experiments.
                This dictionary must have at least one entry in it.

``roi``         is a dictionary for the 26-ID-C pre caluclated region of diffraction interest maps.

``sample_theta`` is the detector channel associated with the angle of the sample during the scan.

Once these values are set the User can run

.. code:: python

    # Change Values, Run Cell, And Input Values Into Function Below
    setup_det_chan(file, fluor, roi, detector_scan, filenumber, sample_theta, hybrid_x, hybrid_y, mis)


Setting Up Frameset
===================

After importing the data, and setting the detector channels you will likely need to process and analyze
the frame set. This is done through the
:py:class:`sxdm.SXDMFrameset` class. Most
**processing and analysis steps are provided as methods on this
class**, so the first step is to create a frameset object.

.. code:: python

    from sxdm import *

    # Use the same HDF file and group name as when importing
    test_fs = SXDMFrameset(file'/path/to/file.h5',
                dataset_name='user_dataset_name',
                scan_numbers=[1, 2, 3, 4, ...],
                fill_num=4,
                restart_zoneplate=False,
                median_blur_algorithm='scipy',
                )

``file``   A string to the file.h5 file

``dataset_name``  A user defined string associated with a specific dataset. Examples - 'Pristine', 'Charged' 

``scan_numbers``       A list of scan numbers the User would like to associated with the set ``dataset_name``
                        This one has to be set once. Every other time it will, pull from these stored values,
                        unless a User decides to change the ``scan_numbers``.

``fill_num``    This is an integer set by the User which defines how many number values are in each .tif file name.

``restart_zoneplate``    Allows the User to redefine the ZonePlate data

``median_blur_algorithm``         Allows the User to choose which type of median blur algorithm is to be used for
                                Data Analysis.



Median Blur Type Selection
--------------------------
In the creation of the SXDMFrameset there is an option to set a ``median_blur_algorithm``.
There are two option in the current version of SXDM. ``scipy`` and ``selective``.


**mis.median_blur_scipy()**

This median blur algorithm calls the ``scipy.signal.me_blur``. This will apply a median blur to the entire 1 dimensional
datasets produced by the 2 dimensional images. 


**mis.median_blur_selective()**

This median blur alogrithm bins off line scan data, determines the mean, if there is a value above a User value + mean
it will be replaced with the mean value for the chunk. This preserves most of the raw intensity data at the cost of
speed.


Scan Dimensions Check
=====================

Starting the SXDMFrameset will automatically determine the pixel X resolution for all the imported scans as well as all
the Y resolutions for all the scans and checks to make sure every scan has identical X resolutions and every scan has
identical Y resolutions. Then it checks to see if the median(x) and median(y) resoltuions are equivalent.

If the program throws an error during the resolution check


1) Make sure you have set the ``hybrid_x`` and ``hybrid_y`` values correctly in the ``setup_det_chan()`` function.

2) Pull up all the scan resolutions with ``test_fs.all_res_x``, and ``test_fs.all_res_y``. These will be in the
same order as test_fs.scan_numbers. Remove the scan that is throwing the error when setting up 
``test_fs = SXDMFrameset()``. Future versions will resample the scans to create identical resolutions in all
X, all Y, and in X v. Y.

3) If there is still an error the scan dimensions are not the same across all scans. Run 
``show_hybrid_dimensions(test_fs)`` to see all the scan dimensions

Alignment
=========

In order to acquire reliable spectra, **it is important that the
frames be aligned properly**. Thermal expansion, motor slop, sample
damage and imperfect microscope alignment can all cause frames to be
misaligned. **It is almost always necessary to align the frames before
performing any of the subsequent steps.**

Aligning the scan can be carried out through the following code and following the GUI. Alignment can only be done of
the Fluorescence images or the Region of Interest images set in the setup_det_chan() function. User will define which
one to use in the GUI. Once all alignment centers have been set, it is ok to just quit out of the windows.

This is done with the
:py:meth:`test_fs.alignment()`
method:

.. code:: python

  from sxdm import *
  # Select an imported hdf file to use
  test_fs = SXDMFrameset(file="...")
  
  # Run through five passes of the default phase correlation
  test_fs.alignment(reset=False)

  #reset (bool) - if you would like to completely reset the alignment make this equal True

**if you import new scan numbers you must make sure reset=True for the first alignment**

Diffraction Axis Values
=======================

To determine the chi bounds (angle bounds) for the detector diffraction images as well as determining the numerical
aperture, focal length, and instrumental broadening in pixels.


.. code:: python

    test_fs.chi_determination()

angle difference (in degrees) from the left/bottom hand side of the detector to the right/top ``test_fs.chi`` 
focal length in millimeters can be called with ``test_fs.focal_length_mm`` numberical aperature in millirads can be 
called with ``test_fs.NA_mrads`` instrumental broadening radius in pixels of the diffraction image can be called with 
``test_fs.broadening_in_pix``

Region Of Interest Analysis
===========================

Segment
-------

In order for the program to determine a region of interest the User must define areas of interest. This GUI allows
the User to define as many Region Of Interests as they please in the diffraction image. Then upon running the Analysis
portion, the program will determine the summed value of these regions, plot them, as well as normalize.

Through a GUI the User can select multiple region of interests from the summed diffraction pattern. Set the
``diff_segmentation=True`` in the ``test_fs.region_of_interest()`` function to True for this analysis to be carried out.


.. code:: python

    test_fs.roi_segmentation(bkg_multiplier=1, restart=False)

``bkg_multiplier`` (int) - an integer value applied to the backgound scans

``restart`` (bool) - if set to True this will reset all the segmentation data

If the program throws image_array doesnt exsist run create_imagearray(self)

If the program throws scan_background doesnt exsist run scan_background(self)

Analysis
--------

Allows the User to create new ROI maps for all the imported scans in the frameset. This will handle hot and
dead pixels as well as show the user the true gaussian distribution of the fields of view.


.. code:: python

    test_fs.region_of_interest(rows, columns,
                                med_blur_distance=9,
                                med_blur_height=100,
                                bkg_multiplier=1,
                                diff_segmentation=True,
                                slow=False)


``rows`` (int or tuple) - the total amount of rows the User would like to analyze 25 or (10,17)

``columns`` (int or tuple) - the total amount of columns the User would like to analyze 25 or (10,17)

``med_blur_distance`` (odd int) - the chunksize for the median_blur() function

``med_blur_height`` (int) - the amount above the mean to carry out a median blur - selective median_blur option only

``bkg_multiplier`` (int) - the multipler given to the backgound scans

``diff_segmentation`` (bool) - if False the program will skip the segmentation analysis

``slow`` (bool) - defaults to multiprocess data. If the program uses too much RAM the User can set this value to True
to slow down the analysis and save on RAM


Centroid Analysis
=================

The centroid analysis function can be called through

.. code:: python

    test_fs.centroid_analysis(rows,
                                columns,
                                med_blur_distance=9,
                                med_blur_height=10,
                                stdev_min=25,
                                bkg_multiplier=9)


``rows`` - total amount of rows in the scans - can also be a tuple of ints

``columns`` - total amount of columns in the scans - can also be a tuple of ints

``med_blur_distance`` (odd int) - the chunksize for the median_blur() function

``med_blur_height`` (int) - the amount above the mean to carry out a median blur - selective median_blur option only

``bkg_multiplier`` (int) - the multipler given to the backgound scans

``stdev_min`` (int) - the minimum standard deviation of a spectrum which is used to crop signals for centroid determination

``slow`` (bool) - defaults to multiprocess data. If the program uses too much RAM the User can set this value to True
to slow down the analysis and save on RAM


**Unsure About Dimension Size**

If you are unsure of the dimension sizes call ``self.frame_shape()``. The first number is the number of scans,
the second number is the about of rows + 1, and the third number is the number of columns + 1


**Difference Between slow=False and slow=True**

The above function calls one of two functions. Either the ``centroid_pixel_analysis()`` function and vectorizes it for
moderate run times with excellent RAM management (1-2GB). Or this will call the ``centroid_pixel_analysis_multi()``
function which will multiprocess the dataset, but uses considerably more RAM (6-8GB). Analysis route determine by slow
bool value.


**What Is The test_fs.results Variable**

Sets the ``test_fs.results`` value where the user can return the results of their analysis.
Outputs - [pixel position, spot diffraction pattern, median blurred x axis, median blurred y axis, truncated x axis
for centroid finding, x axis centroid value, truncated y axis for centroid finding, y axis centroid value,
summed diffraction intensity]

Retrieving Imported Data
========================

Return Detector Data
---------------------

.. code:: python

    return_det(file, scan_numbers, group='fluor', default=False)

Returns all information for a given detector channel for the array of scan numbers.

``file`` - test_fs.file

``scan_numbers`` - test_fs.scan_numbers

``group`` - Examples: filenumber, sample_theta, hybrid_x, hybrid_y, fluor, roi, mis

``default`` - if True this will default to the first fluorescence image

Centering Detector Data
------------------------

.. code:: python

    centering_det(self, group='fluor', center_around=False, summed=False, default=False)

This returns the User defined detector for all scans set in the self.scan_numbers and centers them around a User defined
centering scan index

``self`` - the SXDMFrameset

``group`` - a string defining the group value to be returned filenumber, sample_theta, hybrid_x, hybrid_y, fluor, roi

``center_around`` - if this is set to -1, arrays will not be shifted

``summed`` - if True this will return the summed returned detector value (summed accross all scans)

``default`` - if True this will choose the first fluor or first ROI


Show HDF5 File Groups
----------------------

.. code:: python

    h5group_list(file, group_name='base')

This allows the User to view the group names inside the hdf5 file. 'base' shows the topmost group. If it errors this
means you have hit a dataset and need to call the h5grab_data() function.

``file`` - test_fs.file

``group_name`` - /path/to/group/


Return HDF5 File Data
---------------------

.. code:: python

    h5grab_data(file, data_loc)

This will grab the data stored in a group. If it errors this means you are not in a dataset directory inside the hdf5
file.

``file`` - test_fs.file

``data_loc`` - /path/to/data


Show Alignment Data
--------------

.. code:: python

    grab_dxdy(self)

This returns the dx and dy centering values that are stored from the alignment function

``self`` - the SXDMFrameset


Read HDF5 Group Attributes 
--------------------------------------

.. code:: python

    h5read_attr(file, loc, attribute_name)

This returns the attribute value stored

``file`` - test_fs.file

``loc`` - '/path/to/group/with/attribute'

``attribute_name`` - 'the_attribute_name'



Find Frameset Dimensions
------------------

.. code:: python

    SXDMFrameset_object.frame_shape()


This returns the image dimensions for the SXDMFrameset class object


Calculate Background and FileNumber Locations
----------------

.. code:: python

    SXDMFrameset_object.ims_array()


This will auto load/calculate the background images and the image location array


Show Raw .tif Image Dimensions
----------------------------


.. code:: python

    SXDMFrameset_object.image_data_dimensions()

This will return the diffraction image dimensions