import glob
import importlib
import inspect
import pytest
import pprint
import json

def discover_app_constructors():
    apps = []
    appClasses = []

    globs_system = glob.glob('wasp/apps/system/*.py')
    names_system = [ g[5:-3].replace('/', '.') for g in globs_system ]
    globs_user = glob.glob('apps/*.py')
    names_user = [ g[:-3].replace('/', '.') for g in globs_user ]
    globs_watchface = glob.glob('watch_faces/*.py')
    names_watchface = [ g[:-3].replace('/', '.') for g in globs_watchface ]
    modules = [ importlib.import_module(n) for n in names_system + names_user + names_watchface ]

    for m in modules:
        for sym in m.__dict__.keys():
            if len(sym) > 3 and sym[-3:] == 'App' and not sym in appClasses:
                constructor = m.__dict__[sym]
                sig = inspect.signature(constructor)
                if len(sig.parameters) == 0:
                    apps.append(constructor)
                    appClasses.append(sym)

    return apps

def pytest_generate_tests(metafunc):
    if 'constructor' in metafunc.fixturenames:
         metafunc.parametrize('constructor', discover_app_constructors())
