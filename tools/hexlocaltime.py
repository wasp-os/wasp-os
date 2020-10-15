from datetime import datetime, timedelta
from binascii import hexlify
import struct

dt = datetime.now() + timedelta(seconds=20)

localtime = struct.pack('HBBBBB', dt.year, dt.month, dt.day, dt.hour, dt.minute,
                        dt.second)

print('Set localtime: {} --> Hex: {}'.format(dt.strftime("%Y-%m-%d %H:%M:%S"),
                                             hexlify(localtime).decode().upper()))
