# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys
import os
import types
import django


sys.path.insert(0, os.path.abspath('../..'))

dummy_settings = types.ModuleType("dummy_settings")
sys.modules["dummy_settings"] = dummy_settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'dummy_settings'
django.setup()

project = 'Django Tg Bot Framework'
copyright = '2023, Devman'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.doctest',
    'sphinxcontrib.autodoc_pydantic',
    'sphinx.ext.viewcode',
    'sphinx.ext.autodoc.typehints',
    'sphinxcontrib_django2',
]

autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_field_summary = False
autodoc_typehints = 'description'
exclude_patterns = []
language = 'en'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
templates_path = ['_templates']

