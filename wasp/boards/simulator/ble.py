# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2021 Francesco Gazzetta

_is_enabled = True

def enable():
    global _is_enabled
    _is_enabled = True

def disable():
    global _is_enabled
    _is_enabled = False

def enabled():
    return _is_enabled
