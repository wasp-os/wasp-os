# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Michiel W. Beijen

"""SPI NOR flash block device for LittleFS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Exposes the chip's own 4 KiB erase sector as the LittleFS block size and
implements the erase ioctl, so LittleFS (which only ever programs freshly
erased bytes) writes straight to the chip without a read-modify-write
sector cache. The chip is kept in deep power down between operations.
"""

import time
from micropython import const

_SEC_BITS = const(12)  # 4 KiB erase sectors
_SEC_SIZE = const(4096)
_PAGE = const(256)     # page-program granularity

_READ = const(0x03)
_PP = const(0x02)      # page program
_SE = const(0x20)      # sector erase
_WREN = const(0x06)    # write enable
_RDSR1 = const(0x05)   # read status register 1
_RDID = const(0x9f)    # read JEDEC ID
_DP = const(0xb9)      # deep power down
_RDP = const(0xab)     # release from deep power down

class NORFlash:
    """SPI NOR flash driver.

    .. automethod:: __init__
    """
    def __init__(self, spi, cs):
        """Specify the bus and chip select of the NOR flash.

        :param machine.SPI spi: The SPI bus the flash is attached to.
        :param machine.Pin cs:  The chip select pin.
        """
        self._spi = spi
        self._cs = cs
        self._buf = bytearray(4)
        self._mv = memoryview(self._buf)
        self._chk = bytearray(32)

        self._wake()
        mv = self._mv
        mv[0] = _RDID
        cs(0)
        spi.write_readinto(mv, mv)
        cs(1)
        self._cmd(_DP)
        self._size = 1 << mv[3]
        if self._size > 1 << 24:
            raise ValueError('only 3 byte addressing is supported')

    def readblocks(self, blocknum, buf, offset=0):
        self._read(offset + (blocknum << _SEC_BITS), buf)

    def writeblocks(self, blocknum, buf, offset=None):
        addr = blocknum << _SEC_BITS
        if offset is None:
            # Simple (whole block) protocol: the caller expects an erase.
            self._erase(addr)
        else:
            addr += offset
        self._program(addr, memoryview(buf))

    def ioctl(self, op, arg):
        if op == 4:  # block count
            return self._size >> _SEC_BITS
        if op == 5:  # block size
            return _SEC_SIZE
        if op == 6:  # erase block
            self._erase(arg << _SEC_BITS)
            return 0
        # 1 (init), 2 (deinit), 3 (sync): nothing to do

    def _cmd(self, cmd):
        self._buf[0] = cmd
        self._cs(0)
        self._spi.write(self._mv[:1])
        self._cs(1)

    def _wake(self):
        self._cmd(_RDP)
        time.sleep_us(100)

    def _start(self, cmd, addr):
        mv = self._mv
        mv[0] = cmd
        mv[1] = addr >> 16
        mv[2] = (addr >> 8) & 0xff
        mv[3] = addr & 0xff
        self._cs(0)
        self._spi.write(mv)

    def _wait_rdy(self):
        mv = self._mv
        while True:
            mv[0] = _RDSR1
            self._cs(0)
            self._spi.write_readinto(mv[:2], mv[:2])
            self._cs(1)
            if not mv[1] & 1:
                break
            time.sleep_ms(1)
        self._cmd(_DP)

    def _read(self, addr, buf):
        self._wake()
        self._start(_READ, addr)
        self._spi.readinto(buf)
        self._cs(1)
        self._cmd(_DP)

    def _erase(self, addr):
        # Skip the erase (and its wear) if the sector is already blank.
        chk = self._chk
        blank = True
        self._wake()
        self._start(_READ, addr)
        for _ in range(_SEC_SIZE // len(chk)):
            self._spi.readinto(chk)
            if any(b != 0xff for b in chk):
                blank = False
                break
        self._cs(1)
        if blank:
            self._cmd(_DP)
            return
        self._cmd(_WREN)
        self._start(_SE, addr)
        self._cs(1)
        self._wait_rdy()

    def _program(self, addr, mv):
        nbytes = len(mv)
        start = 0
        while nbytes:
            # A page program wraps around within the page: never cross one.
            n = min(nbytes, _PAGE - (addr & (_PAGE - 1)))
            self._wake()
            self._cmd(_WREN)
            self._start(_PP, addr)
            self._spi.write(mv[start:start + n])
            self._cs(1)
            self._wait_rdy()
            nbytes -= n
            start += n
            addr += n
