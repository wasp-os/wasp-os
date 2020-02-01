import logo
import watch
import time

# Splash screen
watch.display.rleblit(logo.pine64, fg=0xffff)

time.sleep(5)
watch.backlight.set(0)
watch.display.poweroff()
