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
import steplogger
import sys
import watch
import widgets
import appregistry

from apps.system.launcher import LauncherApp
from apps.system.pager import PagerApp, CrashApp, NotificationApp
from apps.system.step_counter import StepCounterApp

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

def _key_app(d):
    """Get a sort key for apps."""
    return d.NAME

def _key_alarm(d):
    """Get a sort key for alarms."""
    return d[0]

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

        self.bar = widgets.StatusBar()

        self.quick_ring = []
        self.launcher = LauncherApp()
        self.launcher_ring = []
        self.notifier = NotificationApp()
        self.notifications = {}
        self.musicstate = {}
        self.musicinfo = {}
        self.weatherinfo = {}
        self.units = "Metric"

        self._theme = (
                b'\x7b\xef'     # ble
                b'\x7b\xef'     # scroll-indicator
                b'\x7b\xef'     # battery
                b'\xe7\x3c'     # status-clock
                b'\x7b\xef'     # notify-icon
                b'\xff\xff'     # bright
                b'\xbd\xb6'     # mid
                b'\x39\xff'     # ui
                b'\xff\x00'     # spot1
                b'\xdd\xd0'     # spot2
                b'\x00\x0f'     # contrast
        )

        self.blank_after = 15

        self._alarms = []
        self._brightness = 2
        self._notifylevel = 2
        if 'P8' in watch.os.uname().machine:
            self._nfylevels = [0, 225, 450]
        else:
            self._nfylevels = [0, 40, 80]
        self._nfylev_ms = self._nfylevels[self._notifylevel - 1]
        self._button = PinHandler(watch.button)
        self._charging = True
        self._scheduled = False
        self._scheduling = False

    def secondary_init(self):
        global free

        if not self.app:
            # Register default apps if main hasn't put anything on the quick ring
            if not self.quick_ring:
                self.register_defaults()

            # System start up...
            watch.display.poweron()
            watch.display.mute(True)
            watch.backlight.set(self._brightness)
            self.sleep_at = watch.rtc.uptime + 90
            if watch.free:
                gc.collect()
                free = gc.mem_free()

            self.switch(self.quick_ring[0])

    def register_defaults(self):
        """Register the default applications."""

        for app in appregistry.autoload_list:
            self.register(app[0], app[1], app[2], app[3])

        self.register('apps.system.step_counter.StepCounterApp', True, no_except=True)
        self.register('apps.system.settings.SettingsApp', no_except=True)
        self.register('apps.system.software.SoftwareApp', no_except=True)

    def register(self, app, quick_ring=False, watch_face=False, no_except=False):
        """Register an application with the system.

        :param object app: The application to register
        :param object quick_ring: Place the application on the quick ring
        :param object watch_face: Make the new application the default watch face
        :param object no_except: Ignore exceptions when instantiating applications
        """
        if isinstance(app, str):
            modname = app[:app.rindex('.')]
            exec('import ' + modname)
            if no_except:
                try:
                    app = eval(app + '()')
                except:
                    app = None
            else:
                    app = eval(app + '()')
            exec('del ' + modname)
            exec('del sys.modules["' + modname + '"]')
            if not app:
                return

        # "Special case" for watches that have working step counters!
        # More usefully it allows other apps to detect the presence/absence
        # of a working step counter by looking at wasp.system.steps .
        if isinstance(app, StepCounterApp):
            self.steps = steplogger.StepLogger(self)

        if watch_face:
            self.quick_ring[0] = app
        elif quick_ring:
            self.quick_ring.append(app)
        else:
            self.launcher_ring.append(app)
            self.launcher_ring.sort(key = _key_app)

    def unregister(self, cls):
        for app in self.launcher_ring:
            if isinstance(app, cls):
                self.launcher_ring.remove(app)
                break

    @property
    def brightness(self):
        """Cached copy of the brightness current written to the hardware."""
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        self._brightness = value
        watch.backlight.set(self._brightness)

    @property
    def notify_level(self):
        """Cached copy of the current notify level"""
        return self._notifylevel

    @notify_level.setter
    def notify_level(self, value):
        self._notifylevel = value
        self._nfylev_ms = self._nfylevels[self._notifylevel - 1]

    @property
    def notify_duration(self):
        """Cached copy of the current vibrator pulse duration in milliseconds"""
        return self._nfylev_ms

    def switch(self, app):
        """Switch to the requested application.
        """
        if self.app is app:
            return

        if self.app:
            if 'background' in dir(self.app):
                try:
                    self.app.background()
                except:
                    # Clear out the old app to ensure we don't recurse when
                    # we switch to to the CrashApp. It's a bit freaky but
                    # True has an empty directory and is is better than
                    # None because it won't re-run the system start up
                    # code (else clause).
                    self.app = True
                    raise

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

    def toggle_music(self, state):
        self.musicstate = state

    def set_music_info(self, info):
        self.musicinfo = info

    def set_weather_info(self, info):
        self.weatherinfo = info

    def set_alarm(self, time, action):
        """Queue an alarm.

        :param int time: Time to trigger the alarm (use time.mktime)
        :param function action: Action to perform when the alarm expires.
        """
        self._alarms.append((time, action))
        self._alarms.sort(key=_key_alarm)

    def cancel_alarm(self, time, action):
        """Unqueue an alarm."""
        alarms = self._alarms
        try:
            if not time:
                time_to_remove = [al[0] for al in alarms if al[1] == action]
                [alarms.remove((t, action)) for t in time_to_remove]
            else:
                alarms.remove((time, action))
        except:
            return False
        return True

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
        if period_ms:
            self.tick_period_ms = period_ms
            self.tick_expiry = watch.rtc.get_uptime_ms() + period_ms
        else:
            self.tick_period_ms = 0
            self.tick_expiry = None

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
        if not self.sleep_at:
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

    @micropython.native
    def _tick(self):
        """Handle the system tick.

        This function may be called frequently and includes short
        circuit logic to quickly exit if we haven't reached a tick
        expiry point.
        """
        rtc = watch.rtc
        update = rtc.update()

        alarms = self._alarms
        if update and alarms:
            now = rtc.time()
            head = alarms[0]

            if head[0] <= now:
                alarms.remove(head)
                head[1]()

        if self.sleep_at:
            if update and self.tick_expiry:
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
            if 1 == self._button.get_event() or \
                    self._charging != watch.battery.charging():
                self.wake()

    def run(self, no_except=True):
        """Run the system manager synchronously.

        This allows all watch management activities to handle in the
        normal execution context meaning any exceptions and other problems
        can be observed interactively via the console. This is used by the
        simulator or for debugging is not normally called. The watch instead
        calls self.schedule() directly at startup from main.py.
        """
        if self._scheduling:
            print('Watch already running in the background')
            return

        self.secondary_init()

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
            except MemoryError:
                self.switch(PagerApp("Your watch is low on memory.\n\nYou may want to reboot."))
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
        except MemoryError:
            self.switch(PagerApp("Your watch is low on memory.\n\nYou may want to reboot."))
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
        self.secondary_init()

        if enable:
            watch.schedule = self._schedule
        else:
            watch.schedule = watch.nop

        self._scheduling = enable

    def set_theme(self, new_theme) -> bool:
        """Sets the system theme.

        Accepts anything that supports indexing,
        and has a len() equivalent to the default theme."""
        if len(self._theme) != len(new_theme):
            return False
        self._theme = new_theme
        return True

    def theme(self, theme_part: str) -> int:
        """Returns the relevant part of theme. For more see ../tools/themer.py"""
        theme_parts = ("ble",
                       "scroll-indicator",
                       "battery",
                       "status-clock",
                       "notify-icon",
                       "bright",
                       "mid",
                       "ui",
                       "spot1",
                       "spot2",
                       "contrast")
        if theme_part not in theme_parts:
            raise IndexError('Theme part {} does not exist'.format(theme_part))
        idx = theme_parts.index(theme_part) * 2
        return (self._theme[idx] << 8) | self._theme[idx+1]

system = Manager()
