# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
# Copyright (C) 2020 Joris Warmbier
# Copyright (C) 2021 Adam Blair
"""Alarm Application
~~~~~~~~~~~~~~~~~~~~

An application to set a vibration alarm. All settings can be accessed from the Watch UI.
Press the button to turn off ringing alarms.

    .. figure:: res/screenshots/AlarmApp.png
        :width: 179

        Screenshot of the Alarm Application

"""
import wasp
import fonts
import time
import widgets
import array
from micropython import const

# 2-bit RLE, generated from res/alarm_icon.png, 390 bytes
icon = (
    b'\x02'
    b'`@'
    b'\x17@\xd2G#G-K\x1fK)O\x1bO&O'
    b'\n\x80\xb4\x89\x0bN$N\x08\x91\tM"M\x07\x97'
    b'\x07M!L\x06\x9b\x07K K\x06\x9f\x06K\x1fJ'
    b'\x05\xa3\x05J\x1eJ\x05\x91\xc0\xd0\xc3\x91\x05J\x1dI'
    b'\x05\x8c\xcf\x8c\x05I\x1dH\x05\x8b\xd3\x8b\x05H\x1dG'
    b'\x05\x8a\xd7\x8a\x05G\x1dG\x04\x89\xdb\x89\x05F\x1dF'
    b'\x04\x89\xcc\x05\xcc\x89\x04F\x1dE\x04\x89\xcd\x05\xcd\x89'
    b'\x04E\x1eD\x03\x88\xce\x07\xce\x88\x04C\x1fC\x04\x88'
    b'\xce\x07\xce\x88\x04C\x1fC\x03\x88\xcf\x07\xcf\x88\x04A'
    b'!A\x04\x87\xd0\x07\xd0\x87\x04A%\x87\xd1\x07\xd1\x87'
    b")\x87\xd1\x07\xd1\x87(\x87\xd2\x07\xd2\x87'\x87\xd2\x07"
    b"\xd2\x87'\x86\xd3\x07\xd3\x86&\x87\xd3\x07\xd3\x87%\x86"
    b'\xd4\x07\xd4\x86%\x86\xd4\x07\xd4\x86%\x86\xd4\x07\xd4\x86'
    b'$\x87\xd4\x07\xd4\x87#\x87\xd4\x07\xd4\x87#\x87\xd4\x07'
    b'\xd4\x87#\x86\xd4\x08\xd5\x86#\x86\xd3\t\xd5\x86#\x86'
    b'\xd2\t\xd6\x86#\x87\xd0\n\xd5\x87#\x87\xcf\n\xd6\x87'
    b'#\x87\xce\n\xd7\x87$\x86\xce\t\xd8\x86%\x86\xce\x08'
    b'\xd9\x86%\x86\xcd\x08\xda\x86%\x87\xcc\x07\xda\x87%\x87'
    b"\xcc\x06\xdb\x86'\x87\xcc\x03\xdc\x87'\x87\xeb\x87(\x87"
    b'\xe9\x87)\x87\xe9\x87*\x87\xe7\x87+\x88\xe5\x88,\x87'
    b'\xe5\x87-\x88\xe3\x88.\x88\xe1\x880\x89\xdd\x892\x89'
    b'\xdb\x893\x8b\xd7\x8b2\x8d\xd4\x8e0\x91\xcf\x91.\x97'
    b'\xc5\x97,\xb5+\x88\x03\x9f\x03\x88*\x88\x05\x9d\x05\x88'
    b')\x87\t\x97\t\x87*\x85\x0c\x93\x0c\x85,\x83\x11\x8b'
    b'\x11\x83\x17'
)

# Enabled masks
_MONDAY = const(0x01)
_TUESDAY = const(0x02)
_WEDNESDAY = const(0x04)
_THURSDAY = const(0x08)
_FRIDAY = const(0x10)
_SATURDAY = const(0x20)
_SUNDAY = const(0x40)
_WEEKDAYS = const(0x1F)
_WEEKENDS = const(0x60)
_EVERY_DAY = const(0x7F)
_IS_ACTIVE = const(0x80)

