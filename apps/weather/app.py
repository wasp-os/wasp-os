# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
# Copyright (C) 2020 Carlos Gil

"""Weather for GadgetBridge and wasp-os companion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. figure:: res/screenshots/WeatherApp.png
        :width: 179

        Screenshot of the Weather application

"""

import wasp

import icons
import time
import fonts.sans36

# 2-bit RLE, generated from res/weather_icon.png, 309 bytes
icon = (
    b'\x02'
    b'`@'
    b'\x1e\xa4<\xa4<\xa4;\xa5?Y\xec2\xf0/\xf2-'
    b'\xf4,\xc3@;n\xc3,\xc3n\xc3,\xc3n\xc3,'
    b'\xc3n\xc3,\xc3n\xc3,\xc3n\xc3,\xc3n\xc3,'
    b'\xc3n\xc3,\xc3n\xc3,\xc3O\x80\xd3\x87X\xc3,'
    b'\xc3M\x8bV\xc3,\xc3K\x8fT\xc3,\xc3J\x91S'
    b'\xc3,\xc3I\x93R\xc3,\xc3H\x95Q\xc3,\xc3H'
    b'\x95Q\xc3,\xc3G\x97P\xc3,\xc3G\x97P\xc3+'
    b'\xc4F\x99O\xc3*\xc5F\x99O\xc3*\xc5F\x99O'
    b'\xc3*\xc5F\x99O\xc3*\xc5F\x99O\xc3*\xc5F'
    b'\x99\xc4K\xc3*\xc5F\x8e\xc5\x84\xc1\x81\xc5J\xc3*'
    b'\xc5G\x8c\xc8\x81\xcaH\xc3+\xc4G\x83\xc5\x83\xd6F'
    b'\xc3,\xc3H\x81\xe0E\xc3,\xc3G\xe2E\xc3,\xc3'
    b'G\xe3D\xc3,\xc3F\xe4D\xc3,\xc3F\xe4D\xc3'
    b',\xc3F\xe4D\xc3,\xc3F\xe4D\xc3,\xc3F\xe3'
    b'E\xc3,\xc3G\xe2E\xc3,\xc3G\xe1F\xc3,\xc3'
    b'H\xc9A\xccC\xc5H\xc3,\xc3J\xc5E\xc9Q\xc3'
    b',\xc3V\xc5S\xc3,\xc3n\xc3,\xc3n\xc3,\xc3'
    b'n\xc3,\xc3n\xc3,\xc3n\xc3,\xc3n\xc3,\xf4'
    b'-\xf2/\xf02\xec?X\xc0\xdb\xe6;\xe4<\xe4<'
    b'\xe4\x1e'
)

class WeatherApp(object):
    """ Weather application."""
    NAME = 'Weather'
    ICON = icon
    
    def __init__(self):
        self._temp = -1
        self._hum = 0
        self._txt = ''
        self._wind = 0
        self._loc = ''
        self._temp_changed = True
        self._hum_changed = True
        self._txt_changed = True
        self._wind_changed = True
        self._loc_changed = True

    def foreground(self):
        """Activate the application."""
        get_info = wasp.system.weatherinfo.get
        temp = get_info('temp')
        hum = get_info('hum')
        txt = get_info('txt')
        wind = get_info('wind')
        loc = get_info('loc')
        if temp:
            self._temp = temp
        if hum:
            self._hum = hum
        if txt:
            self._txt = txt
        if wind:
            self._wind = wind
        if loc:
            self._loc = loc
        wasp.watch.drawable.fill()
        self.draw()
        wasp.system.request_tick(1000)

    def background(self):
        """De-activate the application (without losing state)."""
        self._temp_changed = True
        self._hum_changed = True
        self._txt_changed = True
        self._wind_changed = True
        self._loc_changed = True

    def tick(self, ticks):
        wasp.system.keep_awake()
        get_info = wasp.system.weatherinfo.get
        temp_now = get_info('temp')
        hum_now = get_info('hum')
        txt_now = get_info('txt')
        wind_now = get_info('wind')
        loc_now = get_info('loc')
        if temp_now:
            if temp_now != self._temp:
                self._temp = temp_now
                self._temp_changed = True
        else:
            self._temp_changed = False
        if hum_now:
            if hum_now != self._hum:
                self._hum = hum_now
                self._hum_changed = True
        else:
            self._hum_changed = False
        if txt_now:
            if txt_now != self._txt:
                self._txt = txt_now
                self._txt_changed = True
        else:
            self._txt_changed = False
        if wind_now:
            if wind_now != self._wind:
                self._wind = wind_now
                self._wind_changed = True
        else:
            self._wind_changed = False
        if loc_now:
            if loc_now != self._loc:
                self._loc = loc_now
                self._loc_changed = True
        else:
            self._loc_changed = False
        wasp.system.weatherinfo = {}
        self._update()

    def draw(self):
        """Redraw the display from scratch."""
        self._draw()

    def _draw(self):
        """Redraw the updated zones."""
        draw = wasp.watch.drawable
        if self._temp != -1:
            units = wasp.system.units
            temp = self._temp - 273.15
            wind = self._wind
            wind_units = "km/h"
            if units == "Imperial":
                temp = (temp * 1.8) + 32
                wind = wind / 1.609
                wind_units = "mph"
            temp = round(temp)
            wind = round(wind)
            if self._temp_changed:
                self._draw_label(str(temp), 54, 36)
            if self._hum_changed:
                self._draw_label("Humidity: {}%".format(self._hum), 160)
            if self._txt_changed:
                self._draw_label(self._txt, 12)
            if self._wind_changed:
                self._draw_label("Wind: {}{}".format(wind, wind_units), 120)
            if self._loc_changed:
                self._draw_label(self._loc, 200)
        else:
            if self._temp_changed:
                draw.fill()
                self._draw_label("No weather data.", 120)

    def _draw_label(self, label, pos, size = 24):
        """Redraw label info"""
        if label:
            draw = wasp.watch.drawable
            draw.reset()
            if size == 36:
                draw.set_font(fonts.sans36)
            
            draw.string(label, 0, pos, 240)

    def _update(self):
        self._draw()

    def update(self):
        pass
