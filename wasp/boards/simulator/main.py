# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp

from apps.fibonacci_clock import FibonacciClockApp
wasp.system.register(FibonacciClockApp())

from apps.gameoflife import GameOfLifeApp
wasp.system.register(GameOfLifeApp())

wasp.system.run()
