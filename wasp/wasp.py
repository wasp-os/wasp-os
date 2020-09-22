# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""Wasp-os system manager
~~~~~~~~~~~~~~~~~~~~~~~~~

.. data:: wasp.system

    wasp.system is the system-wide singleton instance of :py:class:`.Manager`.
    Application must use this instance to access the system services provided
    by the manager.

.. data:: wasp.watch

    wasp.watch is an import of :py:mod:`watch` and is simply provided as a
    shortcut (and to reduce memory by keeping it out of other namespaces).
"""

import gc
import machine
import micropython
import watch
import widgets

from apps.clock import ClockApp
from apps.flashlight import FlashlightApp
from apps.heart import HeartApp
from apps.launcher import LauncherApp
from apps.pager import PagerApp, CrashApp, NotificationApp
from apps.settings import SettingsApp
from apps.steps import StepCounterApp
from apps.stopwatch import StopwatchApp
from apps.testapp import TestApp

class EventType():
    """Enumerated interface actions.

    MicroPython does not implement the enum module so EventType
    is simply a regular object which acts as a namespace.
    """
    DOWN = 1
    UP = 2
    LEFT = 3
    RIGHT = 4
    TOUCH = 5

    HOME = 255
    BACK = 254
    NEXT = 253

class EventMask():
    """Enumerated event masks.
    """
    TOUCH = 0x0001
    SWIPE_LEFTRIGHT = 0x0002
    SWIPE_UPDOWN = 0x0004
    BUTTON = 0x0008
    NEXT = 0x0010

class PinHandler():
    """Pin (and Signal) event generator.

    TODO: Currently this driver doesn't actually implement any
    debounce but it will!
    """

    def __init__(self, pin):
        """
        :param Pin pin: The pin to generate events from
        """
        self._pin = pin
        self._value = pin.value()

    def get_event(self):
        """Receive a pin change event.

        Check for a pending pin change event and, if an event is pending,
        return it.

        :return: boolean of the pin state if an event is received, None
                 otherwise.
        """
        new_value = self._pin.value()
        if self._value == new_value:
            return None

        self._value = new_value
        return new_value

class Manager():
    """Wasp-os system manager

    The manager is responsible for handling top-level UI events and
    dispatching them to the foreground application. It also provides
    services to the application.

    The manager is expected to have a single system-wide instance
    which can be accessed via :py:data:`wasp.system` .
    """

    def __init__(self):
        self.app = None

        self.quick_ring = []
        self.launcher = LauncherApp()
        self.launcher_ring = []
        self.notifier = NotificationApp()
        self.notifications = {}

        self.blank_after = 15

        self._brightness = 2
        self._button = PinHandler(watch.button)
        self._charging = True
        self._scheduled = False
        self._scheduling = False

        # TODO: Eventually these should move to main.py
        for app, qr in ( (ClockApp, True),
                         (StepCounterApp, True),
                         (StopwatchApp, True),
                         (HeartApp, True),
                         (FlashlightApp, False),
                         (SettingsApp, False),
                         (TestApp, False) ):
            try:
                self.register(app(), qr)
            except:
                # Let's not bring the whole device down just because there's
                # an exception starting one of the apps...
                pass

    def register(self, app, quick_ring=False):
        """Register an application with the system.

        :param object app: The application to regsister
        """
        if quick_ring == True:
            self.quick_ring.append(app)
        else:
            self.launcher_ring.append(app)
            self.launcher_ring.sort(key = lambda x: x.NAME)

    @property
    def brightness(self):
        """Cached copy of the brightness current written to the hardware."""
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        self._brightness = value
        watch.backlight.set(self._brightness)

    def switch(self, app):
        """Switch to the requested application.
        """
        if self.app:
            if 'background' in dir(self.app):
                self.app.background()
        else:
            # System start up...
            watch.display.poweron()
            watch.display.mute(True)
            watch.backlight.set(self._brightness)
            self.sleep_at = watch.rtc.uptime + 90

        # Clear out any configuration from the old application
        self.event_mask = 0
        self.tick_period_ms = 0
        self.tick_expiry = None

        self.app = app
        watch.display.mute(True)
        watch.drawable.reset()
        app.foreground()
        watch.display.mute(False)

    def navigate(self, direction=None):
        """Navigate to a new application.

        Left/right navigation is used to switch between applications in the
        quick application ring. Applications on the ring are not permitted
        to subscribe to :py:data`EventMask.SWIPE_LEFTRIGHT` events.

        Swipe up is used to bring up the launcher. Clock applications are not
        permitted to subscribe to :py:data`EventMask.SWIPE_UPDOWN` events since
        they should expect to be the default application (and is important that
        we can trigger the launcher from the default application).

        :param int direction: The direction of the navigation
        """
        app_list = self.quick_ring

        if direction == EventType.LEFT:
            if self.app in app_list:
                i = app_list.index(self.app) + 1
                if i >= len(app_list):
                    i = 0
            else:
                i = 0
            self.switch(app_list[i])
        elif direction == EventType.RIGHT:
            if self.app in app_list:
                i = app_list.index(self.app) - 1
                if i < 0:
                    i = len(app_list)-1
            else:
                i = 0
            self.switch(app_list[i])
        elif direction == EventType.UP:
            self.switch(self.launcher)
        elif direction == EventType.DOWN:
            if self.app != app_list[0]:
                self.switch(app_list[0])
            else:
                if len(self.notifications):
                    self.switch(self.notifier)
                else:
                    # Nothing to notify... we must handle that here
                    # otherwise the display will flicker.
                    watch.vibrator.pulse()

        elif direction == EventType.HOME or direction == EventType.BACK:
            if self.app != app_list[0]:
                self.switch(app_list[0])
            else:
                self.sleep()

    def notify(self, id, msg):
        self.notifications[id] = msg

    def unnotify(self, id):
        if id in self.notifications:
            del self.notifications[id]

    def request_event(self, event_mask):
        """Subscribe to events.

        :param int event_mask: The set of events to subscribe to.
        """
        self.event_mask |= event_mask

    def request_tick(self, period_ms=None):
        """Request (and subscribe to) a periodic tick event.

        Note: With the current simplistic timer implementation sub-second
        tick intervals are not possible.
        """
        self.tick_period_ms = period_ms
        self.tick_expiry = watch.rtc.get_uptime_ms() + period_ms

    def keep_awake(self):
        """Reset the keep awake timer."""
        self.sleep_at = watch.rtc.uptime + self.blank_after

    def sleep(self):
        """Enter the deepest sleep state possible.
        """
        watch.backlight.set(0)
        if 'sleep' not in dir(self.app) or not self.app.sleep():
            self.switch(self.quick_ring[0])
            self.app.sleep()
        watch.display.poweroff()
        watch.touch.sleep()
        self._charging = watch.battery.charging()
        self.sleep_at = None

    def wake(self):
        """Return to a running state.
        """
        watch.display.poweron()
        if 'wake' in dir(self.app):
            self.app.wake()
        watch.backlight.set(self._brightness)
        watch.touch.wake()

        self.keep_awake()

    def _handle_button(self, state):
        """Process a button-press (or unpress) event.
        """
        self.keep_awake()

        if bool(self.event_mask & EventMask.BUTTON):
            # Currently we only support one button
            if not self.app.press(EventType.HOME, state):
                # If app reported None or False then we are done
                return

        if state:
            self.navigate(EventType.HOME)

    def _handle_touch(self, event):
        """Process a touch event.
        """
        self.keep_awake()
        event_mask = self.event_mask

        # Handle context sensitive events such as NEXT
        if event[0] == EventType.NEXT:
            if bool(event_mask & EventMask.NEXT) and not self.app.swipe(event):
                # The app has already handled this one (mark as no event)
                event[0] = 0
            elif self.app == self.quick_ring[0] and len(self.notifications):
                event[0] = EventType.DOWN
            elif self.app == self.notifier:
                event[0] = EventType.UP
            else:
                event[0] = EventType.RIGHT

        if event[0] < 5:
            updown = event[0] == 1 or event[0] == 2
            if (bool(event_mask & EventMask.SWIPE_UPDOWN) and updown) or \
               (bool(event_mask & EventMask.SWIPE_LEFTRIGHT) and not updown):
                if self.app.swipe(event):
                    self.navigate(event[0])
            else:
                self.navigate(event[0])
        elif event[0] == 5 and self.event_mask & EventMask.TOUCH:
            self.app.touch(event)

        watch.touch.reset_touch_data()

    def _tick(self):
        """Handle the system tick.

        This function may be called frequently and includes short
        circuit logic to quickly exit if we haven't reached a tick
        expiry point.
        """
        rtc = watch.rtc

        if self.sleep_at:
            if rtc.update() and self.tick_expiry:
                now = rtc.get_uptime_ms()

                if self.tick_expiry <= now:
                    ticks = 0
                    while self.tick_expiry <= now:
                        self.tick_expiry += self.tick_period_ms
                        ticks += 1
                    self.app.tick(ticks)

            state = self._button.get_event()
            if None != state:
                self._handle_button(state)

            event = watch.touch.get_event()
            if event:
                self._handle_touch(event)

            if self.sleep_at and watch.rtc.uptime > self.sleep_at:
                self.sleep()

            gc.collect()
        else:
            watch.rtc.update()

            if 1 == self._button.get_event() or \
                    self._charging != watch.battery.charging():
                self.wake()

    def run(self, no_except=True):
        """Run the system manager synchronously.

        This allows all watch management activities to handle in the
        normal execution context meaning any exceptions and other problems
        can be observed interactively via the console.
        """
        if self._scheduling:
            print('Watch already running in the background')
            return

        if not self.app:
            self.switch(self.quick_ring[0])

        # Reminder: wasptool uses this string to confirm the device has
        # been set running again.
        print('Watch is running, use Ctrl-C to stop')

        if not no_except:
            # This is a simplified (uncommented) version of the loop
            # below
            while True:
                self._tick()
                machine.deepsleep()

        while True:
            try:
                self._tick()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                # Only print the exception if the watch provides a way to do so!
                if 'print_exception' in dir(watch):
                    watch.print_exception(e)
                self.switch(CrashApp(e))

            # Currently there is no code to control how fast the system
            # ticks. In other words this code will break if we improve the
            # power management... we are currently relying on not being able
            # to stay in the low-power state for very long.
            machine.deepsleep()

    def _work(self):
        self._scheduled = False
        try:
            self._tick()
        except Exception as e:
            # Only print the exception if the watch provides a way to do so!
            if 'print_exception' in dir(watch):
                watch.print_exception(e)
            self.switch(CrashApp(e))

    def _schedule(self):
        """Asynchronously schedule a system management cycle."""
        if not self._scheduled:
            self._scheduled = True
            micropython.schedule(Manager._work, self)

    def schedule(self, enable=True):
        """Run the system manager synchronously."""
        if not self.app:
            self.switch(self.quick_ring[0])

        if enable:
            watch.schedule = self._schedule
        else:
            watch.schedule = watch.nop

        self._scheduling = enable

system = Manager()
