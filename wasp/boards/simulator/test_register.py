# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Michiel W. Beijen

"""Registering applications must never stop the watch from booting."""

import sys
import types

import pytest

import appregistry
import apps
import wasp

class BrokenApp():
    NAME = 'Broken'

    def __init__(self):
        raise MemoryError('memory allocation failed, allocating 4096 bytes')

@pytest.fixture
def broken_app(monkeypatch):
    """An importable application whose constructor runs out of memory."""
    module = types.ModuleType('apps.broken')
    module.BrokenApp = BrokenApp
    monkeypatch.setitem(sys.modules, 'apps.broken', module)
    monkeypatch.setattr(apps, 'broken', module, raising=False)
    return 'apps.broken.BrokenApp'

@pytest.fixture
def reported(monkeypatch):
    """The exceptions handed to sys.print_exception()."""
    seen = []
    monkeypatch.setattr(sys, 'print_exception', lambda e, *args: seen.append(e))
    return seen

def test_register_raises_without_no_except(reported):
    system = wasp.Manager()
    with pytest.raises(ImportError):
        system.register('apps.does_not_exist.NopeApp')
    assert not system.launcher_ring
    assert not system.quick_ring
    assert not reported

def test_register_reports_a_failed_import(reported):
    system = wasp.Manager()
    system.register('apps.does_not_exist.NopeApp', no_except=True)
    assert not system.launcher_ring
    assert not system.quick_ring
    assert len(reported) == 1
    assert isinstance(reported[0], ImportError)

def test_register_reports_a_failed_constructor(broken_app, reported):
    system = wasp.Manager()
    system.register(broken_app, no_except=True)
    assert not system.launcher_ring
    assert not system.quick_ring
    assert len(reported) == 1
    assert isinstance(reported[0], MemoryError)

def test_register_defaults_skips_what_cannot_load(monkeypatch, broken_app, reported):
    face = appregistry.autoload_list[0]
    monkeypatch.setattr(appregistry, 'autoload_list', (
        ('apps.does_not_exist.NopeApp', True, False, False),
        (broken_app, False, False, False),
        face,
    ))
    system = wasp.Manager()
    system.register_defaults()

    # The watch face and the system apps are there, the broken ones are not
    names = [app.NAME for app in system.quick_ring + system.launcher_ring]
    assert system.quick_ring
    assert 'Broken' not in names
    assert 'Settings' in names
    assert len(reported) == 2
    assert isinstance(reported[0], ImportError)
    assert isinstance(reported[1], MemoryError)
