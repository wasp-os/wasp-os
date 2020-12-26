import glob
import importlib
import inspect
import pytest

def discover_app_constructors():
    apps = []

    globs = glob.glob('wasp/apps/*.py')
    names = [ g[5:-3].replace('/', '.') for g in globs ]
    modules = [ importlib.import_module(n) for n in names ]

    for m in modules:
        for sym in m.__dict__.keys():
            if len(sym) > 3 and sym[-3:] == 'App':
                constructor = m.__dict__[sym]
                sig = inspect.signature(constructor)
                if len(sig.parameters) == 0:
                    apps.append(constructor)

    return apps

def pytest_generate_tests(metafunc):
    if 'constructor' in metafunc.fixturenames:
         metafunc.parametrize('constructor', discover_app_constructors())
