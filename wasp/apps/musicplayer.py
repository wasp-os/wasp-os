# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
# Copyright (C) 2020 Carlos Gil

"""Music Player for GadgetBridge
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. figure:: res/MusicApp.png
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

class MusicPlayerApp(object):
    """ Music Player Controller application."""
    NAME = 'Music'
    ICON = icons.headset

    def __init__(self):

        self._play_icon = icons.play
        self._pause_icon = icons.pause
        self._play_state = False
        self._icon_state = self._play_icon
        self._max_display = 240
        self._icon_size = 72
        self._center_at = int((self._max_display - self._icon_size)/2)
        self._musicstate = 'pause'
        self._artist = ''
        self._track = ''
        self._state_changed = True
        self._track_changed = True
        self._artist_changed = True

    def _send_cmd(self, cmd):
        print('\r')
        for i in range(1):
            for i in range(0, len(cmd), 20):
                print(cmd[i: i + 20], end='')
                time.sleep(0.2)
            print(' ')
        print(' ')

    def _fill_space(self, key):
        if key == 'top':
            wasp.watch.drawable.fill(
                x=0, y=0, w=self._max_display, h=self._center_at)
        elif key == 'mid':
            wasp.watch.drawable.fill(x=self._center_at, y=self._center_at,
                                     w=self._icon_size, h=self._icon_size)
        elif key == 'down':
            wasp.watch.drawable.fill(x=0, y=self._center_at + self._icon_size,
                                     w=self._max_display,
                            h=self._max_display - (self._center_at + self._icon_size))

    def foreground(self):
        """Activate the application."""
        state = wasp.system.musicstate.get('state')
        artist = wasp.system.musicinfo.get('artist')
        track = wasp.system.musicinfo.get('track')
        if state:
            self._musicstate = state
            if self._musicstate == 'play':
                self._play_state = True
                self._icon_state = self._pause_icon
            elif self._musicstate == 'pause':
                self._play_state = False
                self._icon_state = self._play_icon
        if artist:
            self._artist = artist
        if track:
            self._track = track
        wasp.watch.drawable.fill()
        self.draw()
        wasp.system.request_tick(1000)
        wasp.system.request_event(wasp.EventMask.SWIPE_UPDOWN |
                                  wasp.EventMask.SWIPE_LEFTRIGHT |
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
            self._send_cmd('{"t":"music", "n":"volumeup"} ')
        elif event[0] == wasp.EventType.DOWN:
            self._send_cmd('{"t":"music", "n":"volumedown"} ')
        elif event[0] == wasp.EventType.LEFT:
            self._send_cmd('{"t":"music", "n":"next"} ')
        elif event[0] == wasp.EventType.RIGHT:
            self._send_cmd('{"t":"music", "n":"previous"} ')

    def touch(self, event):
        self._play_state = not self._play_state
        if self._play_state:
            self._musicstate = 'play'
            self._icon_state = self._pause_icon
            self._draw_button()
            self._send_cmd('{"t":"music", "n":"play"} ')
        else:
            self._musicstate = 'pause'
            self._icon_state = self._play_icon
            self._draw_button()
            self._send_cmd('{"t":"music", "n":"pause"} ')

    def draw(self):
        """Redraw the display from scratch."""
        self._draw()

    def _draw(self):
        """Redraw the updated zones."""
        if self._state_changed:
            self._draw_button()
        if self._track_changed:
            self._draw_label(self._track, 24 + 144)
        if self._artist_changed:
            self._draw_label(self._artist, 12)

    def _draw_button(self):
        """Redraw player button"""
        self._fill_space('mid')
        wasp.watch.drawable.blit(self._icon_state, self._center_at,
                                 self._center_at)

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
            self._icon_state = self._pause_icon
        elif self._musicstate == 'pause':
            self._play_state = False
            self._icon_state = self._play_icon
        self._draw()

    def update(self):
        pass
