// SPDX-License-Identifier: LGPL-3.0-or-later
// Copyright (C) 2020 Daniel Thompson
//
// Small pieces of nRF port glue that wasp-os needs and that used to live in
// the wasp-os fork of MicroPython. Kept here so that an unmodified upstream
// MicroPython can be used.

#include "py/runtime.h"
#include "py/mphal.h"
#include "nrf.h"

#include "hal/nrf_gpio.h"
#include "hal/nrf_wdt.h"
#include "hal/nrf_clock.h"
#include "soc/nrfx_coredep.h"

#if MICROPY_PY_BLE_NUS
#include "drivers/bluetooth/ble_uart.h"
#endif

// --- watchdog feeder --------------------------------------------------------
//
// The wasp-bootloader starts a 5 second watchdog before handing over to us
// (see "Watchdog protocol" in docs/wasp.rst). wasp_wdt_feed() is the only
// thing that feeds it: once here at early init, and after that from the
// 8 Hz RTC callback in watch.py via waspnrf.feed(). The RTC callback runs in
// interrupt context, so long-running Python code does not starve it.
//
// It never feeds while the button is held down, so holding the button always
// resets the watch into the bootloader. Once Python has called
// waspnrf.alive() for the first time it also requires that it keeps doing
// so: wasp's system manager calls it on every tick, and if those calls stop
// for WASP_WDT_GRACE_MS the watchdog resets the watch. Without this a fatal
// error (whose handler is an endless loop) or a hung main loop left the
// watch dead with the RTC interrupt still feeding the watchdog. Until the
// first call it is fed unconditionally, which covers booting and keeps the
// REPL usable if booting fails with a Python exception.
//
// (This used to be fed from a TIMER4 interrupt as well, but the port's
// timer_init0() uninitialises TIMER4 moments after MICROPY_BOARD_EARLY_INIT,
// so that interrupt never ran.)

#ifndef WASP_WDT_BUTTON
#define WASP_WDT_BUTTON      (13)   // PineTime: active high
#define WASP_WDT_BUTTON_EN   (15)   // must be driven high to read the button
#endif

#define WASP_WDT_GRACE_MS    (5000)

static bool wasp_wdt_armed;
static uint32_t wasp_wdt_last_alive;

static void wasp_wdt_feed(void) {
    if (nrf_gpio_pin_read(WASP_WDT_BUTTON)) {
        return;
    }
    if (wasp_wdt_armed &&
        (uint32_t)(mp_hal_ticks_ms() - wasp_wdt_last_alive) > WASP_WDT_GRACE_MS) {
        return;
    }
    nrf_wdt_reload_request_set(NRF_WDT, NRF_WDT_RR0);
}

// The bootloader stops the LFCLK right before jumping to us, and MicroPython
// starts it again in rtc1_init_time_ticks(). nRF52832 anomaly 132: a start
// issued 66..138us after a stop can leave the clock dead, which freezes
// time.ticks_ms() and makes every delay loop spin forever. Bring the clock up
// here with safe timing and bounded waits so the port finds it running.
static void wasp_start_lfclk(void) {
    uint32_t guard = 100000;
    while (nrf_clock_lf_is_running(NRF_CLOCK) && guard--) {
    }
    nrfx_coredep_delay_us(250);
    nrf_clock_lf_src_set(NRF_CLOCK, NRF_CLOCK_LFCLK_XTAL);
    nrf_clock_task_trigger(NRF_CLOCK, NRF_CLOCK_TASK_LFCLKSTART);
    guard = 1000000;
    while (!nrf_clock_lf_is_running(NRF_CLOCK) && guard--) {
    }
}

void wasp_early_init(void) {
    wasp_start_lfclk();

    // Boot probe: backlight dim (BL_LO=P14 active low) as early as possible.
    // watch.py switches it to bright as its first action, and the normal
    // backlight handling takes over after the display is initialised.
    nrf_gpio_cfg_output(22); nrf_gpio_pin_set(22);   // BL_MID off
    nrf_gpio_cfg_output(23); nrf_gpio_pin_set(23);   // BL_HI off
    nrf_gpio_cfg_output(14); nrf_gpio_pin_clear(14); // BL_LO on

    nrf_gpio_cfg_output(WASP_WDT_BUTTON_EN);
    nrf_gpio_pin_set(WASP_WDT_BUTTON_EN);
    nrf_gpio_cfg_input(WASP_WDT_BUTTON, NRF_GPIO_PIN_NOPULL);

    // Feed straight away: the bootloader may have used up most of the 5
    // seconds already (e.g. drawing the splash screen). From here watch.py's
    // RTC callback, set up as the very first thing it does, takes over.
    wasp_wdt_feed();
}

// --- machine.bootloader() -------------------------------------------------

void wasp_enter_bootloader(void) {
    const uint32_t DFU_MAGIC_OTA_RESET = 0xa8;
    NRF_POWER->GPREGRET = DFU_MAGIC_OTA_RESET;
    NVIC_SystemReset();
}

// --- waspnrf module -------------------------------------------------------

// Without the BLE console these simply report "not connected" so that the
// board glue can be frozen unchanged.
static mp_obj_t waspnrf_uart_connected(void) {
#if MICROPY_PY_BLE_NUS
    return mp_obj_new_bool(ble_uart_connected());
#else
    return mp_const_false;
#endif
}
static MP_DEFINE_CONST_FUN_OBJ_0(waspnrf_uart_connected_obj, waspnrf_uart_connected);

static mp_obj_t waspnrf_uart_enabled(void) {
#if MICROPY_PY_BLE_NUS
    return mp_obj_new_bool(ble_uart_enabled());
#else
    return mp_const_false;
#endif
}
static MP_DEFINE_CONST_FUN_OBJ_0(waspnrf_uart_enabled_obj, waspnrf_uart_enabled);

static mp_obj_t waspnrf_alive(void) {
    wasp_wdt_last_alive = mp_hal_ticks_ms();
    wasp_wdt_armed = true;
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(waspnrf_alive_obj, waspnrf_alive);

static mp_obj_t waspnrf_feed(void) {
    wasp_wdt_feed();
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(waspnrf_feed_obj, waspnrf_feed);

static mp_obj_t waspnrf_enter_ota_dfu(void) {
    wasp_enter_bootloader();
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(waspnrf_enter_ota_dfu_obj, waspnrf_enter_ota_dfu);

static const mp_rom_map_elem_t waspnrf_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_waspnrf) },
    { MP_ROM_QSTR(MP_QSTR_uart_connected), MP_ROM_PTR(&waspnrf_uart_connected_obj) },
    { MP_ROM_QSTR(MP_QSTR_uart_enabled), MP_ROM_PTR(&waspnrf_uart_enabled_obj) },
    { MP_ROM_QSTR(MP_QSTR_enter_ota_dfu), MP_ROM_PTR(&waspnrf_enter_ota_dfu_obj) },
    { MP_ROM_QSTR(MP_QSTR_alive), MP_ROM_PTR(&waspnrf_alive_obj) },
    { MP_ROM_QSTR(MP_QSTR_feed), MP_ROM_PTR(&waspnrf_feed_obj) },
};
static MP_DEFINE_CONST_DICT(waspnrf_module_globals, waspnrf_module_globals_table);

const mp_obj_module_t mp_module_waspnrf = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&waspnrf_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_waspnrf, mp_module_waspnrf);
