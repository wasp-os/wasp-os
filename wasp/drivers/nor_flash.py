# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Michiel W. Beijen

"""Cache-free SPI NOR flash block device for LittleFS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Exposes the chip's own 4 KiB erase sector as the LittleFS block size and
implements the erase ioctl, so LittleFS (which only ever programs freshly
erased bytes) writes straight to the chip. The generic FlashDevice base
class instead presents 512 byte blocks and emulates them with a
read-modify-write cache of a whole sector, which permanently costs 4 KiB
of heap -- more than 10% of the nRF52832's -- as one contiguous block.
"""

from micropython import const
from bdevice import BlockDevice
from flash.flash_spi import FLASH

_SEC_BITS = const(12)  # 4 KiB erase sectors
_PAGE = const(256)     # page-program granularity
_WREN = const(6)
_PP = const(1)         # index into the command set: page program

class NORFlash(FLASH):
    """SPI NOR flash driver.

    .. automethod:: __init__
    """
    def __init__(self, spi, cspins, size=None, verbose=True):
        """Specify the bus and chip select(s) of the NOR flash.

        :param machine.SPI spi: The SPI bus the flash is attached to.
        :param tuple cspins:    Chip select pins, one per chip.
        :param int size:        Size per chip in KiB, or None to detect.
        :param bool verbose:    Report the detected chip(s) on the console.
        """
        self._spi = spi
        self._cspins = cspins
        self._ccs = None
        self._bufp = bytearray(6)
        self._mvp = memoryview(self._bufp)
        self._page_size = _PAGE
        self._buf = bytearray(32)  # used by is_empty()
        self._mvbuf = memoryview(self._buf)
        self.sec_size = 1 << _SEC_BITS
        size = self.scan(verbose, size)
        BlockDevice.__init__(self, _SEC_BITS, len(cspins), size * 1024)
        if size <= 4096:
            self._cmds = b'\x03\x02\x20'  # 3 byte addresses
            self._cmdlen = 4
        else:
            self._cmds = b'\x13\x12\x21'  # 4 byte addresses
            self._cmdlen = 5

    def readblocks(self, blocknum, buf, offset=0):
        self.rdchip(offset + (blocknum << _SEC_BITS), memoryview(buf))

    def writeblocks(self, blocknum, buf, offset=None):
        addr = blocknum << _SEC_BITS
        if offset is None:
            # Simple (whole block) protocol: the caller expects an erase.
            self._sector_erase(addr)
        else:
            addr += offset
        self._program(addr, memoryview(buf))

    def ioctl(self, op, arg):
        if op == 4:  # block count
            return self._a_bytes >> _SEC_BITS
        if op == 5:  # block size
            return 1 << _SEC_BITS
        if op == 6:  # erase block
            self._sector_erase(arg << _SEC_BITS)
            return 0
        # 1 (init), 2 (deinit), 3 (sync): nothing to do

    def _program(self, addr, mv):
        mvp = self._mvp
        nbytes = len(mv)
        start = 0
        while nbytes:
            # A page program wraps around within the page: never cross one.
            n = min(nbytes, _PAGE - (addr & (_PAGE - 1)))
            self._getaddr(addr, 1)
            cs = self._ccs
            self._wake()
            self._cmd(_WREN)
            mvp[0] = self._cmds[_PP]
            cs(0)
            self._spi.write(mvp[:self._cmdlen])
            self._spi.write(mv[start:start + n])
            cs(1)
            self._wait_rdy()
            nbytes -= n
            start += n
            addr += n

    # FlashDevice's cached byte-level API is not available on this driver.
    def sync(self):
        return 0

    def read(self, addr, mvb):
        self.rdchip(addr, mvb)
        return mvb

    def write(self, addr, mvb):
        raise OSError('unsupported')
