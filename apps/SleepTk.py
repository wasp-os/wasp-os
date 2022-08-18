# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2021 github.com/thiswillbeyourgithub/

"""Sleep tracker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SleepTk is an alarm clock app with several dinstinctive features:
* sleep cycle suggestion (also useful to troubleshoot insomnia)
* gradual wake up via vibration
* easy to snooze, hard to stop
* body movement tracking
* heart rate tracking

Still somewhat under developpement, more information at
[the github](https://github.com/thiswillbeyourgithub/sleep_tracker_pinetime_wasp-os)

Icon kindly designed by [Emanuel Löffler](https://github.com/plan5)

.. figure:: res/SleepTkApp.png
    :width: 179

Note: the time might be inaccurate in the simulator (offset by 1 hour passed
midnight or something) but is fine on the watch.

"""

import wasp
import widgets
import shell
import fonts
import math
import ppg
from array import array
from micropython import const

# HARDCODED VARIABLES:
_ON = const(1)
_OFF = const(0)
_TRACKING = const(0)
_RINGING = const(1)
_SETTINGS1 = const(2)
_SETTINGS2 = const(3)
_FONT = fonts.sans18
_FONT_COLOR = const(0xf800)  # red font to reduce eye strain at night
_TIMESTAMP = const(946684800)  # unix time and time used by wasp os don't have the same reference date

