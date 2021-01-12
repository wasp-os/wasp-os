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
