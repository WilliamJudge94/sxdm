import unittest
from unittest import TestCase, mock
import os

from h5 import *

class H5TestCase(TestCase):
    def test_h5create_file(self):
        h5create_file('./')
        file_check = os.path.isfile('./test.h5')
        self.assertTrue(file_check)

    def test_h5create_group(self):
        h5create_group('./test.h5','group1/group2')