## USER SETTINGS #################################
_KILL_BT = const(1)
# set to 0 to disable turning off bluetooth while tracking to save battery
# (you have to reboot the watch to reactivate BT, default: 1)
_STOP_LIMIT = const(10)
# number of times to swipe or press the button to turn off ringing (default: 10)
_SNOOZE_TIME = const(300)
# number of seconds to snooze for (default: 5 minutes)
_FREQ = const(5)
# get accelerometer data every X seconds, but process and store them only
# every _STORE_FREQ seconds (default: 5)
_HR_FREQ = const(300)
# how many seconds between heart rate data (default: 300, minimum 120)
_STORE_FREQ = const(300)
# process data and store to file every X seconds (default: 300)
_BATTERY_THRESHOLD = const(15)
# under X% of battery, stop tracking and only keep the alarm, set at -200
# or lower to disable (default: 15)
_GRADUAL_WAKE = array("H", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
# nb of minutes before alarm to send a tiny vibration, designed to wake
# you more gently. (default: array("H", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) )
_CYCLE_LENGTH = const(90)
# sleep cycle length in minutes. Currently used only to display best wake up
# time! (default should be: 90 or 100, according to https://sleepyti.me/)
_SLEEP_GOAL_CYCLE = const(5)
# number of sleep cycle you wish to sleep. With _CYCLE_LENGTH this is used
# to suggest best wake up time to user when setting the alarm. (default: 5)
##################################################


class SleepTkApp():
    NAME = 'SleepTk'
    # 2-bit RLE, 60x60, 225 bytes, kindly designed by [Emanuel Löffler](https://github.com/plan5)
    ICON = (
        b'\x02'
        b'<<'
        b'?\x11\xd2*\xd2*\xd2*\xd8$\xd82\xca2\xca6'
        b'\xc4\x02\xc24\xc4\x02\xc24\xc4\x04\xc40\xc4\x04\xc40'
        b'\xc4\x04\xc40\xc4\x04\xc42\xc2\x04\xc8.\xc2\x04\xc8.'
        b'\xc2\x04\xc8.\xc2\x04\xc8 \xc4\n\xc2\x06\xc6 \xc4\n'
        b'\xc2\x06\xc6 \xc4\x08\xc6\x04\xc6 \xc4\x08\xc6\x04\xc6\x1e'
        b'\xc8\x06\xc6\x04\xc6\x1e\xc8\x06\xc6\x04\xc6\x1e\xc8\x06\xc6\x04'
        b'\xc6\x1e\xc8\x06\xc6\x04\xc6\x1c\xca\x06\xc6\x04\xc6\x1c\xd6\x04'
        b'\xc6\x1c\xd6\x04\xc6\x1c\xd6\x04\xc6\x07\xed\x08\xc4\x03\xed\x08'
        b'\xc4\x03\xed\x08\xc4\x03\xed\x08\xc4"\xc6\x04\xc4\x06\xc2&'
        b'\xc6\x04\xc4\x06\xc2&\xc6\x04\xc4\x06\xc2&\xc6\x04\xc4\x06'
        b'\xc2&\xc6\x04\xc6\x04\xc2&\xc6\x04\xc6\x04\xc2(\xc2\x04'
        b'\xc8\x02\xc2*\xc2\x04\xc8\x02\xc2.\xce.\xce.\xce.'
        b'\xce*\xd1+\xd1+\xd1+\xd1%\xd7%\xd4\x16\xe6\x16'
        b'\xe6\x16\xe0\x1c\xe0\x1c\xde\x1e\xde"\xd4(\xd4\x1a'
    )

    def __init__(self):
        wasp.gc.collect()

        # default button state
        self._state_alarm = _ON
        self._state_body_tracking = _OFF
        self._state_HR_tracking = _OFF
        self._state_gradual_wake = _ON
        self._state_spinval_H = _OFF
        self._state_spinval_M = _OFF

        self._hrdata = None
        self._last_HR = _OFF  # if _OFF, no HR to write, if "?": error during last HR, else: heart rate
        self._last_HR_printed = "?"
        self._last_HR_date = _OFF
        self._track_HR_once = _OFF

        self._page = _SETTINGS1
        self._currently_tracking = _OFF
        self._conf_view = _OFF  # confirmation view
        self._buff = array("f", [_OFF, _OFF, _OFF])  # contains accelerometer values
        self._last_touch = int(wasp.watch.rtc.time())

        try:
            shell.mkdir("logs")
        except:  # folder already exists
            pass
        try:
            shell.mkdir("logs/sleep")
        except:  # folder already exists
            pass

    def foreground(self):
        self.stat_bar = widgets.StatusBar()
        self.stat_bar.clock = True
        self._conf_view = _OFF
        wasp.gc.collect()
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_LEFTRIGHT |
                                  wasp.EventMask.SWIPE_UPDOWN |
                                  wasp.EventMask.BUTTON)
        if self._page == _TRACKING and self._track_HR_once:
            wasp.system.request_tick(1000 // 8)

    def sleep(self):
        self._stop_trial = 0
        wasp.gc.collect()
        return True

    def background(self):
        wasp.watch.hrs.disable()
        self._hrdata = None
        wasp.gc.collect()

    def _try_stop_alarm(self):
        """If button or swipe more than _STOP_LIMIT, then stop ringing"""
        if self._stop_trial + 1 >= _STOP_LIMIT:
            self._n_vibration = 0
            del self._n_vibration
            wasp.system.cancel_alarm(self._WU_t, self._activate_ticks_to_ring)
            self._disable_tracking()
            self.__init__()
            self.foreground()
        else:
            self._stop_trial += 1
            draw = wasp.watch.drawable
            draw.set_font(_FONT)
            draw.set_color(_FONT_COLOR)
            draw.string("{} to stop".format(_STOP_LIMIT - self._stop_trial), 0, 70)

    def press(self, button, state):
        "stop ringing alarm if pressed physical button"
        if not state:
            return
        self._last_touch = int(wasp.watch.rtc.time())
        mute = wasp.watch.display.mute
        mute(False)
        if self._page == _RINGING:
            self._try_stop_alarm()
        elif self._page == _TRACKING:
            self._was_touched = 1
            # disable pressing to exit, use swipe up instead
            self._draw()
        else:
            wasp.system.navigate(wasp.EventType.HOME)

    def swipe(self, event):
        "navigate between settings page"
        mute = wasp.watch.display.mute
        mute(False)
        self._last_touch = int(wasp.watch.rtc.time())
        if self._page == _SETTINGS1:
            if event[0] == wasp.EventType.LEFT:
                self._page = _SETTINGS2
                self._draw()
            else:
                return True
        elif self._page == _SETTINGS2:
            if event[0] == wasp.EventType.RIGHT:
                self._page = _SETTINGS1
                self._draw()
            else:
                return True
        elif self._page == _RINGING:
            self._try_stop_alarm()
        else:
            return True

    def touch(self, event):
        """either start trackign or disable it, draw the screen in all cases"""
        wasp.gc.collect()
        self.stat_bar.draw()
        draw = wasp.watch.drawable
        draw.set_font(_FONT)
        mute = wasp.watch.display.mute
        mute(False)
        self._last_touch = int(wasp.watch.rtc.time())
        if self._page == _TRACKING:
            self._was_touched = 1
            if self._conf_view is _OFF:
                if self.btn_off.touch(event):
                    self._conf_view = widgets.ConfirmationView()
                    self._conf_view.draw("Stop tracking?")
                    draw.reset()
                    return
            else:
                if self._conf_view.touch(event):
                    if self._conf_view.value:
                        self._disable_tracking()
                        self._page = _SETTINGS1
                    self._conf_view = _OFF
                draw.reset()
        elif self._page == _RINGING:
            if self.btn_snooz.touch(event):
                if self._track_HR_once:  # if currently tracking HR, stop
                    self._track_HR_once = _OFF
                    self._hrdata = None
                    wasp.watch.hrs.disable()
                self._page = _TRACKING
                self._WU_t = int(wasp.watch.rtc.time()) + _SNOOZE_TIME
                wasp.system.set_alarm(self._WU_t, self._activate_ticks_to_ring)
                wasp.system.sleep()
        elif self._page == _SETTINGS1:
            if self._state_alarm and (self._spin_H.touch(event) or self._spin_M.touch(event)):
                if self._state_spinval_M == 0 and self._spin_M.value == 55:
                    self._spin_H.value -= 1
                elif self._state_spinval_M == 55 and self._spin_M.value == 0:
                    self._spin_H.value += 1
                if self._spin_H.value >= 24:
                    self._spin_H.value = 0
                elif self._spin_H.value <= -1:
                    self._spin_H.value = 23
                self._state_spinval_M = self._spin_M.value
                self._spin_M.update()
                self._state_spinval_H = self._spin_H.value
                self._spin_H.update()
                if self._state_alarm:
                    self._draw_duration(draw)
                return
            elif self.check_al.touch(event):
                self._state_alarm = self.check_al.state
                self.check_al.update()
            return
        elif self._page == _SETTINGS2:
            if self._state_body_tracking:
                if self.btn_HR.touch(event):
                    self.btn_HR.draw()
                    self._state_HR_tracking = self.btn_HR.state
                    return
            if self._state_alarm:
                if self.check_grad.touch(event):
                    self._state_gradual_wake = self.check_grad.state
                    self.check_grad.draw()
                    return
            if self.btn_sta.touch(event):
                draw.fill()
                draw.string("Loading", 0, 100)
                self._start_tracking()
            elif self.check_body_tracking.touch(event):
                self._state_body_tracking = self.check_body_tracking.state
                self.check_body_tracking.draw()
                if not self._state_body_tracking:
                    self._state_HR_tracking = _OFF
        self._draw()

    def _draw_duration(self, draw):
        draw.set_font(_FONT)
        if self._page == _SETTINGS1:
            duration = (self._read_time(self._state_spinval_H, self._state_spinval_M) - wasp.watch.rtc.time()) / 60
            y = 180
        elif self._page == _TRACKING:
            draw.set_color(_FONT_COLOR)
            duration = (wasp.watch.rtc.time() - self._track_start_time) / 60
            if duration <= 0:  # don't print when not yet asleep
                return
            y = 130

        draw.string("Total sleep {:02d}h{:02d}m".format(
            int(duration // 60),
            int(duration % 60)), 0, y + 20)
        cycl = duration / _CYCLE_LENGTH
        cycl_modulo = cycl % 1
        draw.string("{} cycles   ".format(str(cycl)[0:4]), 0, y)
        if duration > 30 and not self._track_HR_once:
            if cycl_modulo > 0.10 and cycl_modulo < 0.90:
                draw.string("Not rested!", 0, y + 40)
            else:
                draw.string("Well rested", 0, y + 40)

    def _draw(self):
        """GUI"""
        mute = wasp.watch.display.mute
        mute(False)
        draw = wasp.watch.drawable
        draw.fill(0)
        self.stat_bar.draw()
        draw.set_font(_FONT)
        draw.set_color(_FONT_COLOR)
        if self._page == _RINGING:
            draw.string("WAKE UP", 0, 50)
            self.btn_snooz = widgets.Button(x=0, y=90, w=240, h=120, label="SNOOZE")
            self.btn_snooz.draw()
            draw.reset()
        elif self._page == _TRACKING:
            ti = wasp.watch.time.localtime(self._track_start_time)
            draw.string('Began at {:02d}:{:02d}'.format(ti[3], ti[4]), 0, 50)
            if self._state_alarm:
                word = "Alarm at "
                ti = wasp.watch.time.localtime(self._WU_t)
                draw.string("{}{:02d}:{:02d}".format(word, ti[3], ti[4]), 0, 70)
                draw.string("Gradual wake: {}".format(True if self._state_gradual_wake else False), 0, 90)
            else:
                draw.string("No alarm set", 0, 70)
            draw.string("data points: {} / {}".format(str(self._data_point_nb), str(self._data_point_nb * _FREQ // _STORE_FREQ)), 0, 110)
            if self._track_HR_once:
                draw.string("(ongoing)", 0, 170)
            if self._state_HR_tracking:
                draw.string("HR:{}".format(self._last_HR_printed), 160, 170)
            self.btn_off = widgets.Button(x=0, y=200, w=240, h=40, label="Stop")
            self.btn_off.update(txt=_FONT_COLOR, frame=0, bg=0)
            self._draw_duration(draw)
        elif self._page == _SETTINGS1:
            # reset spinval values between runs
            self._state_spinval_H = _OFF
            self._state_spinval_M = _OFF
            self.check_al = widgets.Checkbox(x=0, y=40, label="Wake me up")
            self.check_al.state = self._state_alarm
            self.check_al.draw()
            if self._state_alarm:
                if (self._state_spinval_H, self._state_spinval_M) == (_OFF, _OFF):
                    # suggest wake up time, on the basis of desired sleep goal + time to fall asleep
                    (H, M) = wasp.watch.rtc.get_localtime()[3:5]
                    goal_h = _SLEEP_GOAL_CYCLE * _CYCLE_LENGTH // 60
                    goal_m = _SLEEP_GOAL_CYCLE * _CYCLE_LENGTH % 60
                    M += goal_m
                    while M % 5 != 0:
                        M += 1
                    self._state_spinval_H = ((H + goal_h) % 24 + (M // 60)) % 24
                    self._state_spinval_M = M % 60
                self._spin_H = widgets.Spinner(30, 70, 0, 23, 2)
                self._spin_H.value = self._state_spinval_H
                self._spin_H.draw()
                self._spin_M = widgets.Spinner(150, 70, 0, 59, 2, 5)
                self._spin_M.value = self._state_spinval_M
                self._spin_M.draw()
                if self._state_alarm:
                    self._draw_duration(draw)
        elif self._page == _SETTINGS2:
            self.check_body_tracking = widgets.Checkbox(x=0, y=40, label="Movement tracking")
            self.check_body_tracking.state = self._state_body_tracking
            self.check_body_tracking.draw()
            if self._state_body_tracking:
                self.btn_HR = widgets.Checkbox(x=0, y=80, label="Heart rate tracking")
                self.btn_HR.state = self._state_HR_tracking
                self.btn_HR.draw()
            if self._state_alarm:
                self.check_grad = widgets.Checkbox(0, 120, "Gradual wake")
                self.check_grad.state = self._state_gradual_wake
                self.check_grad.draw()
            self.btn_sta = widgets.Button(x=0, y=200, w=240, h=40, label="Start")
            self.btn_sta.draw()
        draw.reset()

    def _start_tracking(self):
        # save some memory
        self.check_al = None
        self.check_body_tracking = None
        self.check_grad = None
        self.btn_sta = None
        self.btn_snooz = None
        self.btn_off = None
        self.btn_HR = None
        self._spin_H = None
        self._spin_M = None
        del self.check_al, self.check_body_tracking, self.check_grad, self.btn_sta, self.btn_snooz, self.btn_off, self.btn_HR, self._spin_H, self._spin_M

        self._currently_tracking = True

        # accel data not yet written to disk:
        self._data_point_nb = 0  # total number of data points so far
        self._last_checkpoint = 0  # to know when to save to file
        self._track_start_time = int(wasp.watch.rtc.time())  # makes output more compact
        self._last_HR_printed = "?"
        self._was_touched = 0
        wasp.watch.accel.reset()

        # create one file per recording session:
        self.filep = "logs/sleep/{}.csv".format(str(self._track_start_time + _TIMESTAMP))
        f = open(self.filep, "wb")
        f.write(b"")
        f.close()

        # if enabled, add alarm to log accel data in _FREQ seconds
        if self._state_body_tracking:
            self.next_al = wasp.watch.rtc.time() + _FREQ
            wasp.system.set_alarm(self.next_al, self._trackOnce)
        else:
            self.next_al = None

        if self._state_gradual_wake and not self._state_alarm:
            # fix incompatible settings
            self._state_gradual_wake = _OFF

        # setting up alarm
        if self._state_alarm:
            self._old_notification_level = wasp.system.notify_level
            self._WU_t = self._read_time(self._state_spinval_H, self._state_spinval_M)
            wasp.system.set_alarm(self._WU_t, self._activate_ticks_to_ring)

            # also set alarm to vibrate a tiny bit before wake up time
            # to wake up gradually
            if self._state_gradual_wake:
                for t in _GRADUAL_WAKE:
                    wasp.system.set_alarm(self._WU_t - int(t*60), self._tiny_vibration)

        # don't track heart rate right away, wait a few seconds
        if self._state_HR_tracking:
            self._last_HR_date = int(wasp.watch.rtc.time()) + 10
        wasp.system.notify_level = 1  # silent notifications

        # kill bluetooth
        if _KILL_BT:
            import ble
            if ble.enabled():
                ble.disable()

        self._page = _TRACKING
        self._stop_trial = 0

    def _read_time(self, HH, MM):
        "convert time from spinners to seconds"
        (Y, Mo, d, h, m) = wasp.watch.rtc.get_localtime()[0:5]
        HH = self._state_spinval_H
        MM = self._state_spinval_M
        if HH < h or (HH == h and MM <= m):
            d += 1
        return wasp.watch.time.mktime((Y, Mo, d, HH, MM, 0, 0, 0, 0))

    def _disable_tracking(self, keep_main_alarm=False):
        """called by touching "STOP TRACKING" or when computing best alarm time
        to wake up you disables tracking features and alarms"""
        self._currently_tracking = False
        if self.next_al:
            wasp.system.cancel_alarm(self.next_al, self._trackOnce)
        if self._state_alarm:
            if keep_main_alarm is False:  # to keep the alarm when stopping because of low battery
                wasp.system.cancel_alarm(self._WU_t, self._activate_ticks_to_ring)
                for t in _GRADUAL_WAKE:
                    wasp.system.cancel_alarm(self._WU_t - int(t*60), self._tiny_vibration)
        wasp.watch.hrs.disable()
        self._periodicSave()
        self._state_HR_tracking = _OFF
        wasp.gc.collect()

    def _trackOnce(self):
        """get one data point of accelerometer every _FREQ seconds, keep
        the average of each axis then store in a file every
        _STORE_FREQ seconds"""
        if self._currently_tracking:
            buff = self._buff
            xyz = wasp.watch.accel.accel_xyz()
            if xyz == (0, 0, 0):
                wasp.watch.accel.reset()
                xyz = wasp.watch.accel.accel_xyz()
            buff[0] += xyz[0]
            buff[1] += xyz[1]
            buff[2] += xyz[2]
            self._data_point_nb += 1

            # add alarm to log accel data in _FREQ seconds
            self.next_al = wasp.watch.rtc.time() + _FREQ
            wasp.system.set_alarm(self.next_al, self._trackOnce)

            self._periodicSave()
            if wasp.watch.battery.level() <= _BATTERY_THRESHOLD:
                # strop tracking if battery low
                self._disable_tracking(keep_main_alarm=True)
                h, m = wasp.watch.time.localtime(wasp.watch.rtc.time())[3:5]
                wasp.system.notify(wasp.watch.rtc.get_uptime_ms(), {"src": "SleepTk",
                                                          "title": "Bat low",
                                                          "body": "Stopped \
tracking sleep at {}h{}m because your battery went below {}%. Alarm kept \
on.".format(h, m, _BATTERY_THRESHOLD)})
            elif self._state_HR_tracking and \
                    wasp.watch.rtc.time() - self._last_HR_date > _HR_FREQ and \
                    not self._track_HR_once:
                self._track_HR_once = _ON
                wasp.system.wake()
                if int(wasp.watch.rtc.time()) - self._last_touch > 5:
                    mute = wasp.watch.display.mute
                    mute(True)
                wasp.system.switch(self)
                wasp.system.request_tick(1000 // 8)

        wasp.gc.collect()

    def _periodicSave(self):
        """save data to csv with row order:
            1. average arm angle
            2. elapsed times
            3/4. heart rate if present, and/or -1 if screen was woken up
                by user during that time
         arm angle formula from https://www.nature.com/articles/s41598-018-31266-z
         note: math.atan() is faster than using a taylor serie
        """
        buff = self._buff
        n = self._data_point_nb - self._last_checkpoint
        if n >= _STORE_FREQ // _FREQ and not self._track_HR_once:
            buff[0] /= n
            buff[1] /= n
            buff[2] /= n
            if self._last_HR != _OFF:
                bpm = ",{}".format(str(self._last_HR))
                self._last_HR = _OFF
            else:
                bpm = ""
            f = open(self.filep, "ab")
            f.write("{:7f},{}{}\n".format(
                math.atan(buff[2] / (buff[0]**2 + buff[1]**2))*180/3.1415926535,  # estimated arm angle
                int(wasp.watch.rtc.time() - self._track_start_time),
                bpm,
                ",-1" if self._was_touched else ""
                ).encode())
            f.close()
            del f
            buff[0] = 0  # resets x/y/z to 0
            buff[1] = 0
            buff[2] = 0
            self._last_checkpoint = self._data_point_nb
            self._was_touched = 0
            wasp.gc.collect()

    def _activate_ticks_to_ring(self):
        """listen to ticks every second, telling the watch to vibrate and
        completely wake the user up"""
        wasp.gc.collect()
        wasp.system.notify_level = self._old_notification_level  # restore notification level
        self._page = _RINGING
        self._n_vibration = 0
        if int(wasp.watch.rtc.time()) - self._last_touch > 5:
            mute = wasp.watch.display.mute
            mute(True)
        wasp.system.wake()
        wasp.system.switch(self)
        self._draw()
        wasp.system.request_tick(period_ms=1000)

    def tick(self, ticks):
        """vibrate to wake you up OR track heart rate using code from heart.py"""
        wasp.gc.collect()
        wasp.system.switch(self)
        if self._page == _RINGING:
            wasp.system.keep_awake()
            # in 60 vibrations, ramp up from subtle to strong:
            wasp.watch.vibrator.pulse(duty=max(80 - 1 * self._n_vibration, 20),
                                      ms=min(100 + 6 * self._n_vibration, 500))
            self._n_vibration += 1
        elif self._track_HR_once:
            wasp.watch.hrs.enable()
            if self._hrdata is None:
                self._hrdata = ppg.PPG(wasp.watch.hrs.read_hrs())
            t = wasp.machine.Timer(id=1, period=8000000)
            t.start()
            wasp.system.keep_awake()
            if int(wasp.watch.rtc.time()) - self._last_touch > 5:
                mute = wasp.watch.display.mute
                mute(True)
            self._subtick(1)
            while t.time() < 41666:
                pass
            wasp.system.keep_awake()
            self._subtick(1)
            while t.time() < 83332:
                pass
            wasp.system.keep_awake()
            self._subtick(1)
            t.stop()
            del t

            wasp.system.keep_awake()
            if len(self._hrdata.data) >= 240:  # 10 seconds passed
                bpm = self._hrdata.get_heart_rate()
                bpm = int(bpm) if bpm is not None else None
                if bpm is None:
                    # in case of invalid data, write it in the file but
                    # keep trying to read HR
                    self._last_HR = "?"
                    self._hrdata = None
                    self._last_HR_printed = self._last_HR
                elif bpm < 100 and bpm > 40:
                    # if HR was already computed since last periodicSave,
                    # then average the two values
                    if self._last_HR != _OFF and self._last_HR != "?" and isinstance(int, self._last_HR):
                        self._last_HR = (self._last_HR + bpm) // 2
                    else:
                        self._last_HR = bpm
                    self._last_HR_printed = self._last_HR
                    self._last_HR_date = int(wasp.watch.rtc.time())
                    self._track_HR_once = _OFF
                    self._hrdata = None
                    wasp.watch.hrs.disable()
                    if int(wasp.watch.rtc.time()) - self._last_touch > 5:
                        wasp.system.sleep()

    def _subtick(self, ticks):
        """track heart rate at 24Hz"""
        self._hrdata.preprocess(wasp.watch.hrs.read_hrs())

    def _tiny_vibration(self):
        """vibrate just a tiny bit before waking up, to gradually return
        to consciousness"""
        wasp.gc.collect()
        if int(wasp.watch.rtc.time()) - self._last_touch > 5:
            mute = wasp.watch.display.mute
            mute(True)
        wasp.system.wake()
        wasp.system.switch(self)
        wasp.watch.vibrator.pulse(duty=3, ms=50)
        # time.sleep(0.1)
        # wasp.watch.vibrator.pulse(duty=3, ms=50)
        if not self._track_HR_once:
            wasp.system.sleep()

