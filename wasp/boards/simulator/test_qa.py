import pytest
import wasp
import importlib
import os
from PIL import Image

EXCLUDE = ('Notifications', 'Template', 'Faces', 'ReadMe')

def test_screenshot(constructor):
    if constructor.NAME in EXCLUDE:
        return
    fname = f'res/{constructor.NAME}App.png'.replace(' ', '')

    # Every application requires a screenshot be captured for use in the
    # documentation. The screenshots must conform to standard dimensions
    # and have a specific name. The apps are shown in a grid at
    # https://wasp-os.readthedocs.io/en/latest/README.html#screenshots
    # so your app will look untidy if it does not use the same dimensions
    # as the others.
    #
    # Press 's' in the simulator to capture a screenshot that meets these
    # requirements.
    with Image.open(fname) as screenshot:
        assert screenshot.width == 358
        assert screenshot.height == 406

def test_README(constructor):
    if constructor.NAME in EXCLUDE:
        return
    fname = f'res/{constructor.NAME}App.png'.replace(' ', '')

    with open('README.rst') as f:
        readme = f.readlines()

    # Get the offset (or offsets) of that fname within the file
    offsets = [i for i, ln in enumerate(readme) if fname in ln]

    # Every app must have its screenshot included in the README image
    # gallery.
    assert len(offsets) >= 1

    for offset in offsets:
        # Paranoid self-test of the test code
        assert fname in readme[offset]

        # There must be alt text attached to every instance of the
        # screenshot (and it must be on the line following the
        # screenshot.
        assert ':alt:' in readme[offset+1]

        # The width must be set to 179 (e.g. half the true size). The
        # watch is a HiDPI device and HTML pixel width coordinates are
        # based on a low value DPI. Thus we need to scale them on older
        # displays for them to look right (a browser on a HiDPI laptop
        # will do the right thing and not downscale).
        assert ':width: 179' in readme[offset+2]

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

    # Screenshots should *not* be included in the constructor doc
    # strings.
    if constructor.__doc__:
        assert fname not in constructor.__doc__

    # Screenshots must be included in the full module documentation
    assert f'.. figure:: {fname }' in module_doc

    # The width must be set to 179 (e.g. half the true size). The
    # watch is a HiDPI device and HTML pixel width coordinates are
    # based on a low value DPI. Thus we need to scale them on older
    # displays for them to look right (a browser on a HiDPI laptop
    # will do the right thing and not downscale).
    #
    # Note that this can be a looser test than the one for the
    # README because there shouldn't be too many other images in
    # the class docstrings.
    assert ':width: 179' in module_doc

    # The second line of the module documentation should be an
    # underline (e.g. the first line must be a section header)
    assert(module_doc.split('\n')[1].startswith('~~~~'))
