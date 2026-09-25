// SPDX-License-Identifier: LGPL-3.0-or-later
// Copyright (C) 2020 Daniel Thompson
//
// Small pieces of nRF port glue that wasp-os needs and that used to live in
// the wasp-os fork of MicroPython. Kept here so that an unmodified upstream
// MicroPython can be used.

#include "py/runtime.h"
#include "py/mphal.h"
#include "nrf.h"

#include "nrfx_timer.h"
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
// (see "Watchdog protocol" in docs/wasp.rst). We feed it from a hardware
// timer interrupt, started from MICROPY_BOARD_EARLY_INIT() before any Python
// runs, unless the button is held down. Holding the button therefore resets
// the watch into the bootloader, and a Python exception at boot leaves the
// REPL alive instead of rebooting.

#ifndef WASP_WDT_BUTTON
#define WASP_WDT_BUTTON      (13)   // PineTime: active high
#define WASP_WDT_BUTTON_EN   (15)   // must be driven high to read the button
#endif

static const nrfx_timer_t wasp_wdt_timer = NRFX_TIMER_INSTANCE(4);

// Boot heartbeat (temporary diagnostic): until Python calls
// waspnrf.boot_done() the motor (P16, active low) pulses for one timer tick
// every two seconds. Continuous heartbeat == C start-up never reached Python.
#define WASP_MOTOR (16)
static volatile bool wasp_python_started;
static volatile uint32_t wasp_hb_ticks;

static void wasp_wdt_timer_handler(nrf_timer_event_t event_type, void *p_context) {
    if (!nrf_gpio_pin_read(WASP_WDT_BUTTON)) {
        nrf_wdt_reload_request_set(NRF_WDT, NRF_WDT_RR0);
    }
    if (!wasp_python_started) {
        wasp_hb_ticks++;
        if ((wasp_hb_ticks % 8) == 0) {
            nrf_gpio_pin_clear(WASP_MOTOR);   // on
        } else {
            nrf_gpio_pin_set(WASP_MOTOR);     // off
        }
    }
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
    nrf_gpio_cfg_output(WASP_MOTOR); nrf_gpio_pin_set(WASP_MOTOR); // motor off
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

    nrfx_timer_config_t config = {
        .frequency = 1000000,
        .mode = NRF_TIMER_MODE_TIMER,
        .bit_width = NRF_TIMER_BIT_WIDTH_32,
        .interrupt_priority = 6, // SoftDevice compatible
        .p_context = NULL,
    };
    nrfx_timer_init(&wasp_wdt_timer, &config, wasp_wdt_timer_handler);
    nrfx_timer_extended_compare(&wasp_wdt_timer, NRF_TIMER_CC_CHANNEL0,
        nrfx_timer_ms_to_ticks(&wasp_wdt_timer, 250),
        NRF_TIMER_SHORT_COMPARE0_CLEAR_MASK, true);
    nrfx_timer_enable(&wasp_wdt_timer);

    // First feed straight away: the bootloader may have used up most of the
    // 5 seconds already (e.g. drawing the splash screen).
    nrf_wdt_reload_request_set(NRF_WDT, NRF_WDT_RR0);
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

static mp_obj_t waspnrf_boot_done(void) {
    wasp_python_started = true;
    nrf_gpio_pin_set(WASP_MOTOR);
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(waspnrf_boot_done_obj, waspnrf_boot_done);

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
    { MP_ROM_QSTR(MP_QSTR_boot_done), MP_ROM_PTR(&waspnrf_boot_done_obj) },
};
static MP_DEFINE_CONST_DICT(waspnrf_module_globals, waspnrf_module_globals_table);

const mp_obj_module_t mp_module_waspnrf = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&waspnrf_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_waspnrf, mp_module_waspnrf);
