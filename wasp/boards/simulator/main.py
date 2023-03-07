# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp

# Test app is used a lot on the simulator. Let's make sure it is
# registered by default.
wasp.system.register('apps.test.TestApp')

# Ensure there's something interesting to look at ;-)
wasp.system.set_music_info({
        'track': 'Tasteless Brass Duck',
        'artist': 'Dreams of Bamboo',
    })

wasp.system.set_weather_info({
    'temp': 295,
    'hum': 100,
    'txt': 'Cloudy',
    'wind': 25,
    'loc': 'Toronto'
})


# Increase the display blanking time to avoid spamming the console
# with backlight activations.
wasp.system.blank_after = 300

# Replace the default (digital) clock with an alternative
# (digital) clock with this alternative.
#wasp.system.register('apps.chrono.ChronoApp', watch_face=True)

# Enable the demostration application
#wasp.system.register('apps.demo.DemoApp')

# Adopt a basic all-orange theme
#wasp.system.set_theme(
#        b'\xff\x00'     # ble
#        b'\xff\x00'     # scroll-indicator
#        b'\xff\x00'     # battery
#        b'\xff\x00'     # status-clock
#        b'\xff\x00'     # notify-icon
#        b'\xff\x00'     # bright
#        b'\xbe\xe0'     # mid
#        b'\xff\x00'     # ui
#        b'\xff\x00'     # spot1
#        b'\xff\x00'     # spot2
#        b'\x00\x0f'     # contrast
#    )

wasp.system.run()
