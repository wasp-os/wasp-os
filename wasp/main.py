# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp
from gadgetbridge import *
wasp.system.schedule()

theme_string = b'{\xef{\xef{\xef\xff\xe0\xe7<{\xef\xff\xff\xbd\xb69\xff\xff\x00\xdd\xd0\x00\x0f'
wasp.system.set_theme(theme_string)
