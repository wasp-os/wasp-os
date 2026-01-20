# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2022 Francesco Gazzetta

"""Digital clock with weekday
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Shows a time (as HH:MM) together with a battery meter, the date, and the weekday.

.. figure:: res/screenshots/WeekClockApp.png
    :width: 179
"""

from apps.user.clock import ClockApp, MONTH

WDAY = 'MonTueWedThuFriSatSun'

class WeekClockApp(ClockApp):
    NAME = 'WeekClk'

    def _day_string(self, now):
        """Produce a string representing the current day"""
        # Format the month as text
        month = now[1] - 1
        month = MONTH[month*3:(month+1)*3]

        # Format the weekday as text
        wday = now[6]
        wday = WDAY[wday*3:(wday+1)*3]

        return '{} {} {} {}'.format(wday, now[2], month, now[0])
