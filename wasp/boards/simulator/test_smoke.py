import pytest
import time
import wasp

def step():
    wasp.system._tick()
    wasp.machine.deepsleep()
    time.sleep(0.1)
wasp.system.step = step

wasp.watch.touch.press = wasp.watch.touch.i2c.sim.press
wasp.watch.touch.swipe = wasp.watch.touch.i2c.sim.swipe

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

def test_constructor(system, constructor):
    # Special case for the notification app
    if 'NotificationApp' in str(constructor):
         wasp.system.notify(wasp.watch.rtc.get_uptime_ms(),
             {
                 "src":"testcase",
                 "title":"A test",
                 "body":"This is a long message containingaverylongwordthatdoesnotfit and lots of other contents as well."
             })

    try:
        system.switch(constructor())
        system.step()
        system.step()
        wasp.watch.touch.press(120, 120)
        system.step()
        system.step()
        system.switch(system.quick_ring[0])
    except FileNotFoundError:
        # Some apps intend to generate exceptions during the constructor
        # if they don't have required files available
        if 'HaikuApp' not in str(constructor):
            raise

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

def test_selftests(system):
    """Walk though each screen in the Self Test.

    This is a simple "does it crash" test and the only thing we do to stimulate
    the app is press in the centre of the screen. For most of the tests that
    will do something useful! For example it will run the benchmark for every
    one of the benchmark tests.
    """
    system.switch(system.apps['Self Test'])
    system.step()

    start_point = system.app.test

    for i in range(len(system.app.tests)):
        wasp.watch.touch.press(120, 120)
        system.step()
        wasp.watch.touch.swipe('down')
        system.step()

    assert(start_point == system.app.test)

def test_selftest_crash(system):
    system.switch(system.apps['Self Test'])
    system.step()

    def select(name):
        for i in range(len(system.app.tests)):
            if system.app.test == name:
                break
            wasp.watch.touch.swipe('down')
            system.step()
        assert system.app.test == name

    select('Crash')

    wasp.watch.button.value(0)
    with pytest.raises(Exception):
        system.step()

    # Get back to a safe state for the next test!
    try:
        wasp.watch.button.value(1)
        system.step()
    except:
        pass
    system.step()
