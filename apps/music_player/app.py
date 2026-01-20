# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
# Copyright (C) 2020 Carlos Gil

"""Music Player for GadgetBridge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. figure:: res/screenshots/MusicPlayerApp.png
        :width: 179

        Screenshot of the Music Player application

Music Player Controller:

* Touch: play/pause
* Swipe UPDOWN: Volume down/up
* Swipe LEFTRIGHT: next/previous
"""

import wasp

import icons
import time

from micropython import const
from gadgetbridge import send_cmd

# 2-bit RLE, generated from res/music_icon.png, 358 bytes
icon = (
    b'\x02'
    b'`@'
    b'\x1e\xa4<\xa4<\xa4;\xa6?X\xec2\xf0/\xf2-'
    b'\xf4,\xc3@[n\xc3,\xc3n\xc3,\xc3n\xc3,'
    b'\xc3n\xc3,\xc3b\xc7E\xc3,\xc3]\xccE\xc3,'
    b'\xc3Z\xcfE\xc3,\xc3T\xd5E\xc3,\xc3Q\xd8E'
    b'\xc3,\xc3Q\xd8E\xc3,\xc3Q\xd8E\xc3,\xc3Q'
    b'\xd0E\xc3E\xc3,\xc3Q\xccI\xc3E\xc3,\xc3Q'
    b'\xc9L\xc3E\xc3,\xc3Q\xc5P\xc3E\xc3,\xc3Q'
    b'\xc3R\xc3E\xc3,\xc3Q\xc3R\xc3E\xc3,\xc3Q'
    b'\xc3R\xc3E\xc3+\xc4Q\xc3R\xc3E\xc3*\xc5Q'
    b'\xc3R\xc3E\xc3*\xc5Q\xc3R\xc3E\xc3*\xc5Q'
    b'\xc3R\xc3E\xc3*\xc5Q\xc3R\xc3E\xc3*\xc5Q'
    b'\xc3R\xc3E\xc3*\xc5Q\xc3R\xc3E\xc3*\xc5Q'
    b'\xc3L\xc4B\xc3E\xc3+\xc4Q\xc3I\xccE\xc3,'
    b'\xc3Q\xc3H\xcdE\xc3,\xc3Q\xc3G\xceE\xc3,'
    b'\xc3K\xc3C\xc3F\xcfE\xc3,\xc3H\xccF\xcfE'
    b'\xc3,\xc3G\xcdF\xcfE\xc3,\xc3F\xceF\xcfE'
    b'\xc3,\xc3E\xcfF\xcfE\xc3,\xc3E\xcfG\xceE'
    b'\xc3,\xc3D\xd0H\xccF\xc3,\xc3D\xd0I\xcaG'
    b'\xc3,\xc3E\xcfK\xc5J\xc3,\xc3E\xce[\xc3,'
    b'\xc3F\xcd[\xc3,\xc3G\xca]\xc3,\xc3I\xc7^'
    b'\xc3,\xc3n\xc3,\xc3n\xc3,\xc3n\xc3,\xc3n'
    b'\xc3,\xf4-\xf2/\xf02\xec?X\xa6;\xa4<\xa4'
    b'<\xa4\x1e'
)

