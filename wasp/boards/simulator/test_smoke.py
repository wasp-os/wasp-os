import pytest
import time
import wasp

def step():
    wasp.system._tick()
    wasp.machine.deepsleep()
wasp.system.step = step

def play(appname):
    system = wasp.system
    system.switch(system.apps[appname])
    for i in range(4):
        system.step()
        time.sleep(0.125)
    system.switch(system.quick_ring[0])
wasp.system.play = play

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

def test_steps(system):
    system.play('Steps')

def test_timer(system):
    system.play('Timer')

def test_heart(system):
    system.play('Heart')

def test_self_test(system):
    system.play('Self Test')

def test_settings(system):
    system.play('Settings')

def test_torch(system):
    system.play('Torch')
