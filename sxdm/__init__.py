import sys
import os
import numpy as np
import h5py
import imageio
import os
from tqdm import tqdm_notebook as tqdm
import matplotlib.pyplot as plt
import warnings
from functools import partial

from scipy.ndimage import shift
from matplotlib.patches import Circle
from matplotlib.widgets import Button, TextBox

# Make sure this directory is in python path for imports
sys.path.append(os.path.dirname(__file__))
#export PYTHONPATH="$PYTHONPATH:/path/to/module" run in terminal

from alignment import *
from background import *
from clicks import *
from chi_determination import *
from det_chan import *
from h5 import *
from importer import *
from logger import *
from mis import *
from multi import *
from multi_update import *
from pixel import *
from postprocess import *
from preprocess import *
from roi import *
from roi_bounding import *
from SXDM import *
from summed2d import *
from viewer import *
from readingmda import *
from generalize import *

def get_sxdm_test_data_location():
    """Obtaining the folder locaitons of the test data.

    Returns
    -------
    the mda_location, the images_location
    """
    base = f'{os.path.dirname(__file__)[:-4]}tests/test_data/'
    mda_data = f'{base}data/'
    images = f'{base}images/'
    return mda_data, images

def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    """Warning formatter
    """
    return ' %s:%s: %s:%s' % (filename, lineno, category.__name__, message)

warnings.formatwarning = warning_on_one_line