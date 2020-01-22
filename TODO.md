# TODO

Currently the focus for WASP is both to meet feature parity with a dumb
watch and to have a bootloader and watchdog strategy that is robust enough
to allow a PineTime case to be confidently glued shut.

The TODO list helps keep track on progress towards that goal. It is not
(yet) a place for the wishlist!

## Bootloader

 * [X] Basic board ports (PineTime, DS-D6, 96Boards Nitrogen)
 * [X] OTA application update
 * [ ] OTA bootloader update
 * [X] Enable watchdog before starting the application
 * [ ] Splash screen
  
## Micropython

 * [X] Basic board ports (PineTime, DS-D6, 96Boards Nitrogen)
 * [-] Long press reset (conditional feeding of the watchdog)
   - [X] Feed dog from REPL polling loop
   - [ ] Feed dog from a tick interrupt
 * [ ] Basic (WFI) power saving
 * [ ] Implement machine.RTC for nrf52
 * [ ] Implement machine.ADC for nrf52
 
## WASP

 * [-] Display driver
   - [-] Display initialization
   - [ ] Bitmap blitting
   - [ ] RLE coder and decoder
 * [ ] Backlight driver
 * [ ] Button driver (interrupt based)
 * [ ] Battery/charger driver
 * [ ] Simple clock and battery level application
