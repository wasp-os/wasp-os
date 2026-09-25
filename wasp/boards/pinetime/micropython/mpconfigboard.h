// SPDX-License-Identifier: LGPL-3.0-or-later
// Copyright (C) 2020 Daniel Thompson
//
// MicroPython board configuration for the Pine64 PineTime.

#define MICROPY_HW_BOARD_NAME       "Pine64 PineTime"
#define MICROPY_HW_MCU_NAME         "NRF52832"

// The console is the Nordic UART Service (BLE); no wired UART REPL.
#define MICROPY_PY_BLE_NUS          (1)
#define MICROPY_PY_MACHINE_UART     (0)

#define MICROPY_PY_MACHINE_HW_PWM   (1)
#define MICROPY_PY_MACHINE_TIMER_NRF (1)
#define MICROPY_PY_MACHINE_RTCOUNTER (1)
#define MICROPY_PY_MACHINE_I2C      (1)
#define MICROPY_PY_MACHINE_ADC      (1)
#define MICROPY_PY_MACHINE_TEMP     (1)
#define MICROPY_HW_ENABLE_RNG       (1)
// The battery voltage is sensed through a high impedance divider
#define MICROPY_HW_SAADC_ACQTIME    NRF_SAADC_ACQTIME_40US

// wasp-os relies on micropython.schedule() to run application code outside
// interrupt context (see wasp.py Manager._schedule/_work). Upstream only
// forces MICROPY_ENABLE_SCHEDULER on for boards with USB device support;
// the PineTime has none, so it must be requested explicitly here, or it
// silently falls back to the ROM-level default (off, for nRF52832 without
// USB) and every call to micropython.schedule() raises AttributeError.
#define MICROPY_ENABLE_SCHEDULER    (1)
#define MICROPY_SCHEDULER_STATIC_NODES (1)

#define MICROPY_HW_HAS_LED          (0)
#define MICROPY_HW_LED_COUNT        (0)
#define MICROPY_HW_LED_PULLUP       (0)

// Features wasp-os relies on that sit above the default nrf52832 level
#define MICROPY_EMIT_THUMB          (1)
#define MICROPY_EMIT_INLINE_THUMB   (1)
#define MICROPY_PY_JSON             (1)
#define MICROPY_PY_SYS_STDFILES     (1)
#define MICROPY_PY_BUILTINS_INPUT   (1)
#define MICROPY_PY_TIME_GMTIME_LOCALTIME_MKTIME (1)
#define MICROPY_PY_TIME_TIME_TIME_NS (1)
#define MICROPY_PY_TIME_INCLUDEFILE "wasp_modtime.c"

// The filesystem lives on the external SPI NOR flash (LittleFS2), mounted
// from watch.py. Do not carve an internal flash filesystem or ROMFS.
#define MICROPY_MBFS                (0)
#define MICROPY_VFS                 (1)
#define MICROPY_HW_ENABLE_INTERNAL_FLASH_STORAGE (0)
#define MICROPY_VFS_ROM             (0)

// machine.bootloader() -> reboot into the wasp-bootloader OTA DFU mode
void wasp_enter_bootloader(void);
#define MICROPY_BOARD_ENTER_BOOTLOADER(nargs, args) wasp_enter_bootloader()

// Feed the bootloader's watchdog from a timer interrupt (waspnrf module)
void wasp_early_init(void);
#define MICROPY_BOARD_EARLY_INIT() wasp_early_init()

// UART config (not connected on production units)
#define MICROPY_HW_UART1_RX         (17)
#define MICROPY_HW_UART1_TX         (11)
#define MICROPY_HW_UART1_HWFC       (0)

// SPI0 config
#define MICROPY_HW_SPI0_NAME        "SPI0"
#define MICROPY_HW_SPI0_SCK         (2)
#define MICROPY_HW_SPI0_MOSI        (3)
#define MICROPY_HW_SPI0_MISO        (4)

#define MICROPY_HW_PWM0_NAME        "PWM0"
#define MICROPY_HW_PWM1_NAME        "PWM1"
#define MICROPY_HW_PWM2_NAME        "PWM2"

#define HELP_TEXT_BOARD_LED         ""
