import pytest
import wasp
import importlib
import os

EXCLUDE = ('Notifications', 'Template', 'Faces', 'ReadMe')

def test_README(constructor):
    if constructor.NAME in EXCLUDE:
        return
    fname = f'res/{constructor.NAME}App.png'.replace(' ', '')

    # A screenshot must exist for every application (press 's' in the
    # simulator)
    assert os.path.exists(fname)

    # Every screenshot must be included in the README image gallery
    with open('README.rst') as f:
        readme = f.read()
    assert fname in readme

def test_app_library(constructor):
    if constructor.NAME in EXCLUDE:
        return

    with open('docs/apps.rst') as f:
        appdoc = f.read()
    with open('docs/wasp.rst') as f:
        waspdoc = f.read()

    # Every application must be listed in the Application Library
    needle_system = f'.. automodule:: {constructor.__module__}'
    needle_user_defined = f'.. automodule:: {constructor.__module__}'.replace('apps.', '')
    assert needle_system in appdoc or needle_user_defined in appdoc

def test_docstrings(constructor):
    if constructor.NAME in EXCLUDE:
        return
    fname = f'res/{constructor.NAME}App.png'.replace(' ', '')

    class_doc = constructor.__doc__
    module_doc = importlib.import_module(constructor.__module__).__doc__

    # Screenshots should *not* appear in the constructor.
    if constructor.__doc__:
        assert fname not in constructor.__doc__

    # Screenshots should appear in the full module documentation
    assert f'.. figure:: {fname }' in module_doc

    # The second line of the module documentation should be an
    # underline (e.g. the first line must be a section header)
    assert(module_doc.split('\n')[1].startswith('~~~~'))
