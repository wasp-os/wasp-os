# MicroPython board definition for the Pine64 PineTime, used out-of-tree
# via BOARD_DIR=... so that no patches to the micropython submodule are
# required.
MCU_SERIES = m4
MCU_VARIANT = nrf52
MCU_SUB_VARIANT = nrf52832
SOFTDEV_VERSION = 6.1.1

NRF_DEFINES += -DNRF52832_XXAA

MICROPY_VFS_LFS2 = 1

# Provide the full linker script list so that pnvram.ld can run *after*
# the SoftDevice script and grow the reserved RAM by 32 bytes (the RTC
# state that survives a reset, see drivers/nrf_rtc.py).
LD_FILE = $(BOARD_DIR)/pinetime.ld boards/s132_$(SOFTDEV_VERSION).ld $(BOARD_DIR)/pnvram.ld boards/memory.ld boards/common.ld

# wasp-os freezes @micropython.native and @micropython.viper code, so
# mpy-cross must know the target architecture.
MPY_CROSS_FLAGS += -march=armv7m

# Make port/wasp_modtime.c findable for MICROPY_PY_TIME_INCLUDEFILE (kept out of
# the board dir root because the nrf Makefile compiles every *.c found there)
INC += -I$(BOARD_DIR)/port
