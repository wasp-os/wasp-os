# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp

# Instantiate the analogue clock application and replace the default
# (digital) clock with this alternative.
from apps.chrono import ChronoApp
clock = wasp.system.quick_ring[0]
wasp.system.quick_ring[0] = ChronoApp()
wasp.system.switch(wasp.system.quick_ring[0])
wasp.system.register(clock)

from gadgetbridge import *
wasp.system.schedule()
