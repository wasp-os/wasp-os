import pytest
import time
import wasp

def step():
    wasp.system._tick()
    wasp.machine.deepsleep()
    time.sleep(0.1)
wasp.system.step = step

wasp.system.apps = {}
for app in wasp.system.quick_ring + wasp.system.launcher_ring:
    wasp.system.apps[app.NAME] = app

@pytest.fixture
def system():
    system = wasp.system
    if system.app != system.quick_ring[0]:
        system.switch(system.quick_ring[0])
    system.step()

    return system

def test_step(system):
    system.step()

def test_quick_ring(system):
    names = [ x.NAME for x in system.quick_ring ]
    assert('Clock' in names)
    assert('Steps' in names)
    assert('Timer' in names)
    assert('Heart' in names)

def test_launcher_ring(system):
    names = [ x.NAME for x in system.launcher_ring ]
    assert('Self Test' in names)
    assert('Settings' in names)
    assert('Torch' in names)

@pytest.mark.parametrize("name",
        ('Steps', 'Timer', 'Heart', 'Self Test', 'Settings', 'Torch'))
def test_app(system, name):
    system.switch(system.apps[name])
    for i in range(4):
        system.step()
    system.switch(system.quick_ring[0])

def test_stopwatch(system):
    system.switch(system.apps['Timer'])

    system.step()

    wasp.watch.button.value(0)
    system.step()
    assert(system.app._started_at > 0)
    wasp.watch.button.value(1)

    system.step()
    system.step()
    system.step()

    wasp.watch.button.value(0)
    system.step()
    assert(system.app._started_at == 0)
    wasp.watch.button.value(1)

    system.step()
