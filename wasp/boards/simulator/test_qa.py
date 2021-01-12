import pytest
import wasp
import os

EXCLUDE = ('Notifications', 'Template', 'Demo')

def test_screenshot(constructor):
    if constructor.NAME in EXCLUDE:
        return
    fname = f'res/{constructor.NAME}App.png'.replace(' ', '')
    assert os.path.exists(fname)

def test_screenshot_README(constructor):
    if constructor.NAME in EXCLUDE:
        return
    fname = f'res/{constructor.NAME}App.png'.replace(' ', '')
    
    with open('README.rst') as f:
        readme = f.read()
    assert fname in readme

def test_apps_documented(constructor):
    if constructor.NAME in EXCLUDE:
        return

    with open('docs/apps.rst') as f:
        appdoc = f.read()
    with open('docs/wasp.rst') as f:
        waspdoc = f.read()

    needle = f'.. automodule:: {constructor.__module__}'
    assert needle in appdoc or needle in waspdoc

    if needle in waspdoc:
        assert constructor.__name__ in appdoc
