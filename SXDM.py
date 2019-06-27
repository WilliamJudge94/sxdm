import warnings

from h5 import *
from det_chan import *
from importer import *
from mis import *
from clicks import *
from preprocess import *
from multi import *
from multi_update import *
from pixel import *
from alignment import *
from logger import *
from viewer import *
from postprocess import *
from chi_determination import *
from roi_bounding import *
from roi import *
from summed2d import *

from tqdm import tqdm


class SXDMFrameset():

    def __init__(self, file, dataset_name,
                  scan_numbers=False, fill_num=4, restart_zoneplate=False):

        self.file = file
        self.dataset_name = dataset_name

        initialize_scans(self, scan_numbers=scan_numbers, fill_num=fill_num)
        initialize_group(self)

        initialize_zoneplate_data(self, reset=restart_zoneplate)
        initialize_experimental_attrs(self)
        initialize_saving(self)
        initialize_logging(self)

        shape_check(self)
        resolution_check(self)

    def alignment(self, reset=False):
        """Allows the user to align all scans based on Fluorescence Maps or ROI Maps

        Parameters
        ==========
        reset (bool)
            if True this will clear all the alignment data. Use this when adding new scans to a group

        Returns
        =======
        Nothing - sets alignment data

        """
        self.log.info('Starting self.alignment')

        if reset == True:
            reset_dxdy(self)

        alignment_function(self)

        self.log.info('Ending self.alignment')

    def gaus_checker(self, center_around=False, default=False):
        """Plots total diffraction intensity vs scan angle for a set ROI

        Parameters
        ==========
        center_around (bool)
            if True this will default the centerind index to the first index (0)
        default (bool)
            if True this will default the roi to check the gaus of to the first user defined ROI

        Returns
        =======
        Nothing - displays the total intensity vs scan theta rocking curve
        """

        self.log.info('Starting self.gaus_checker')

        x, y = gaus_check(self, center_around=center_around, default=default)
        self.mda_roi_gaus_check = (x, y)
        plt.plot(x, y)
        plt.xlabel('Sample Angle (Degrees)')
        plt.ylabel('Relative Intensity')

        self.log.info('Ending self.gaus_checker')

    def chi_determination(self):
        """Determine the axis bounds for the diffraction images

        """

        self.log.info('Starting self.chi_determination')

        self.user_rocking_check = False
        while self.user_rocking_check == False:
            self.user_rocking = str(input("What Are You Rocking For The Chi Determination? "
                                          "The Sample or Detector? spl/det - "))
            self.user_rocking_check = self.user_rocking in ['det', 'spl']
        chi_function(self)

        self.log.info('Ending self.chi_determination')

    def roi_segmentation(self, bkg_multiplier=1, restart=False):
        """Allows the User to create a summed diffraction pattern bounding box for region_of_interest analysis

        Parameters
        ==========
        bkg_multiplier (int)
            the scaler applied to the background images
        restart (bool)
            if True this clears all bounding boxes when loading the segmentation data

        Returns
        =======
        Nothing
        """
        self.log.info('Starting self.roi_segmentation')

        try:
            if restart==True:
                dif_im = summed2d_all_data(self=self, bkg_multiplier=bkg_multiplier)
                self.dif_im = dif_im

            else:
                dif_im = self.dif_im
        except:
            dif_im = summed2d_all_data(self=self, bkg_multiplier=bkg_multiplier)
            self.dif_im = dif_im
        roi, rs = start_bounding_box(dif_im, self)
        self.rando1 = roi
        self.rando2 = rs

        self.log.info('Ending self.roi_segmentation')

    def region_of_interest(self, rows, columns, med_blur_distance=9,
                           med_blur_height=100, bkg_multiplier=1, diff_segmentation=True, slow=False):
        """Create a region of interest map for each scan and center the region of interest maps.
        If the diff segmentation is True this will also create a region of interest map based on
        a user defined sub region of interests

        Parameters
        ==========
        rows (int) or (tup)
            the total amount of rows the user wants to do analysis on
        columns (int) or (tup)
            the total amount of columns the user wants to do analysis on
        med_blur_distance (int)
            the amount of values to scan for median blur
        med_blur_height (int)
            the height cut off for the median blur
        bkg_multiplier (int)
            multiplier for the background signal to be subtracted
        diff_segmentation (bool)
            if set to True this will determine region of interests maps for sub roi's set
            by the user

        Returns
        =======
        the roi results in self.roi_results

            [(row, column), idxs,
               raw_scan_data, corr_scan_data, scan_data_roi_vals,
               summed_data, corr_summed_data, summed_data_roi_vals]
        """

        self.log.info('Starting self.region_of_interest')

        # Setting total rows and columns for the roi_viewer
        self.roi_analysis_total_rows = rows
        self.roi_analysis_total_columns = columns

        if slow == True:
            self.roi_results = roi_analysis(self, rows, columns, med_blur_distance=med_blur_distance,
                                        med_blur_height=med_blur_height, multiplier=bkg_multiplier,
                                        center_around=1, diff_segmentation=diff_segmentation)
        else:
            self.roi_results = roi_analysis_multi(self, rows=rows, columns=columns, med_blur_distance=med_blur_distance,
                                                med_blur_height=med_blur_height, bkg_multiplier=bkg_multiplier,
                                                 diff_segments=diff_segmentation)

        if False in self.roi_results:
            warnings.warn('RAM Usage Too High. ROI Analysis Stopped')
        self.roi_analysis_params = [med_blur_distance, med_blur_height, bkg_multiplier]

        print('Results Stored As self.roi_results')

        self.log.info('Ending self.region_of_interest')

    def roi_viewer(self):
        """Takes the self.roi_results variable and displays it in a GUI format

        Parameters
        ==========
        self (SXDMFrameset)
            the sxdmframeset object

        Returns
        =======
        Nothing
        """
        self.log.info('Starting self.roi_viewer')

        initiate_roi_viewer(self)

        self.log.info('Ending self.roi_viewer')

    def centroid_analysis(self, rows, columns, med_blur_distance=9,
                 med_blur_height=10, stdev_min=25, bkg_multiplier=1, slow=False):
        """Calculates spot diffraction and data needed to make 2theta/chi/roi maps

        Parameters
        ==========

        rows: (int)
            the total number of rows you want to iterate through
        columns: (int)
            the total number of columns you want to iterate through
        med_blur_distance: (int)
            the amount of values to scan for median blur
        med_blur_height:  (int)
            the height cut off for the median blur
        stdev_min: (int)
            standard deviation above the mean of signal to ignore
        bkg_multiplier: (int)
            multiplier for the background signal to be subtracted

        Returns
        =======
        the analysis results in the form of self.results
        """

        try:
            dummy = self.image_array
        except:
            create_imagearray(self)

        self.log.info('Starting self.centroid_analysis')

        self.analysis_total_rows = rows
        self.analysis_total_columns = columns


        if slow == True:
            self.results = best_analysis(self, rows, columns, med_blur_distance=med_blur_distance,
                                        med_blur_height=med_blur_height, stdev_min=stdev_min, multiplier=bkg_multiplier,
                                        center_around=1)
        else:
            self.results = centroid_analysis_multi(self, rows=rows, columns=columns, med_blur_distance=med_blur_distance,
                                                med_blur_height=med_blur_height, stdev=stdev_min, bkg_multiplier=bkg_multiplier)

        if False in self.results:
            warnings.warn('RAM Usage Too High. Centroid Analysis Stopped')
        self.analysis_params = [med_blur_distance, med_blur_height, stdev_min, bkg_multiplier]

        print('Results Stored As self.results')

        self.log.info('Ending self.centroid_analysis')

    def save(self):
        """Save self.results (Centroid Data) to _savedata.h5

        Unable to efficiently save ROI data
        """

        self.log.info('Starting self.save')

        save_filename = self.file[0:-3] + '_savedata.h5'
        self.save_file = save_filename
        acceptable_values = ['row_column', 'summed_dif', 'ttheta', 'chi', 'ttheta_corr', 'ttheta_centroid', 'chi_corr',
                         'chi_centroid', 'full_roi']

        h5set_attr(save_filename, self.dataset_name, 'Analysis Parameters', self.analysis_params)

        for value in tqdm(acceptable_values):
            pre_data = pooled_return(self.results, value)
            readable_results = []
            for data in pre_data:
                readable_results.append(data)
            readable_results2 = np.asarray(readable_results)

            try:
                h5create_dataset(save_filename, self.dataset_name + '/{}'.format(value), np.asarray(readable_results2))
            except:
                h5replace_data(save_filename, self.dataset_name + '/{}'.format(value), np.asarray(readable_results2))

        self.log.info('Ending self.save')

    def centroid_viewer(self):
        """Allow the user to view the data in a convenient format

        Parameters
        ==========

        diffraction_load (bool)
            if True this will load all necessary data for the diffraction
            will take up at least 2gb of RAM

        Returns
        =======
        Nothing - displays viewer
        """

        # Depreciated code would not import the diffraction patterns to save RAM
        # Steps have been taken to never fully load all diffraction patterns
        # diffraction_load variable will be phased out in future versions
        diffraction_load = True

        self.log.info('Starting self.centroid_viewer')

        warnings.warn('The Starting Parameters In The Viewer May Not Be Identical The Parameters Used For The Analysis')
        try:
            fluor_image = centering_det(self)
            fluor_image = fluor_image[0]
        except:
            fluor_image = sum_error()
        self.diffraction_load = diffraction_load
        run_viewer(self, fluor_image)

        self.log.info('Ending self.centroid_viewer')

    def reload_save(self, summed_dif_return=True):
        """Allow the user to reload Centroid saved data

        Parameters
        ==========

        summed_dif_return (bool)
            if True this will load all necessary data for the diffraction
            will take up at least 2gb of RAM

        Returns
        =======
        Nothing
        """

        self.log.info('Starting self.reload_save')

        self.save_filename = self.file[0:-3] + '_savedata.h5'
        self.results = saved_return(self.save_filename, self.dataset_name, summed_dif_return=summed_dif_return)
        self.analysis_params = h5read_attr(self.save_filename, self.dataset_name, 'Analysis Parameters')

        self.log.info('Ending self.reload_save')
