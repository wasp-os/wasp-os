# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../wasp'))
sys.path.insert(0, os.path.abspath('../apps'))
sys.path.insert(0, os.path.abspath('../watch_faces'))
sys.path.insert(0, os.path.abspath('../wasp/boards/sphinx'))


# -- Project information -----------------------------------------------------

project = 'WASP-OS'
copyright = '2020, Daniel Thompson'
author = 'Daniel Thompson'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.graphviz',
]

# Add any paths that contain templates here, relative to this directory.
#templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'shibuya'
html_theme_options = {
    'accent_color': 'amber',
    'github_url': 'https://github.com/wasp-os/wasp-os',
    'nav_links': [
        {'title': 'Install', 'url': 'install'},
        {'title': 'Apps', 'url': 'apps'},
        {'title': 'Builds', 'url': 'https://wasp-os.org/', 'external': True},
    ],
    'show_ai_links': False,
}
# "Edit this page" in the sidebar
html_context = {
    'source_type': 'github',
    'source_user': 'wasp-os',
    'source_repo': 'wasp-os',
    'source_version': 'main',
    'source_docs_path': '/docs/',
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']
html_logo = 'logo.png'
