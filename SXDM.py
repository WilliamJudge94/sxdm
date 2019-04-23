from h5 import *
from det_chan import *
from importer import *
from mis import *
from clicks import *
from preprocess import *
from multi import *
from pixel import *
from alignment import *
from logger import *
from viewer import *

from tqdm import tqdm

class SXDMFrameset():

    def __init__ (self, file, dataset_name, scan_numbers = False, fill_num = 4, restart_zoneplate = False):

        self.file = file
        self.dataset_name = dataset_name

        initialize_zoneplate_data(self, reset = restart_zoneplate)
        initialize_experimental_attrs(self)
        initialize_saving(self)
        initialize_logging(self)
        initialize_scans(self, scan_numbers = scan_numbers, fill_num = fill_num)


        shape_check(self)
        resolution_check(self)
        initialize_group(self)

    def alignment(self):
        """Allows the user to align all scans based on Fluorescence Maps or ROI Maps

        :return:
        """
        alignment_function(self)

    def gaus_checker(self):
        """Plots total diffraction intensity vs scan angle

        :return:
        """
        x, y = gaus_check(self)
        plt.plot(x,y)
        plt.xlabel('Sample Angle (Degrees)')
        plt.ylabel('Relative Intensity')

    def chi_determination(self):
        pass

    def analysis(self, rows, columns, med_blur_distance = 4,
                 med_blur_height = 10, stdev_min = 35, bkg_multiplier = 1):
        """Calculates spot diffraction and data needed to make 2theta/chi/roi maps

        :param rows: (int) the total number of rows you want to iterate through
        :param columns: (int) the total number of columns you want to iterate through
        :param med_blur_distance: (int) the amount of values to scan for median blur
        :param med_blur_height:  (int) the height cut off for the median blur
        :param stdev_min: (int) standard deviation above the mean of signal to ignore
        :param bkg_multiplier: (int) multiplier for the background signal to be subtracted
        :return:
        """
        self.results = best_analysis(self, rows, columns, med_blur_distance=med_blur_distance,
                                     med_blur_height=med_blur_height, stdev_min=stdev_min, multiplier=bkg_multiplier)

        print('Results Stored As self.results')

    def viewer(self):
        pass

    def save(self):
        save_filename = self.file[0:-3] + '_savedata.h5'
        self.save_file = save_filename
        acceptable_values = ['row_column', 'summed_dif', 'ttheta', 'chi', 'ttheta_corr', 'ttheta_centroid','chi_corr',
                         'chi_centroid', 'full_roi']
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

    def viewer(self):
        try:
            fluor_image = centering_det(self)
        except:
            fluor_image = 'default'

        run_viewer(self.results, fluor_image[0])

