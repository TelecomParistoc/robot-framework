# This test shows how it is possible to easily install callbacks on GPIO or other pin events
# On rasp 2, this test uses GPIO 5 (BCM pin_index) which must be in mode "OUT"

import gpio
import time

gpio.init()

pin_index = gpio.gpio_index_of_wpi_pin(5)
print "GPIO 5 corresponds to BCM index "+str(pin_index)

gpio.set_pin_mode(pin_index, gpio.OUTPUT)


def print_something(index, text):
    print "GPIO "+str(index)+" "+text

gpio.assign_callback_on_gpio_down(pin_index, lambda: print_something(pin_index, "down"))

print ""
gpio.digital_write(pin_index, 1)
time.sleep(0.5)
print "Read "+str(gpio.digital_read(pin_index))+" on pin "+str(pin_index)
gpio.digital_write(pin_index, 0)
time.sleep(0.5)
print "Read "+str(gpio.digital_read(pin_index))+" on pin "+str(pin_index)

gpio.assign_callback_on_gpio_change(pin_index, lambda: print_something(pin_index, "changed"))

print ""
gpio.digital_write(pin_index, 1)
time.sleep(0.5)
print "Read "+str(gpio.digital_read(pin_index))+" on pin "+str(pin_index)
gpio.digital_write(pin_index, 0)
time.sleep(0.5)
print "Read "+str(gpio.digital_read(pin_index))+" on pin "+str(pin_index)

gpio.assign_callback_on_gpio_change(pin_index, lambda: print_something(pin_index, "changed (one shot, disappear after beeing triggered)"), True) # the last "True" argument is for one shot callback
gpio.assign_callback_on_gpio_up(pin_index, lambda: print_something(pin_index, "up"))

print ""
gpio.digital_write(pin_index, 1)
time.sleep(0.5)
print "Read "+str(gpio.digital_read(pin_index))+" on pin "+str(pin_index)
gpio.digital_write(pin_index, 0)
time.sleep(0.5)
print "Read "+str(gpio.digital_read(pin_index))+" on pin "+str(pin_index)

gpio.remove_callbacks_on_gpio_change(pin_index)

print ""
gpio.digital_write(pin_index, 1)
time.sleep(0.5)
print "Read "+str(gpio.digital_read(pin_index))+" on pin "+str(pin_index)
gpio.digital_write(pin_index, 0)
time.sleep(0.5)
print "Read "+str(gpio.digital_read(pin_index))+" on pin "+str(pin_index)

gpio.remove_callbacks_on_gpio(pin_index)

print "All callbacks are removed, it should not be printed anything from them now"

print ""
gpio.digital_write(pin_index, 1)
time.sleep(0.5)
print "Read "+str(gpio.digital_read(pin_index))+" on pin "+str(pin_index)
gpio.digital_write(pin_index, 0)
time.sleep(0.5)
print "Read "+str(gpio.digital_read(pin_index))+" on pin "+str(pin_index)
gpio.set_pin_mode(pin_index, gpio.INPUT)

gpio.join() # this is necessary to properly close the callback C thread
