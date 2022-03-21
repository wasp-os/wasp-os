# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

import wasp

from gadgetbridge import *
wasp.system.schedule()

# Registering normal apps *after* the schedule() ensures the
# watch will still (partially) boot even if we end up taking
# an exception during application init.
wasp.system.register('apps.flashlight.TorchApp')
wasp.system.register('apps.gallery.GalleryApp')
