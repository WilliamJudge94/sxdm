=============================
 Importing Data into SXDM
=============================
.. _submit an issue: https://github.com/WilliamJudge94/sxdm/issues

The first step in any SXDM workflow will be to **import the raw
data into a common format**. These importer functions are written as
needed: if your preferred beamline is not here, `submit an issue`_.


APS Beamline 26-ID-C
====================

Experimental Data (.mda) Import
-------------------------------

The raw data file ``file.mda`` given to the User at 26-ID-C saves all source
data as a matlab binary file. SXDM preserves the original ("source") file
and saves imported and processed data in a second ("destination") HDF file
to be used in later analysis. The source ``file.mda`` file can be easily
imported:

.. code:: python

   import_mda(mda_path='path/to/folder/holding/.mda_files',
                hdf5_save_directory='path/to/save/dir', 
                hdf5_save_filename='file')

This function will iterate through all ``scan.mda`` files in the `mda_folder` and import all
detector channel data into the User defined hdf5 destination/file.

.. code:: python

    # EXAMPLE

    import_mda(mda_path='/home/usr/Desktop/mda_folder/',
                hdf5_save_directory='/home/usr/Desktop',
                hdf5_save_filename='test_file')

.. note::

    Raw reader values are flipped and inverted to match 26-ID-C beamline MatLab
    Viewer output.

.. note::

    This importer is what creates the main *.h5 file.



Diffraction Image (.tif) Import
-------------------------------

The raw diffraction images ``image_#####.tif`` given to the User at 26-ID-C
will be imported based on the protocol below. SXDM preserves the original ("source")
file and saves imported and processed data in a second ("destination") HDF file
to be used in later analysis. All source ``image_#####.tif`` file can be easily imported:

.. code:: python

    import_images(
        file='path/to/save/dir/file.h5',
        images_loc='/path/to/master/images/directory',
        scans=False,
        fill_num=4,
        delete=False,
        import_type='uint32',
        delimiter_function=<function delimiter_func at 0x7f0873f3fe18>,
        force_reimport=False,
        )

This function will iterate through all folders in the ``images_loc`` folders and import all
``images_####.tif`` image data into the User defined hdf5 destination/file.

.. code:: python

    # EXAMPLE
    # /home/usr/Desktop/images_folder/scan_folder/image.tif

    import_images(
        file='/home/usr/Desktop/test_file.h5',
        images_loc='/home/usr/Desktop/images_folder/',
        scans=[1, 2, 10, 18],
        )

.. note::
    fill number is the number of digits in the image_####.tif name.

.. note::
    scans=False will import all scans in the designated folder. Must be either False or an array.

.. note::
    import_type gets passed into 'np.astype()' function

.. note::
    This will **Not** reimport the .tif images. If the User would like to do this they
    can set ``force_reimport=True``


Data Structure
==============

The main structure is similar to what is shown below:

.. code:: python

    #Main_HDF5_File#

        #images/
            #0001_scan/
                #000001.tif
                .
                .
                .
                #number.tif

            #0002_scan/
                #000001.tif
                .
                .
                .
                #number.tif

            #0003_scan/
                #000001.tif
                .
                .
                .
                #number.tif

        #mda/
            #0001_scan/
                #D01_channel/
                    #detector data
                .
                .
                .
                #D70_channel/
                    #detector data

            #0002_scan/
                #D01_channel/
                    #detector data
                .
                .
                .
                #D70_channel/
                    #detector data

            #0003_scan/
                #D01_channel/
                    #detector data
                .
                .
                .
                #D70_channel/
                    #detector data

        #detector_channels/
            #detector_scan/
            #filenumber/
            #fluor/
            #hybrid_x/
            #hybrid_y/
            #mis/
            #roi/
            #sample_theta/

        #zone_plate/
            #D_um/
            #d_rN_nm/
            #detector_pixel_size/

        #dataset_name1/
            #dxdy/
            #scan_numbers/
            #scan_theta/

        #dataset_name2/
            #dxdy/
            #scan_numbers/
            #scan_theta/

.. note::

    Please see `Analyzing the Data/Retrieving Imported Data` for more details
