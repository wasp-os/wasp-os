from machine import RTCounter as RTC

# Start measuring time (and feeding the watchdog)
rtc = RTC(1, mode=RTC.PERIODIC)
rtc.start()
