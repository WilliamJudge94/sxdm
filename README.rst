SXDM v0.7
==========

.. image:: https://travis-ci.org/WilliamJudge94/sxdm.svg?branch=master
    :target: https://travis-ci.org/WilliamJudge94/sxdm
.. image:: https://coveralls.io/repos/github/WilliamJudge94/sxdm/badge.svg?branch=master
    :target: https://coveralls.io/github/WilliamJudge94/sxdm?branch=master
.. image:: https://readthedocs.org/projects/sxdm/badge/?version=latest
   :target: http://sxdm.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation status



SXDM is a library for analyzing Scanning X-Ray Diffraction Microscopy data
for materials science, chemistry and similar fields. The major focus is on
Scanning Microscopy frames collected at multiple incident angles. One can
import, retrieve, and analyze 26 - ID - C datasets all from a Python format.


Motivation & Features
---------------------

- Importing and analysis of scanning x-ray diffraction microscopy framesets
- Analysis of scanning x-ray diffraction microscopy (centroids, region of interest, and general user analysis)


Installation (pip)
------------------

- `pip install sxdm`


Developer Installation (git)
----------------------------

- conda create -n sxdm python=3.6
- source activate sxdm
- git clone clone git@github.com:WilliamJudge94/sxdm.git
- pip3 install -r sxdm/requirements.txt
- pip3 install ipykernel
- ipython kernel install --user --name=sxdm

Developer Virtual Environment & Jupyter Setup (git)
---------------------------------------------------

**Run Commands In Jupyter Shell**


- `%matplotlib qt`
- `import sys`

**Linux**
- `sys.path.append('/path/to/sxdm/folder')`

**MacOS**
- `sys.path.append('/Users/usr/virtual_environment/lib/python3.7/site-packages/')`


- `from sxdm import *`



Usage
-----

Please see the https://sxdm.readthedocs.io/en/latest/ for more details


License
-------

This project is released under the `GNU General Public License version 3`_.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

.. _GNU General Public License version 3: https://www.gnu.org/licenses/gpl-3.0.en.html
