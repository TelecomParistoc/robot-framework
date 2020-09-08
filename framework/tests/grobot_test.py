#!/usr/bin/python

from ..robot.thread_easy_stop import Thread_Easy_Stop
from ..robot.starting_block import add_jack_and_delay, Wait_Object
from ..local_robot.big_robot import *
from I2C_bus import I2C_bus
from AX12 import AX12
import gpio
import random
import time

#TODO AX12 id's have to be completed
#TODO: python 2 to 3
catapult_id = 0
sorting_wheel_id = 0
ball_catcher_id = 0

def catapult_ball():
    catapult.turn()

if __name__ == '__main__':

    print("Jack removed !")

    try:
        I2C_bus.init(115200)
    except Exception as e:
        print "[-] Unable to start I2C communication ("+str(e)+"), exiting"
        exit()

    #scanned = I2C_bus.scan(print_ax12_id_on_the_fly)
    scanned = [130, 141]
    if len(scanned)<2:
        print "[-] Not enough AX12 on I2C bus to achieve the sequence, exiting"
        exit()

    gpio.init()

    jack_pin = gpio.gpio_index_of_wpi_pin(5)
    print "Jack pin corresponds to BCM index "+str(jack_pin)

    #gpio.set_pin_mode(jack_pin, gpio.INPUT)
    gpio.set_pin_mode(jack_pin, gpio.OUTPUT) #easier to test with hand (gpio write 5 0 ou 1)

    robot = init()

    robot.add_object(AX12(catapult_id), "catapult")
    robot.add_object(AX12(sorting_wheel_id), "sorting_wheel")
    robot.add_object(AX12(ball_catcher_id), "ball_catcher")

    manage_jack = add_jack_and_delay(robot, 30)

    gpio.assign_callback_on_gpio_down(24, lambda: manage_jack(False))
    gpio.assign_callback_on_gpio_up(24, lambda: manage_jack(True))

    #program

    robot.stop()
