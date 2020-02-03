# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

import reach.backends
from reach import Cohort, Mouse, Session


## Project information

project = 'reach'
copyright = '2020, Matt Colligan'
author = 'Matt Colligan'
repo = 'https://github.com/m-col/reach'


## General configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.extlinks',
    'sphinx.ext.githubpages',
]

napoleon_google_docstring = False
napoleon_use_rtype = False

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
master_doc = 'index'
pygments_style = 'sphinx'


## Options for HTML output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# :repo:`text </path/>` hyperlinks to repo/path/
extlinks = {
    'repo': (f'{repo}/%s', 'repo ')
}

# replace |repo| with the repo string above
rst_epilog = f"""
.. |repo| replace:: {repo}
"""
