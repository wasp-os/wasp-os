# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp

from apps.alarm import AlarmApp
wasp.system.register(AlarmApp())

from apps.fibonacci_clock import FibonacciClockApp
wasp.system.register(FibonacciClockApp())

from apps.gameoflife import GameOfLifeApp
wasp.system.register(GameOfLifeApp())

from apps.snake import SnakeGameApp
wasp.system.register(SnakeGameApp())

from apps.calc import CalculatorApp
wasp.system.register(CalculatorApp())

from apps.musicplayer import MusicPlayerApp
wasp.system.register(MusicPlayerApp())
wasp.system.set_music_info({
        'track': 'Tasteless Brass Duck',
        'artist': 'Dreams of Bamboo',
    })

wasp.system.run()
