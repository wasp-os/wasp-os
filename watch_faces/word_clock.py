# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
# Copyright (C) 2021 Brendan Sleight


"""Word clock
~~~~~~~~~~~~~~~~

Shows a time as words together with a battery meter and the date.

.. figure:: res/screenshots/WordClockApp.png
    :width: 179
"""

import wasp

MONTH = 'JanFebMarAprMayJunJulAugSepOctNovDec'


class WordClockApp():
    """Simple digital clock application."""
    NAME = 'WordClk'

    def foreground(self):
        """Activate the application.

        Configure the status bar, redraw the display and request a periodic
        tick callback every second.
        """
        wasp.system.bar.clock = False
        self._draw(True)
        wasp.system.request_tick(1000)

    def sleep(self):
        """Prepare to enter the low power mode.

        :returns: True, which tells the system manager not to automatically
                  switch to the default application before sleeping.
        """
        return True

    def wake(self):
        """Return from low power mode.

        Time will have changes whilst we have been asleep so we must
        udpate the display (but there is no need for a full redraw because
        the display RAM is preserved during a sleep.
        """
        self._draw()

    def tick(self, ticks):
        """Periodic callback to update the display."""
        self._draw()

    def preview(self):
        """Provide a preview for the watch face selection."""
        wasp.system.bar.clock = False
        self._draw(True)

    def _draw(self, redraw=False):
        """Draw or lazily update the display.

        The updates are as lazy by default and avoid spending time redrawing
        if the time on display has not changed. However if redraw is set to
        True then a full redraw is be performed.
        """
        draw = wasp.watch.drawable
        hi =  wasp.system.theme('bright')

        now = wasp.watch.rtc.get_localtime()

        if redraw:
            # Clear the display and draw that static parts of the watch face
            draw.fill()

            # Redraw the status bar
            wasp.system.bar.draw()
        else:
            # Redraw the status bar if necessary. This does not overlap the
            # other elements on the screen.
            wasp.system.bar.update()

            # Only continue drawing if the minute has changed.
            if self._min == now[4]:
                return

        draw.set_color(hi)

        # Format the month as text
        month = now[1] - 1
        month = MONTH[month*3:(month+1)*3]
        # Record the minute that is currently being displayed
        self._hour = now[3]
        self._min = now[4]

        # Testing
        # self._hour = 23
        # self._min = 59
        
        # Convert to words
        part_day = ""
        hour = ""
        part_hour = ""
        minute_words= ""

        part_day = ""

        hours_a = ["midnight", "one", "two", 
                "three", "four", "five", 
                "six", "seven", "eight", 
                "nine", "ten", "eleven", 
                "twelve",
                "one", "two", 
                "three", "four", "five", 
                "six", "seven", "eight", 
                "nine", "ten", "eleven"]
        if (self._min > 32):
            hour = hours_a[(self._hour + 1) % 24]
        else:
            hour = hours_a[self._hour % 24]
        if (hour != "midnight" and hour != "twelve"):
            if (self._hour >= 22):
                part_day = " at night"
            elif (self._hour >= 18):
                part_day = " in the evening"
            elif (self._hour >= 12):
                part_day = " in the afternoon"
            elif (self._hour >= 6):
                part_day = " in the morning"
            elif (self._hour >= 3):
                part_day = " in the early hours"
            elif (self._hour >= 0):
                part_day = " at night"

        if (self._min > 57):
            part_hour = ""
        elif (self._min > 52):
            part_hour = "five to "
        elif (self._min > 47):
            part_hour = "ten to "
        elif (self._min > 42):
            part_hour = "quarter to "
        elif (self._min > 37):
            part_hour = "twenty to "
        elif (self._min > 32):
            part_hour = "twenty-five to "
        elif (self._min > 27):
            part_hour = "half past "
        elif (self._min > 22):
            part_hour = "twenty-five past "
        elif (self._min > 17):
            part_hour = "twenty past "
        elif (self._min > 12):
            part_hour = "quarter past "
        elif (self._min > 7):
            part_hour = "ten past "
        elif (self._min > 2):
            part_hour = "five past "
        else:
            part_hour = ""

        minute_words_int = (self._min % 5)
        if (minute_words_int == 4):
            minute_words = "almost"
        if (minute_words_int == 3):
            minute_words = "coming up to"
        if (minute_words_int == 2):
            minute_words = "after"
        if (minute_words_int == 1):
            minute_words = "just gone"

        self._words = ""
        if (minute_words !=""):
            self._words = minute_words + "\n" 
        if (part_hour !=""):
            self._words = self._words + part_hour + "\n"
        self._words = self._words + hour + "\n" 
        if (part_day !=""):
            self._words = self._words + part_day 
        
        # No capitilise in Micropython 
        # ASCII convert 
        self._words = chr(ord(self._words[0])-32) + self._words[1:]
        
        # Some phases may be 5 lines long, some may be 1 
        draw.fill(0, 0, 48)

        chunks = draw.wrap(self._words, 240)
        lines_of_text = len(chunks)-1
        offset_y=int(((5-lines_of_text/2)*26))

        for i in range(len(chunks)-1):
            sub = self._words[chunks[i]:chunks[i+1]].rstrip()
            draw.string(sub, 0, offset_y+26*i, 240)        

        draw.string('{} {} {}'.format(now[2], month, now[0]),
                0, 214, width=240)
