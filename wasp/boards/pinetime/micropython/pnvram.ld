/* Reserve 32 bytes of RAM immediately after the SoftDevice RAM. wasp-os
 * keeps the RTC offset and uptime there (drivers/nrf_rtc.py) so that the
 * time survives a soft reset or watchdog reset. */
_sd_ram = _sd_ram + 32;