# Alarm data indices
_HOUR_IDX = const(0)
_MIN_IDX = const(1)
_ENABLED_IDX = const(2)

# Pages
_HOME_PAGE = const(-1)
_RINGING_PAGE = const(-2)

class AlarmApp:
    """Allows the user to set a vibration alarm.
    """
    NAME = 'Alarm'
    ICON = icon

    def __init__(self):
        """Initialize the application."""

        self.page = _HOME_PAGE
        self.alarms = (bytearray(3), bytearray(3), bytearray(3), bytearray(3))
        self.pending_alarms = array.array('d', [0.0, 0.0, 0.0, 0.0])

        self.num_alarms = 0
        try:
            with open("alarms.txt", "r") as f:
                alarms = f.readlines()[0].split(";")
            if "" in alarms:
                alarms.remove("")
            for alarm in alarms:
                n = self.num_alarms
                h, m, st = map(int, alarm.split(","))
                self.alarms[n][0] = h
                self.alarms[n][1] = m
                self.alarms[n][2] = st
                self.num_alarms += 1
        except Exception:
            pass
        self._set_pending_alarms()

    def foreground(self):
        """Activate the application."""

        self.del_alarm_btn = widgets.Button(170, 204, 70, 35, 'DEL')
        self.hours_wid = widgets.Spinner(50, 30, 0, 23, 2)
        self.min_wid = widgets.Spinner(130, 30, 0, 59, 2, 5)
        self.day_btns = (widgets.ToggleButton(10, 145, 40, 35, 'Mo'),
                         widgets.ToggleButton(55, 145, 40, 35, 'Tu'),
                         widgets.ToggleButton(100, 145, 40, 35, 'We'),
                         widgets.ToggleButton(145, 145, 40, 35, 'Th'),
                         widgets.ToggleButton(190, 145, 40, 35, 'Fr'),
                         widgets.ToggleButton(10, 185, 40, 35, 'Sa'),
                         widgets.ToggleButton(55, 185, 40, 35, 'Su'))
        self.alarm_checks = (widgets.Checkbox(200, 57), widgets.Checkbox(200, 102),
                             widgets.Checkbox(200, 147), widgets.Checkbox(200, 192))

        self._deactivate_pending_alarms()
        self._draw()

        wasp.system.request_event(wasp.EventMask.TOUCH | wasp.EventMask.SWIPE_LEFTRIGHT | wasp.EventMask.BUTTON)
        wasp.system.request_tick(1000)

    def background(self):
        """De-activate the application."""
        if self.page > _HOME_PAGE:
            self._save_alarm()

        self.page = _HOME_PAGE

        self.del_alarm_btn = None
        del self.del_alarm_btn
        self.hours_wid = None
        del self.hours_wid
        self.min_wid = None
        del self.min_wid
        self.alarm_checks = None
        del self.alarm_checks
        self.day_btns = None
        del self.day_btns

        self._set_pending_alarms()
        try:
            if self.num_alarms == 0:
                return
            with open("alarms.txt", "w") as f:
                for n in range(self.num_alarms):
                    al = self.alarms[n]
                    f.write(",".join(map(str, al)) + ";")
        except Exception:
            pass


    def tick(self, ticks):
        """Notify the application that its periodic tick is due."""
        if self.page == _RINGING_PAGE:
            wasp.watch.vibrator.pulse(duty=50, ms=500)
            wasp.system.keep_awake()
        else:
            wasp.system.bar.update()

    def press(self, button, state):
        """"Notify the application of a button press event."""
        wasp.system.navigate(wasp.EventType.HOME)

    def swipe(self, event):
        """"Notify the application of a swipe event."""
        if self.page == _RINGING_PAGE:
            self._snooze()
        elif self.page > _HOME_PAGE:
            self._save_alarm()
            self._draw()
        else:
            wasp.system.navigate(event[0])

    def touch(self, event):
        """Notify the application of a touchscreen touch event."""
        if self.page == _RINGING_PAGE:
            self._snooze()
        elif self.page > _HOME_PAGE:
            if self.hours_wid.touch(event) or self.min_wid.touch(event):
                return
            for day_btn in self.day_btns:
                if day_btn.touch(event):
                    return
            if self.del_alarm_btn.touch(event):
                self._remove_alarm(self.page)
        elif self.page == _HOME_PAGE:
            for index, checkbox in enumerate(self.alarm_checks):
                if index < self.num_alarms and checkbox.touch(event):
                    if checkbox.state:
                        self.alarms[index][_ENABLED_IDX] |= _IS_ACTIVE
                    else:
                        self.alarms[index][_ENABLED_IDX] &= ~_IS_ACTIVE
                    self._draw(index)
                    return
            for index, alarm in enumerate(self.alarms):
                # Open edit page for clicked alarms
                if index < self.num_alarms and event[1] < 190 \
                        and 60 + (index * 45) < event[2] < 60 + ((index + 1) * 45):
                    self.page = index
                    self._draw()
                    return
                # Add new alarm if plus clicked
                elif index == self.num_alarms and 60 + (index * 45) < event[2]:
                    self.num_alarms += 1
                    self._draw(index)
                    return

    def _remove_alarm(self, alarm_index):
        # Shift alarm indices
        for index in range(alarm_index, 3):
            self.alarms[index][_HOUR_IDX] = self.alarms[index + 1][_HOUR_IDX]
            self.alarms[index][_MIN_IDX] = self.alarms[index + 1][_MIN_IDX]
            self.alarms[index][_ENABLED_IDX] = self.alarms[index + 1][_ENABLED_IDX]
            self.pending_alarms[index] = self.pending_alarms[index + 1]

        # Set last alarm to default
        self.alarms[3][_HOUR_IDX] = 8
        self.alarms[3][_MIN_IDX] = 0
        self.alarms[3][_ENABLED_IDX] = 0

        self.page = _HOME_PAGE
        self.num_alarms -= 1
        self._draw()

    def _save_alarm(self):
        alarm = self.alarms[self.page]
        alarm[_HOUR_IDX] = self.hours_wid.value
        alarm[_MIN_IDX] = self.min_wid.value
        for day_idx, day_btn in enumerate(self.day_btns):
            if day_btn.state:
                alarm[_ENABLED_IDX] |= 1 << day_idx
            else:
                alarm[_ENABLED_IDX] &= ~(1 << day_idx)

        self.page = _HOME_PAGE

    def _draw(self, update_alarm_row=-1):
        if self.page == _RINGING_PAGE:
            self._draw_ringing_page()
        elif self.page > _HOME_PAGE:
            self._draw_edit_page()
        else:
            self._draw_home_page(update_alarm_row)

    def _draw_ringing_page(self):
        draw = wasp.watch.drawable

        draw.set_color(wasp.system.theme('bright'))
        draw.fill()
        draw.set_font(fonts.sans24)
        draw.string("Alarm", 0, 150, width=240)
        draw.string("Touch to snooze", 0, 180, width=240)
        draw.blit(icon, 73, 50)
        draw.line(35, 1, 35, 239)
        draw.string('S', 10, 65)
        draw.string('t', 10, 95)
        draw.string('o', 10, 125)
        draw.string('p', 10, 155)

    def _draw_edit_page(self):
        draw = wasp.watch.drawable
        alarm = self.alarms[self.page]

        draw.fill()
        self._draw_system_bar()

        self.hours_wid.value = alarm[_HOUR_IDX]
        self.min_wid.value = alarm[_MIN_IDX]
        draw.set_font(fonts.sans28)
        draw.string(':', 110, 90-14, width=20)

        self.del_alarm_btn.draw()
        self.hours_wid.draw()
        self.min_wid.draw()
        for day_idx, day_btn in enumerate(self.day_btns):
            day_btn.state = alarm[_ENABLED_IDX] & (1 << day_idx)
            day_btn.draw()

    def _draw_home_page(self, update_alarm_row=_HOME_PAGE):
        draw = wasp.watch.drawable
        if update_alarm_row == _HOME_PAGE:
            draw.set_color(wasp.system.theme('bright'))
            draw.fill()
            self._draw_system_bar()
            draw.line(0, 50, 240, 50, width=1, color=wasp.system.theme('bright'))

        for index in range(len(self.alarms)):
            if index < self.num_alarms and (update_alarm_row == _HOME_PAGE or update_alarm_row == index):
                self._draw_alarm_row(index)
            elif index == self.num_alarms:
                # Draw the add button
                draw.set_color(wasp.system.theme('bright'))
                draw.set_font(fonts.sans28)
                draw.string('+', 100, 60 + (index * 45))

    def _draw_alarm_row(self, index):
        draw = wasp.watch.drawable
        alarm = self.alarms[index]

        self.alarm_checks[index].state = alarm[_ENABLED_IDX] & _IS_ACTIVE
        self.alarm_checks[index].draw()

        if self.alarm_checks[index].state:
            draw.set_color(wasp.system.theme('bright'))
        else:
            draw.set_color(wasp.system.theme('mid'))

        draw.set_font(fonts.sans28)
        draw.string("{:02d}:{:02d}".format(alarm[_HOUR_IDX], alarm[_MIN_IDX]), 10, 60 + (index * 45), width=120)

        draw.set_font(fonts.sans18)
        draw.string(self._get_repeat_code(alarm[_ENABLED_IDX]), 130, 70 + (index * 45), width=60)

        draw.line(0, 95 + (index * 45), 240, 95 + (index * 45), width=1, color=wasp.system.theme('bright'))

    def _draw_system_bar(self):
        sbar = wasp.system.bar
        sbar.clock = True
        sbar.draw()

    def _alert(self):
        self.page = _RINGING_PAGE
        wasp.system.wake()
        wasp.system.switch(self)

    def _snooze(self):
        now = wasp.watch.rtc.get_localtime()
        alarm = (now[0], now[1], now[2], now[3], now[4] + 10, now[5], 0, 0, 0)
        wasp.system.set_alarm(time.mktime(alarm), self._alert)
        wasp.system.navigate(wasp.EventType.HOME)

    def _set_pending_alarms(self):
        now = wasp.watch.rtc.get_localtime()
        for index, alarm in enumerate(self.alarms):
            if index < self.num_alarms and alarm[_ENABLED_IDX] & _IS_ACTIVE:
                yyyy = now[0]
                mm = now[1]
                dd = now[2]
                HH = alarm[_HOUR_IDX]
                MM = alarm[_MIN_IDX]

                # If next alarm is tomorrow increment the day
                if HH < now[3] or (HH == now[3] and MM <= now[4]):
                    dd += 1

                pending_time = time.mktime((yyyy, mm, dd, HH, MM, 0, 0, 0, 0))

                # If this is not a one time alarm find the next day of the week that is enabled
                if alarm[_ENABLED_IDX] & ~_IS_ACTIVE != 0:
                    for _i in range(7):
                        if (1 << time.localtime(pending_time)[6]) & alarm[_ENABLED_IDX] == 0:
                            dd += 1
                            pending_time = time.mktime((yyyy, mm, dd, HH, MM, 0, 0, 0, 0))
                        else:
                            break

                self.pending_alarms[index] = pending_time
                wasp.system.set_alarm(pending_time, self._alert)
            else:
                self.pending_alarms[index] = 0.0

    def _deactivate_pending_alarms(self):
        now = wasp.watch.rtc.get_localtime()
        now = time.mktime((now[0], now[1], now[2], now[3], now[4], now[5], 0, 0, 0))
        for index, alarm in enumerate(self.alarms):
            pending_alarm = self.pending_alarms[index]
            if not pending_alarm == 0.0:
                wasp.system.cancel_alarm(pending_alarm, self._alert)
                # If this is a one time alarm and in the past disable it
                if alarm[_ENABLED_IDX] & ~_IS_ACTIVE == 0 and pending_alarm <= now:
                    alarm[_ENABLED_IDX] = 0

    @staticmethod
    def _get_repeat_code(days):
        # Ignore the is_active bit
        days = days & ~_IS_ACTIVE

        if days == _WEEKDAYS:
            return "wkds"
        elif days == _WEEKENDS:
            return "wkns"
        elif days == _EVERY_DAY:
            return "evry"
        elif days == 0:
            return "once"
        else:
            return "cust"
