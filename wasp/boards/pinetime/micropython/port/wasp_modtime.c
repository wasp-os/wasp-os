// SPDX-License-Identifier: LGPL-3.0-or-later
//
// Port hooks for the time module, textually included by extmod/modtime.c via
// MICROPY_PY_TIME_INCLUDEFILE. wasp-os keeps wall clock time in Python
// (drivers/nrf_rtc.py) and only calls time.localtime(secs) and
// time.mktime(tuple); the argument-less forms simply report the epoch.

#include "py/obj.h"
#include "shared/timeutils/timeutils.h"

static void mp_time_localtime_get(timeutils_struct_time_t *tm) {
    timeutils_seconds_since_epoch_to_struct_time(0, tm);
}

static mp_obj_t mp_time_time_get(void) {
    return MP_OBJ_NEW_SMALL_INT(0);
}
