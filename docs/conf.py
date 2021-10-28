# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.


import os
import sys
import numpy as np
from unittest import mock

sys.path.insert(0, os.path.abspath('../'))
# -- Project information -----------------------------------------------------
import sphinx_rtd_theme

if False:
    autodoc_mock_imports = ['_tkinter', 'pandas', 'scipy.optimize', 'numpy', 'h5py',]
    for mod_name in autodoc_mock_imports:
        sys.modules[mod_name] = mock.Mock()

master_doc = 'index'

project = 'SXDM Documentation'
copyright = '2019, William Judge'
author = 'William Judge'

# The full version, including alpha/beta/rc tags
def read(fname):
    og_fname = os.path.join(os.path.dirname(__file__))
    og_fname2 = og_fname.split('/')[:-1]
    return open(os.path.join('/'.join(og_fname2)+'/', fname)).read()

release = read('VERSION.txt')


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    "sphinx_rtd_theme",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']

latex_documents = [
    (master_doc, 'sxdm.tex', 'SXDM Documentation',
     author, 'manual'),
]

epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright