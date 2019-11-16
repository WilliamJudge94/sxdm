===============
 Introduction 
===============

SXSM is a toolkit for interacting with Scanning X-ray microscopy data,
most likely collected at the Advanced Photon Source - Beamline 26-ID-C.
By collecting a set of frames at multiple incident angles, spectral/diffraction
maps  are reconstructed to provide chemical/strain insight. Although SXDM was not
designed for Fluorescence Mapping or XANES Mapping, built in functions allow
Users to easily handle datasets to fit their needs.

This project has the following design goals:

- Provide a python toolkit for analysis of X-ray diffraction frames.
- Store data in an open format for easy distribution.
- Provide framework 26-ID-C data handling.

GUI tools (eg. DUDE) exist for performing this type of
analysis. While convenient and more versatile, final setup and testing has not
been carried out. This module hopes to alleviate importing and
data analysis issues for the 26-ID-C beamline. SXDM does provide
an interactive GUI for visualizing the data, but this GUI
does not alter the data or export results. This way, the analysis
steps are captured either in an IPython notebook or conventional python
script. These steps, together with the original data, should then be
sufficient to reproduce the results exactly.


Installation
============

SXDM can be installed from the python package index (PyPI) using pip

.. code:: bash

   $ pip install sxdm

Development
===========

If you plan to contribute changes to `sxdm`, installing in developer
mode may be more your style. This will also allow you to run tests and
build documentation.

Installation
------------

Assuming you are using conda, here are the
steps. Any version of python >=3.5 should be ok.

.. code:: bash

   $ conda create -n sxdm python=3.6
   $ source activate sxdm
   $ git clone clone git@github.com:WilliamJudge94/sxdm.git
   $ pip3 install -r sxdm/requirements.txt
   $ pip3 install ipykernel
   $ ipython kernel install --user --name=sxdm

Jupyter
-------

Once in Jupyter the User may have to initiate the import through

.. code:: python

    import sys
    sys.path.append('/Users/usr/virtual_environment/lib/python3.6/site-packages/')

    %matplotlib qt
    import sys
    sys.path.append('/path/to/sxdm/folder')
    from sxdm import *

   
Tests
-----

The easiest way to run unit-tests is with python tester from the command line:

.. code:: bash

   $ pip install pytest
   $ pip install pytest-cov

   $ cd /dir/sxdm
   $ pytest --cov=sxdm tests/

Documentation
-------------

The documentation is built using sphinx. To make HTML documents, use the following:

.. code:: bash

   $ pip install sphinx
   $ cd /dir/sxdm/docs
   $ make html

Scanning X-Ray Diffraction Microscopy
=====================================

Coming soon...


Example Workflow
================

A typical procedure for interacting with microscope frame-sets involves the following parts:

- Import the raw data (.mda and .tif)
- Apply corrections and align the images
- Calculate some metric and create maps of it
- Visualize the maps, statically or interactively.

Example for a single frameset across difference X-ray incident angles:

.. code:: python

    %load_ext autoreload
    %autoreload 2
    %matplotlib qt


    # Developer Version
    import sys
    sys.path.append('/path/to/sxdm')
    # Developer Version


    from sxdm import *

    # Set file name
    hdf5_save_directory = '/dir/'
    hdf5_save_filename = 'test'

    # Importing .mda data
    import_mda(mda_path, hdf5_save_directory, hdf5_save_filename)

    # Importing .tif images - file='/dir/test.h5'
                                - was created by the import_mda() function
    import_images(file, images_loc)

    # Setting Detector Channels
    disp_det_chan(file)
    setup_det_chan(file, fluor, roi, detector_scan,
                    filenumber, sample_theta, hybrid_x, hybrid_y, mis)

    # Set up SXDMFrameset
    scan_numbers = [1, 2, 3, 4, 5, ...]
    dataset_name = 'Test_Name'
    test_fs = SXDMFrameset(file, dataset_name,
                            scan_numbers = scan_numbers, median_blur_algorithm='numpy')

    # Alignment
    test_fs.alignment()

    # Analysis
    test_fs.centroid_analysis()

    # Viewer
    test_fs.centroid_viewer()

