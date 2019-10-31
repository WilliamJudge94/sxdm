SXDM
=======


SXDM is a library for analyzing Scanning X-Ray Diffraction Micriscopy data
for materials science, chemistry and similar fields. The major focus is on
Scanning Micriscopy frames collected at multiple incident angles. One can
import, retrieve, and analyze 26 - ID - C datasets all from a Python format.


Motivation & Features
---------------------

- Importing and analysis of scanning x-ray diffraction microscopy framesets
- Analysis of scanning x-ray diffraction microscopy (centroids & region of interest)


Installation
------------

# Clone the GitHub Repository
Make a clone of the SXDM project onto your machine
Possibly create a virtaul environment
Run the requirements.txt file

# Making a Virtual Environment
cd to directory you would like to keep the virtual environment
run python3 -m venv projectname in the terminal projectname can be anything the User would like it to be
run source projectname/bin/activate
pip3 install ipykernel
ipython kernel install --user --name=projectname
pip3 install -r requirements.txt
run import sys and sys.path.append("/path/to/module/") in jupyter notebook shell

if you are running on a Mac then import sys

sys.path.append('/Users/will/tf/lib/python3.7/site-packages/')


Usage
-----

Please see the SXDM_Manual.ipnb for more details


License
-------

This project is released under the `GNU General Public License version 3`_.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

.. _GNU General Public License version 3: https://www.gnu.org/licenses/gpl-3.0.en.html
