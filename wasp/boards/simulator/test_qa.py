import pytest
import wasp
import importlib
import os
from PIL import Image

EXCLUDE = ('NotificationApp', 'PagerApp', 'TemplateApp', 'FacesApp', 'ReadMeApp')

def test_screenshot(constructor):
    if f'{constructor.__name__}' in EXCLUDE or f'{constructor.__module__}'.startswith('apps.user.'):
        return

    fname = f'res/screenshots/{constructor.__name__}.png'.replace(' ', '')

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
    if f'{constructor.__name__}' in EXCLUDE or f'{constructor.__module__}'.startswith('apps.user.'):
        return

    fname = f'res/screenshots/{constructor.__name__}.png'.replace(' ', '')

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
    if f'{constructor.__name__}' in EXCLUDE or f'{constructor.__module__}'.startswith('apps.user.'):
        return

    with open('docs/apps.rst') as f:
        appdoc = f.read()
    with open('docs/wasp.rst') as f:
        waspdoc = f.read()

    # Every application must be listed in the Application Library
    needle_system = f'.. automodule:: {constructor.__module__}'.replace('apps.system.', '')
    needle_user_defined = f'.. automodule:: {constructor.__module__}'.replace('apps.', '')
    needle_watch_faces = f'.. automodule:: {constructor.__module__}'.replace('watch_faces.', '')
    assert needle_system in appdoc or needle_user_defined in appdoc or needle_watch_faces in appdoc

def test_app_naming(constructor):
    # The class name of every app must be the PascalCase version of its file name in snake_case appended with "App"
    if f'{constructor.__name__}' in EXCLUDE or f'{constructor.__module__}'.startswith('apps.user.'):
        return

    module = f'{constructor.__module__}'
    if module.startswith('apps.system.'):
        assert _snake_case_to_pascal_case(module.replace('apps.system.', '')) + 'App' == f'{constructor.__name__}'
    elif module.startswith('apps.'):
        assert _snake_case_to_pascal_case(module.replace('apps.', '')) + 'App' == f'{constructor.__name__}'
    elif module.startswith('watch_faces.'):
        assert _snake_case_to_pascal_case(module.replace('watch_faces.', '')) + 'App' == f'{constructor.__name__}'


def test_docstrings(constructor):
    if f'{constructor.__name__}' in EXCLUDE or f'{constructor.__module__}'.startswith('apps.user.'):
        return

    fname = f'res/screenshots/{constructor.__name__}.png'.replace(' ', '')

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

def _snake_case_to_pascal_case(s):
        out = ''
        for word in s.split('_'):
            out = out + word[:1].upper() + word[1:]
        return out