DISPLAY_WIDTH = const(240)
ICON_SIZE = const(72)
CENTER_AT = const((DISPLAY_WIDTH - ICON_SIZE) // 2)

class MusicPlayerApp(object):
    """ Music Player Controller application."""
    NAME = 'Music'
    ICON = icon

    def __init__(self):
        self._pauseplay = wasp.widgets.GfxButton(CENTER_AT, CENTER_AT, icons.play)
        self._back = wasp.widgets.GfxButton(0, 120-12, icons.back)
        self._fwd = wasp.widgets.GfxButton(240-48, 120-12, icons.fwd)
        self._play_state = False
        self._musicstate = 'pause'
        self._artist = ''
        self._track = ''
        self._state_changed = True
        self._track_changed = True
        self._artist_changed = True

    def _fill_space(self, key):
        if key == 'top':
            wasp.watch.drawable.fill(
                x=0, y=0, w=DISPLAY_WIDTH, h=CENTER_AT)
        elif key == 'down':
            wasp.watch.drawable.fill(x=0, y=CENTER_AT + ICON_SIZE,
                                     w=DISPLAY_WIDTH,
                            h=DISPLAY_WIDTH - (CENTER_AT + ICON_SIZE))

    def foreground(self):
        """Activate the application."""
        state = wasp.system.musicstate.get('state')
        artist = wasp.system.musicinfo.get('artist')
        track = wasp.system.musicinfo.get('track')
        if state:
            self._musicstate = state
            if self._musicstate == 'play':
                self._play_state = True
            elif self._musicstate == 'pause':
                self._play_state = False
        if artist:
            self._artist = artist
        if track:
            self._track = track
        wasp.watch.drawable.fill()
        self.draw()
        wasp.system.request_tick(1000)
        wasp.system.request_event(wasp.EventMask.SWIPE_UPDOWN |
                                  wasp.EventMask.TOUCH)

    def background(self):
        """De-activate the application (without losing state)."""
        self._state_changed = True
        self._track_changed = True
        self._artist_changed = True

    def tick(self, ticks):
        wasp.system.keep_awake()
        music_state_now = wasp.system.musicstate.get('state')
        music_artist_now = wasp.system.musicinfo.get('artist')
        music_track_now = wasp.system.musicinfo.get('track')
        if music_state_now:
            if music_state_now != self._musicstate:
                self._musicstate = music_state_now
                self._state_changed = True
        else:
            self._state_changed = False
        wasp.system.musicstate = {}
        if music_track_now:
            if music_track_now != self._track:
                self._track = music_track_now
                self._track_changed = True
        else:
            self._track_changed = False
        if music_artist_now:
            if music_artist_now != self._artist:
                self._artist = music_artist_now
                self._artist_changed = True
        else:
            self._artist_changed = False
        wasp.system.musicinfo = {}
        self._update()

    def swipe(self, event):
        """
        Notify the application of a touchscreen swipe event.
        """
        if event[0] == wasp.EventType.UP:
            send_cmd('{"t":"music", "n":"volumeup"} ')
        elif event[0] == wasp.EventType.DOWN:
            send_cmd('{"t":"music", "n":"volumedown"} ')

    def touch(self, event):
        if self._pauseplay.touch(event):
            self._play_state = not self._play_state
            if self._play_state:
                self._musicstate = 'play'
                self._pauseplay.gfx = icons.pause
                self._pauseplay.draw()
                send_cmd('{"t":"music", "n":"play"} ')
            else:
                self._musicstate = 'pause'
                self._pauseplay.gfx = icons.play
                self._pauseplay.draw()
                send_cmd('{"t":"music", "n":"pause"} ')
        elif self._back.touch(event):
            send_cmd('{"t":"music", "n":"previous"} ')
        elif self._fwd.touch(event):
            send_cmd('{"t":"music", "n":"next"} ')

    def draw(self):
        """Redraw the display from scratch."""
        self._draw()

    def _draw(self):
        """Redraw the updated zones."""
        if self._state_changed:
            self._pauseplay.draw()
        if self._track_changed:
            self._draw_label(self._track, 24 + 144)
        if self._artist_changed:
            self._draw_label(self._artist, 12)
        self._back.draw()
        self._fwd.draw()

    def _draw_label(self, label, pos):
        """Redraw label info"""
        if label:
            draw = wasp.watch.drawable
            chunks = draw.wrap(label, 240)
            self._fill_space(pos)
            for i in range(len(chunks)-1):
                sub = label[chunks[i]:chunks[i+1]].rstrip()
                draw.string(sub, 0, pos + 24 * i, 240)

    def _update(self):
        if self._musicstate == 'play':
            self._play_state = True
            self._pauseplay.gfx = icons.pause
        elif self._musicstate == 'pause':
            self._play_state = False
            self._pauseplay.gfx = icons.play
        self._draw()

    def update(self):
        pass
