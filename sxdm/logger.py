import logging
import os

def initialize_logging(self):
    """Initiate logging

    Not set up
    """
    log_filename = './sxdm.log'
    if os.path.isfile(log_filename) == False:
        f = open(log_filename, "w+")
        f.close()

    log = logging.getLogger(__name__)

    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        filemode="a",
        format='%(asctime)s │ %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')

    self.log = log