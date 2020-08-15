# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson
"""Gadgetbridge/Bangle.js protocol

Currently implemented messages are:

 * t:"notify", id:int, src,title,subject,body,sender,tel:string - new
   notification
 * t:"notify-", id:int - delete notification
 * t:"alarm", d:[{h,m},...] - set alarms
 * t:"find", n:bool - findDevice
 * t:"vibrate", n:int - vibrate
 * t:"weather", temp,hum,txt,wind,loc - weather report
 * t:"musicstate", state:"play/pause",position,shuffle,repeat - music
   play/pause/etc
 * t:"musicinfo", artist,album,track,dur,c(track count),n(track num) -
   currently playing music track
 * t:"call", cmd:"accept/incoming/outgoing/reject/start/end", name: "name", number: "+491234" - call
"""

import io
import json
import sys
import wasp

# JSON compatibility
null = None
true = True
false = False

def _info(msg):
    json.dump({'t':'info', 'msg':msg}, sys.stdout)
    sys.stdout.write('\r\n')

def _error(msg):
    json.dump({'t':'error', 'msg':msg}, sys.stdout)
    sys.stdout.write('\r\n')

def GB(cmd):
    task = cmd['t']
    del cmd['t']

    try:
        if task == 'find':
            wasp.watch.vibrator.pin(not cmd['n'])
        elif task == 'notify':
            id = cmd['id']
            del cmd['id']
            wasp.system.notify(id, cmd)
        elif task == 'notify-':
            wasp.system.unnotify(cmd['id'])
        else:
            pass
            #_info('Command "{}" is not implemented'.format(cmd))
    except Exception as e:
        msg = io.StringIO()
        sys.print_exception(e, msg)
        _error(msg.getvalue())
        msg.close()


